import pickle
import random
import re
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from chatcontents.base import ChatContent
from synchaev.helpers import NoneMessage
from synchaev.prompts import alf_chat1, alf_chat2, alf_chat3, alf_environment_prompt_template


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

        num_turns = 25 
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
            print("environment_result.content =", environment_result.content)
            agent_messages.append(HumanMessage(content=environment_result.content.split('Output: ')[1].strip()))
            
        return agent_messages, environment_messages            
