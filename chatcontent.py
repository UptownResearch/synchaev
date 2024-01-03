import pickle
from helpers import NoneMessage
import re
from langchain.schema import HumanMessage, AIMessage, SystemMessage

class ChatContent:
    def __init__(self):
        # Constructor for initializing the ChatContent class
        pass

    def max_chat_length(self):
        # Returns the length of the longer chat (agent or environment)
        pass

    def get_agent_side(self, example_index, message_index):
        # Retrieves agent chat content at the specified message index
        pass

    def update_agent_side(self, example_index, message_index, content):
        # Updates the agent chat content at the specified message index
        pass

    def get_environment_side(self, example_index, message_index):
        # Retrieves environment chat content at the specified message index
        pass

    def update_environment_side(self, example_index, message_index, content):
        # Updates the environment chat content at the specified message index
        pass

    def delete_example(self, example_index):
        # Deletes the chat content at the specified example index
        pass

    def load(self, filecontent):
        # Loads chat content examples from filecontent dictionary
        pass

    def write(self, filename):
        # Writes chat examples to a file
        pass

    def num_examples(self,  example_index):
        # Returns the number of chat content examples
        pass

    def add_to_agent(self,  example_index):
        # Adds a message to the agent conversation
        pass

    def add_to_environment(self):
        # Adds a message to the environment conversation
        pass

    def replay_from_index(self, example_index, conversation_side, message_index):
        # Recreates both conversations starting from the given side and index
        pass

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # Creates new content at index in the specified conversation
        pass

    def delete_at_index(self, example_index, conversation_side, message_index):
        # Deletes all conversation starting at index on the specified side
        pass

mysql_agent_prompt_improved = '''I will ask you a question, then you should help me operate a MySQL database with SQL to answer the question. 
You have to explain the problem and your solution to me and write down your thoughts. After thinking and explaining 
thoroughly, every round you can choose to operate or to answer. your operation should be like this: 
Action: Operation ```sql SELECT * FROM table WHERE condition; ``` You MUST put SQL in markdown format 
without any other comments. Your SQL should be in one line. Every time you can only execute one SQL statement. 
I will only execute the statement in the first SQL code block. Every time you write a SQL, I will execute it for you 
and give you the output. If the output is zero, or empty, you should always double check that you haven't made a mistake before submitting a final answer.
You can double check by removing limitations from your previous SQL statement until you get non-zero or non-empty results.
If you are done operating, and you want to commit your final answer, then write down: 
Action: Answer Final Answer: ["ANSWER1", "ANSWER2", ...] DO NOT write this pattern unless you are sure about your 
answer. You must ALWAYS provide SQL or a Final Answer. I expect an accurate and correct answer. Your answer should be accurate. 
Your answer must be exactly the same as the correct answer. If the question is about modifying the database, then after you are done with operation, 
your answer field can be anything. If your response cannot match any pattern I mentioned earlier, 
you will be judged as FAIL immediately. Your input will be raw MySQL response, you have to deal with it by yourself.'''


environment_prompt_template = '''Pretend you are a MySQL database, responding to SQL statements from an agent. Provide realistic MySQL outputs for SELECT, INSERT, UPDATE, and DELETE operations, maintaining the state of the simulated database accordingly.  The user is expecting answers like those that would be received when using  mysql-connector-python. Reflect changes in subsequent outputs, and confirm operations with typical MySQL success messages. The initial state of the database is described below

Initial Database state:
{}

First command:
{}

The user is working on the following task. The Database may include state that helps the user complete the task:
{}

Please only respond in rawMySQL format (with no extra formatting or commentary) for a user of  mysql-connector-python, for example, if the result is 59.555, the result would be presented as [('59.555',)]. After responding, end your response.
'''

class DBBenchChatContent(ChatContent):
    def __init__(self, agent_model, environment_model):
        # Initialize with additional properties for DBBench
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.agents = None
        self.environments = None
        self.offset = 3
    
    def _ext_to_int_index(self, external_index):
        return external_index - self.offset
    
    def load(self, filecontent):
        # Loads chat content examples from filecontent dictionary
        self.agents = filecontent["agents"]
        self.environments = filecontent["environments"]

    def max_chat_length(self, example_index):
        # Returns the length of the longer chat (agent or environment)
        return max(len(self.agents[example_index]), len(self.environments[example_index])+self.offset)

    def get_agent_side(self, example_index, message_index):
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index] = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index] = content

    def delete_example(self, example_index):
        del self.agents[example_index]
        del self.environments[example_index]

    def write(self, filename):
        output = {
            "agents": self.agents,
            "environments": self.environments
        }
        # Saving data to the specified pickle file
        with open(filename, 'wb') as file:
            pickle.dump(output, file)

    def num_examples(self):
        return len(self.agents)

    def add_to_agent(self, example_index):
        if self.agents[example_index][-1].type == "ai":
            return
        else:
            agent_response = self.agent_model.predict_messages(self.agents[example_index])
            self.agents[example_index].append(agent_response)
            print(agent_response.content + "\n")
            sql_block = re.search(r"```sql(.*?)```", agent_response.content, re.DOTALL)
            if sql_block:
                sql_code = sql_block.group(1).strip()
            else:
                sql_code = ""
            if not "Final Answer:" in agent_response.content:
                self.environments[example_index].append(HumanMessage(content=sql_code))     

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            return
        else:
            environment_result = self.environment_model.predict_messages(self.environments[example_index])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            self.agents[example_index][message_index] = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            self.environments[example_index][mapped_index]  = self.environment_model.predict_messages(self.environments[example_index][:mapped_index])
            print(self.environments[example_index][mapped_index])

    def delete_at_index(self, example_index, conversation_side, message_index):
        if conversation_side == 'agent':
            del self.agents[example_index][message_index:] 
            if message_index <= self.offset:
                del self.environments[example_index]
            if message_index > self.offset:
                mapped_index = self._ext_to_int_index(message_index)
                del self.environments[example_index][mapped_index:]
        else:
            print("Delete clicked in Environment")
            mapped_index = self._ext_to_int_index(message_index)
            del self.environments[example_index][mapped_index:]
            del self.agents[example_index][message_index+1:]
    
    def _process_task_environment(self, data):
        return (data.split("..")[0], '\n'.join(data.split("..")[1:]))
    
    def _get_sql_code(self, message):
        sql_block = re.search(r"```sql(.*?)```", message, re.DOTALL)
        if sql_block:
            sql_code = sql_block.group(1).strip()
        else:
            sql_code = ""  
        return sql_code

    def replay_from_index(self, example_index, conversation_side, message_index):
        print("\nplay_from_point\n\n")
        step = 0
        # first, delete conversation after current location
        if conversation_side == "agent": 
            # possible values of index = [1,3, 5...]
            delete_from = max(3, message_index)
            print(f" Deleting {self.agents[example_index][delete_from+1:]}\n\n")
            del self.agents[example_index][delete_from+1:]
            if message_index <= 3: 
                print(f" Deleting all environment messages.\n\n")
                self.environments[example_index] = []
            else:
                start = self.offset - 1
                print(f" Deleting {self.environments[example_index][message_index - start:]}\n\n")
                del self.environments[example_index][ message_index- start:]
        else:
            # possible values of index = [1, 3, ...]
            start = self.offset - 1
            print(f" Deleting {self.environments[example_index][message_index - start:]}\n\n")
            print(f" Deleting {self.agents[example_index][message_index:]}\n\n")
                    
            del self.environments[example_index][message_index - start:]
            del self.agents[example_index][message_index:]

            # replace last agent message
            message = self.environments[example_index][-1].content
            self.agents[example_index].append(HumanMessage(content = message))

        if conversation_side == "agent" and message_index == 1:
            step = 1
        if conversation_side == "agent" and message_index == 3:
            step = 2
        if conversation_side == "environment" and message_index == 4:
            step = 5
        if conversation_side == "agent" and message_index > 3:
            step = 4
        if conversation_side == "environment" and message_index >= 4:
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            first_response = self.agents[example_index][3].content
            sql_code = self._get_sql_code(first_response)
            task_, environment_info = self._process_task_environment(self.agents[example_index][2].content)
            environment_prompt = environment_prompt_template.format(environment_info, sql_code, task_)
            self.environments[example_index] = [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            environment_result = self.environment_model.predict_messages(self.environments[example_index])
            self.environments[example_index].append(environment_result)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))
            print(environment_result.content + "\n")
        
        skip_once = False
        if step == 4:
            skip_once = True
            if self.environments[example_index][-1].type == "ai":
                sql_code = self._get_sql_code(self.agents[example_index][-1].content)
                self.environments[example_index].append(HumanMessage(content=sql_code))
                print(self.environments[example_index][-1])

        num_turns = 10 
        for i in range(num_turns):
            if not skip_once:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                print(agent_response.content)
                sql_code = self._get_sql_code(self.agents[example_index][-1].content)
                self.agents[example_index].append(agent_response)
                if "Final Answer:" in agent_response.content:
                    break
                self.environments[example_index].append(HumanMessage(content=sql_code))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages(self.environments[example_index])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

