import pickle
import random
import re
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from helpers import NoneMessage


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


class DBBenchChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for DBBench
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            sql_block = re.search(r"```sql(.*?)```", self.agents[example_index][-1], re.DOTALL)
            if sql_block:
                sql_code = sql_block.group(1).strip()
            else:
                sql_code = ""
            self.environments[example_index].append(HumanMessage(content=sql_code)) 
        else:
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]
    
    def _process_task_environment(self, data):
        return (data.split("There are 2 tables involved with this task.")[0], data.split("There are 2 tables involved with this task.")[1])
    
    def _get_sql_code(self, message):
        sql_block = re.search(r"```sql(.*?)```", message, re.DOTALL)
        if sql_block:
            sql_code = sql_block.group(1).strip()
        else:
            sql_code = ""  
        print( f'SQL code found: [{sql_code}]')
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

        if conversation_side == "agent" and message_index == 9: # 1
            step = 1
        if conversation_side == "agent" and message_index == 11: # 3
            step = 2
        if conversation_side == "environment" and message_index == 9:
            step = 5
        if conversation_side == "agent" and message_index > 11: # 3 
            step = 4
        if conversation_side == "environment" and message_index >= 9: # 4
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            first_response = self.agents[example_index][9].content
            sql_code = self._get_sql_code(first_response)
            # task_, environment_info = self._process_task_environment(self.agents[example_index][2].content)
            task_and_envinfo = self.agents[example_index][8].content
            tables_ = self.creator_model.predict_messages(db_chat3 + [HumanMessage(content=task_and_envinfo)]).content
            environment_prompt = db_environment_prompt_template.format(tables_, task_and_envinfo, sql_code)
            self.environments[example_index] = db_chat2 + [HumanMessage(content=""), AIMessage(content="")] + [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
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
                sql_code = self._get_sql_code(agent_response.content)
                self.agents[example_index].append(agent_response)
                if "Final Answer:" in agent_response.content or sql_code == "":
                    break
                self.environments[example_index].append(HumanMessage(content=sql_code))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def play_start2end(self, task, num_turns):
        # agent_messages = db_chat1[:2] + [HumanMessage(content=task)]
        agent_messages = db_chat1 + [HumanMessage(content=f"Now, I will start a new problem in a new Database. My problem is: {task}.")]
        agent_response = self.agent_model.predict_messages(agent_messages)
        CORRECT_FLAG, i = True, 0
        while 'Action: Operation\n```sql' not in agent_response.content: 
            agent_response = self.agent_model.predict_messages(agent_messages)
            i += 1
            if i == 5: break
        if 'Action: Operation\n```sql' not in agent_response.content:
            CORRECT_FLAG = False
        print("AGENT: ", agent_response.content)
        agent_messages.append(agent_response)
        tables_ = self.creator_model.predict_messages(db_chat3 + [HumanMessage(content=task)]).content
        sql_code = self._get_sql_code(agent_response.content)
        environment_prompt = db_environment_prompt_template.format(tables_, task, sql_code)
        environment_messages = db_chat2 + [HumanMessage(content=environment_prompt)]
        environment_result = self.environment_model.predict_messages(environment_messages)
        environment_messages.append(environment_result)
        agent_messages.append(HumanMessage(content=environment_result.content))
        print("ENVIRONMENT: ", environment_result.content)
        for i in range(num_turns):
            agent_response = self.agent_model.predict_messages(agent_messages)
            i = 0
            while 'Action: Operation\n```sql' not in agent_response.content and 'Action: Answer\nFinal Answer: ["' not in agent_response.content:
                agent_response = self.agent_model.predict_messages(agent_messages)
                i += 1
                if i==5: break
            if 'Action: Operation\n```sql' not in agent_response.content and 'Action: Answer\nFinal Answer: ["' not in agent_response.content:
                CORRECT_FLAG = False
            print("AGENT: ", agent_response.content)
            sql_code = self._get_sql_code(agent_response.content)
            agent_messages.append(agent_response)
            if "Final Answer:" in agent_response.content:
                break
            environment_messages.append(HumanMessage(content=sql_code))
            environment_result = self.environment_model.predict_messages(environment_messages)
            environment_messages.append(environment_result)
            print("ENVIRONMENT: ", environment_result.content)
            agent_messages.append(HumanMessage(content=environment_result.content))
        
        return agent_messages, environment_messages, 1 if CORRECT_FLAG else 0 



class OSChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
        self.agents = None
        self.environments = None
        self.offset = 1
    
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            bash_block = re.search(r"```bash\n(.*?)\n```", self.agents[example_index][-1], re.DOTALL)
            if bash_block:
                bash_code = f"Bash Command:```bash\n{bash_block.group(1).strip()}\n```"
            else:
                bash_code = ""
            self.environments[example_index].append(HumanMessage(content=bash_code)) 
        else:
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]

    def _process_task_environment(self, data):
        return (data.split("There are 2 tables involved with this task.")[0], data.split("There are 2 tables involved with this task.")[1])

    def _get_bash_code(self, message):
        bash_block = re.search(r"```bash\n(.*?)\n```", message, re.DOTALL)
        if bash_block:
            bash_code = bash_block.group(1).strip()
        else:
            bash_code = ""  
        print( f'bash code found: {bash_code}')
        return bash_code

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

        if conversation_side == "agent" and message_index == 7: # 1
            step = 1
        if conversation_side == "agent" and message_index == 9: # 3
            step = 2
        if conversation_side == "environment" and message_index == 7: # 4
            step = 5
        if conversation_side == "agent" and message_index > 9:
            step = 4
        if conversation_side == "environment" and message_index >= 7: # 4
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            first_response = self.agents[example_index][7].content
            bash_code = self._get_bash_code(first_response)
            # task_, environment_info = self._process_task_environment(self.agents[example_index][2].content)
            # The above code is a comment in Python. It is not doing anything in terms of code
            # execution. It is used to provide information or explanations about the code to other
            # developers or to remind oneself about the code's purpose.
            task = self.agents[example_index][6].content.replace("Now, I will start a new problem in a new OS. My problem is:", "").strip()
            init_bash_command = self._get_bash_code(self.creator_model.predict_messages(os_chat3 + [HumanMessage(content=f"Task: {task}")]).content)
            environment_prompt = os_environment_prompt_template.format(task, init_bash_command, bash_code)
            
            # put empty strings to even the left and right side of the conversation when displayed, i.e., agent and environment sides
            self.environments[example_index] = os_chat2 + [HumanMessage(content=""), AIMessage(content="")] + [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))
            print(environment_result.content + "\n")
        
        skip_once = False
        if step == 4:
            skip_once = True
            if self.environments[example_index][-1].type == "ai":
                bash_code = self._get_bash_code(self.agents[example_index][-1].content)
                self.environments[example_index].append(HumanMessage(content=f"Bash Command:\n```bash\n{bash_code}\n```"))
                print(self.environments[example_index][-1])

        num_turns = 10 
        for i in range(num_turns):
            if not skip_once:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                print(agent_response.content)
                bash_code = self._get_bash_code(agent_response.content)
                self.agents[example_index].append(agent_response)
                if "finish" in agent_response.content or "answer(" in agent_response.content or bash_code == "":
                    break
                self.environments[example_index].append(HumanMessage(content=f"Bash Command:\n```bash\n{bash_code}\n```"))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def play_start2end(self, task, num_turns):
        agent_messages = os_chat1 + [HumanMessage(content=task)]
        agent_response = self.agent_model.predict_messages(agent_messages)
        print("AGENT: ", agent_response.content)
        bash_code = self._get_bash_code(agent_response.content)
        agent_messages.append(agent_response)
        task = task.replace("Now, I will start a new problem in a new OS. My problem is:", "").strip()
        init_bash_command = self._get_bash_code(self.creator_model.predict_messages(os_chat3 + [HumanMessage(content=f"Task: {task}")]).content)
        environment_prompt = os_environment_prompt_template.format(task, init_bash_command, bash_code)
        environment_messages = os_chat2 + [HumanMessage(content=# The above code is a prompt for the
        # user to enter a question or request
        # related to Python programming.
        environment_prompt)]
        environment_result = self.environment_model.predict_messages(environment_messages)
        environment_messages.append(environment_result)
        agent_messages.append(HumanMessage(content=environment_result.content))
        print("ENVIRONMENT: ", environment_result.content)
        for i in range(num_turns):
            agent_response = self.agent_model.predict_messages(agent_messages)
            print("AGENT: ", agent_response.content)
            bash_code = self._get_bash_code(agent_response.content)
            environment_messages.append(HumanMessage(content=f"Bash Command:\n```bash\n{bash_code}\n```"))
            agent_messages.append(agent_response)
            if "finish" in agent_response.content or "answer(" in agent_response.content or bash_code == "":
                break
            environment_result = self.environment_model.predict_messages(environment_messages)
            environment_messages.append(environment_result)
            print("ENVIRONMENT: ", environment_result.content)
            agent_messages.append(HumanMessage(content=environment_result.content))
            
        return agent_messages, environment_messages            


class AlfChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
        self.agents = None
        self.environments = None
        self.offset = 2
    
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1])) 
        else:
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]

    # def _process_task_environment(self, data):
    #     return (data.split("There are 2 tables involved with this task.")[0], data.split("There are 2 tables involved with this task.")[1])

    # def _get_bash_code(self, message):
    #     bash_block = re.search(r"```bash\n(.*?)\n```", message, re.DOTALL)
    #     if bash_block:
    #         bash_code = bash_block.group(1).strip()
    #     else:
    #         bash_code = ""  
    #     print( f'bash code found: {bash_code}')
    #     return bash_code

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

        if conversation_side == "agent" and message_index == 22: # 1
            step = 1
        if conversation_side == "agent" and message_index == 24: # 3
            step = 2
        if conversation_side == "environment" and message_index == 23: 
            step = 5
        if conversation_side == "agent" and message_index > 24:
            step = 4
        if conversation_side == "environment" and message_index >= 23:
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            # The above code is a comment in Python. It is not doing anything in terms of code
            # execution. It is used to provide information or explanations about the code to other
            # developers or to remind oneself about the code's purpose.
            
            task = self.agents[example_index][23].content.replace("Now here is your new task.", "").strip()
            init_state = self.creator_model.predict_messages(alf_chat3 + [HumanMessage(content=f"Now here is a new task: {task}")]).content.replace("Initial State:", "").strip()
            environment_prompt = alf_environment_prompt_template.format(init_state, task, self.agents[example_index][-1].content)
            
            # put empty strings to even the left and right side of the conversation when displayed, i.e., agent and environment sides
            self.environments[example_index] = alf_chat2 + [HumanMessage(content=""), AIMessage(content="")] + [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
            print(environment_result.content + "\n")
        
        skip_once = False
        if step == 4:
            skip_once = True
            if self.environments[example_index][-1].type == "ai":
                self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1].content))
                print(self.environments[example_index][-1])

        num_turns = 15 
        for i in range(num_turns):
            if not skip_once:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                print(agent_response.content)
                self.agents[example_index].append(agent_response)
                self.environments[example_index].append(HumanMessage(content=agent_response.content))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            if "success" in environment_result.content:
                break
            self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))

    def play_start2end(self, task, num_turns):
        agent_messages = alf_chat1 + [HumanMessage(content=task)]
        agent_response = self.agent_model.predict_messages(agent_messages)
        print("AGENT: ", agent_response.content)
        agent_messages.append(agent_response)
        task = task.replace("Here is your new task.", "").strip()
        init_state = self.creator_model.predict_messages(alf_chat3 + [HumanMessage(content=f"Now here is a new task: {task}")]).content.replace("Initial State:", "").strip()
        environment_prompt = alf_environment_prompt_template.format(init_state, task, agent_response.content)
        environment_messages = alf_chat2 + [HumanMessage(content=environment_prompt)]
        environment_result = self.environment_model.predict_messages(environment_messages)
        environment_messages.append(environment_result)
        agent_messages.append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
        print("ENVIRONMENT: ", environment_result.content)
        for i in range(num_turns):
            agent_response = self.agent_model.predict_messages(agent_messages)
            print("AGENT: ", agent_response.content)
            environment_messages.append(HumanMessage(content=agent_response.content))
            agent_messages.append(agent_response)
            environment_result = self.environment_model.predict_messages(environment_messages)
            environment_messages.append(environment_result)
            print("ENVIRONMENT: ", environment_result.content)            
            if "success" in environment_result.content:
                break
            agent_messages.append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
            
        return agent_messages, environment_messages            
    
    
class KGChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1])) 
        else:
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]

    # def _process_task_environment(self, data):
    #     return (data.split("There are 2 tables involved with this task.")[0], data.split("There are 2 tables involved with this task.")[1])

    # def _get_bash_code(self, message):
    #     bash_block = re.search(r"```bash\n(.*?)\n```", message, re.DOTALL)
    #     if bash_block:
    #         bash_code = bash_block.group(1).strip()
    #     else:
    #         bash_code = ""  
    #     print( f'bash code found: {bash_code}')
    #     return bash_code

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

        if conversation_side == "agent" and message_index == 17: # 1
            step = 1
        if conversation_side == "agent" and message_index == 19: # 3
            step = 2
        if conversation_side == "environment" and message_index == 18: 
            step = 5
        if conversation_side == "agent" and message_index > 19:
            step = 4
        if conversation_side == "environment" and message_index >= 18:
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            # The above code is a comment in Python. It is not doing anything in terms of code
            # execution. It is used to provide information or explanations about the code to other
            # developers or to remind oneself about the code's purpose.
            
            task = self.agents[example_index][18].content
            complexity = random.choices([1, 2, 3], weights=[0.25, 0.25, 0.5], k=1)[0]
            kg_chat3[1].content = kg_chat3[1].content.format(task, complexity)
            init_state = re.findall(r"relation_map = dict\((.*?)\)", self.creator_model.predict_messages(kg_chat3).content, re.DOTALL)[0]
            print("**init_state** =", init_state)
            environment_prompt = kg_environment_prompt_template.format(init_state, task.replace("A new question:", "").strip(), self.agents[example_index][-1].content)
            
            # put empty strings to even the left and right side of the conversation when displayed, i.e., agent and environment sides
            self.environments[example_index] = kg_chat2 + [HumanMessage(content=""), AIMessage(content="")] + [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))
            print(environment_result.content + "\n")
        
        skip_once = False
        if step == 4:
            skip_once = True
            if self.environments[example_index][-1].type == "ai":
                self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1].content))
                print(self.environments[example_index][-1])

        num_turns = 15
        for i in range(num_turns):
            if not skip_once:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                print(agent_response.content)
                self.agents[example_index].append(agent_response)
                if "Final Answer:" in agent_response.content:
                    break
                self.environments[example_index].append(HumanMessage(content=agent_response.content))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def play_start2end(self, task, num_turns):
        agent_messages = kg_chat1 + [HumanMessage(content=task)]
        agent_response = self.agent_model.predict_messages(agent_messages)
        print("AGENT: ", agent_response.content)
        agent_messages.append(agent_response)
        task = task.replace("Here is your new task.", "").strip()
        init_state = self.creator_model.predict_messages(alf_chat3 + [HumanMessage(content=f"Now here is a new task: {task}")]).content.replace("Initial State:", "").strip()
        environment_prompt = alf_environment_prompt_template.format(init_state, task, agent_response.content)
        environment_messages = alf_chat2 + [HumanMessage(content=environment_prompt)]
        environment_result = self.environment_model.predict_messages(environment_messages)
        environment_messages.append(environment_result)
        agent_messages.append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
        print("ENVIRONMENT: ", environment_result.content)
        for i in range(num_turns):
            agent_response = self.agent_model.predict_messages(agent_messages)
            print("AGENT: ", agent_response.content)
            environment_messages.append(HumanMessage(content=agent_response.content))
            agent_messages.append(agent_response)
            environment_result = self.environment_model.predict_messages(environment_messages)
            environment_messages.append(environment_result)
            print("ENVIRONMENT: ", environment_result.content)            
            if "Final Answer:" in environment_result.content:
                break
            agent_messages.append(HumanMessage(content=environment_result.content))
            
        return agent_messages, environment_messages    
    

class M2WChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
        self.agents = None
        self.environments = None
        self.offset = 1
    
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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
            self.agents[example_index][-1].content = self.creator_model.predict_messages(m2w_chat3 + [self.agents[example_index][-1]]).content + \
                "\n\n" + self.agents[example_index][-1].content
            self.environments[example_index][-1].content = str(self.agents[example_index][-1].content)
            agent_response = self.agent_model.predict_messages(self.agents[example_index])
            self.agents[example_index].append(agent_response)
            print(agent_response.content + "\n")

    # def add_to_environment(self, example_index):
    #     if self.environments[example_index][-1].type == "ai":
    #         self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1])) 
    #     else:
    #         environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
    #         self.environments[example_index].append(environment_result)
    #         print(environment_result.content)
    #         self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]

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

        if conversation_side == "agent" and message_index == 1: # 1
            step = 1

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step == 1:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")

    def play_start2end(self, task, num_turns):
        agent_messages = m2w_chat1 + [HumanMessage(content=task)]
        agent_messages[-1].content = self.creator_model.predict_messages(m2w_chat3 + [agent_messages[-1]]).content + \
            "\n\n" + agent_messages[-1].content
        agent_response = self.agent_model.predict_messages(agent_messages)
        agent_messages.append(agent_response)
        print(agent_response.content + "\n")        
        return agent_messages, [""]    
    
        
class WSChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
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
        if message_index >= len(self.agents[example_index]):
            return NoneMessage()
        return self.agents[example_index][message_index]

    def update_agent_side(self, example_index, message_index, content):
        self.agents[example_index][message_index].content = content

    def get_environment_side(self, example_index, message_index):
        mapped_index = self._ext_to_int_index(message_index)
        if mapped_index < 0 or mapped_index >= len(self.environments[example_index]):
            return NoneMessage()
        return self.environments[example_index][mapped_index]

    def update_environment_side(self, example_index, message_index, content):
        mapped_index = self._ext_to_int_index(message_index)
        self.environments[example_index][mapped_index].content = content

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

    def add_to_environment(self, example_index):
        if self.environments[example_index][-1].type == "ai":
            self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1])) 
        else:
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))

    def refresh_at_index(self, example_index, conversation_side, message_index):
        # print(f"Modifying Index {index}")
        if conversation_side == "agent":
            result = self.agent_model.predict_messages(self.agents[example_index][:message_index])
            if result.content != "":
                self.agents[example_index][message_index] = result
            print(self.agents[example_index][message_index])
            
        else:
            mapped_index = self._ext_to_int_index(message_index)
            result = self.environment_model.predict_messages([msg for msg in self.environments[example_index][:mapped_index] if msg.content!=""])
            if result.content != "":
                self.environments[example_index][mapped_index] = result
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
            del self.agents[example_index][message_index:]

    # def _process_task_environment(self, data):
    #     return (data.split("There are 2 tables involved with this task.")[0], data.split("There are 2 tables involved with this task.")[1])

    # def _get_bash_code(self, message):
    #     bash_block = re.search(r"```bash\n(.*?)\n```", message, re.DOTALL)
    #     if bash_block:
    #         bash_code = bash_block.group(1).strip()
    #     else:
    #         bash_code = ""  
    #     print( f'bash code found: {bash_code}')
    #     return bash_code

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

        if conversation_side == "agent" and message_index == 17: # 1
            step = 1
        if conversation_side == "agent" and message_index == 19: # 3
            step = 2
        if conversation_side == "environment" and message_index == 18: 
            step = 5
        if conversation_side == "agent" and message_index > 19:
            step = 4
        if conversation_side == "environment" and message_index >= 18:
            step = 5

        print(f"\nIndex: {message_index} Determined Step: {step}")

        if step < 3:
            if  self.agents[example_index][-1].type == "HumanMessage":
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")
        if step < 4:
            # The above code is a comment in Python. It is not doing anything in terms of code
            # execution. It is used to provide information or explanations about the code to other
            # developers or to remind oneself about the code's purpose.
            
            task = self.agents[example_index][18].content
            complexity = random.choices([1, 2, 3], weights=[0.25, 0.25, 0.5], k=1)[0]
            kg_chat3[1].content = kg_chat3[1].content.format(task, complexity)
            init_state = re.findall(r"relation_map = dict\((.*?)\)", self.creator_model.predict_messages(kg_chat3).content, re.DOTALL)[0]
            print("**init_state** =", init_state)
            environment_prompt = kg_environment_prompt_template.format(init_state, task.replace("A new question:", "").strip(), self.agents[example_index][-1].content)
            
            # put empty strings to even the left and right side of the conversation when displayed, i.e., agent and environment sides
            self.environments[example_index] = kg_chat2 + [HumanMessage(content=""), AIMessage(content="")] + [
                HumanMessage(content=environment_prompt)
            ]
            print(environment_prompt)
            
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))
            print(environment_result.content + "\n")
        
        skip_once = False
        if step == 4:
            skip_once = True
            if self.environments[example_index][-1].type == "ai":
                self.environments[example_index].append(HumanMessage(content=self.agents[example_index][-1].content))
                print(self.environments[example_index][-1])

        num_turns = 15
        for i in range(num_turns):
            if not skip_once:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                print(agent_response.content)
                self.agents[example_index].append(agent_response)
                if "Final Answer:" in agent_response.content:
                    break
                self.environments[example_index].append(HumanMessage(content=agent_response.content))
            else:
                skip_once = False
            environment_result = self.environment_model.predict_messages([msg for msg in self.environments[example_index] if msg.content!=""])
            self.environments[example_index].append(environment_result)
            print(environment_result.content)
            self.agents[example_index].append(HumanMessage(content=environment_result.content))

    def play_start2end(self, task, num_turns):
        agent_messages = kg_chat1 + [HumanMessage(content=task)]
        agent_response = self.agent_model.predict_messages(agent_messages)
        print("AGENT: ", agent_response.content)
        agent_messages.append(agent_response)
        task = task.replace("Here is your new task.", "").strip()
        init_state = self.creator_model.predict_messages(alf_chat3 + [HumanMessage(content=f"Now here is a new task: {task}")]).content.replace("Initial State:", "").strip()
        environment_prompt = alf_environment_prompt_template.format(init_state, task, agent_response.content)
        environment_messages = alf_chat2 + [HumanMessage(content=environment_prompt)]
        environment_result = self.environment_model.predict_messages(environment_messages)
        environment_messages.append(environment_result)
        agent_messages.append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
        print("ENVIRONMENT: ", environment_result.content)
        for i in range(num_turns):
            agent_response = self.agent_model.predict_messages(agent_messages)
            print("AGENT: ", agent_response.content)
            environment_messages.append(HumanMessage(content=agent_response.content))
            agent_messages.append(agent_response)
            environment_result = self.environment_model.predict_messages(environment_messages)
            environment_messages.append(environment_result)
            print("ENVIRONMENT: ", environment_result.content)            
            if "Final Answer:" in environment_result.content:
                break
            agent_messages.append(HumanMessage(content=environment_result.content))
            
        return agent_messages, environment_messages    