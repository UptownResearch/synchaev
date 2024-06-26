import pickle
import random
import re
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from chatcontents.base import ChatContent
from synchaev.helpers import NoneMessage
from synchaev.prompts import db_chat1, db_chat2, db_chat3, db_environment_prompt_template


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
