import pickle
import random
import re
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from chatcontents.base import ChatContent
from synchaev.helpers import NoneMessage
from synchaev.prompts import m2w_chat1, m2w_chat2, m2w_chat3, m2w_environment_prompt_template


class M2WChatContent(ChatContent):
    def __init__(self, agent_model, environment_model, creator_model):
        # Initialize with additional properties for OS
        super().__init__()
        self.agent_model = agent_model
        self.environment_model = environment_model
        self.creator_model = creator_model
        self.agents = None
        self.environments = None
        self.offset = 0
    
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
            
            # Resampling
            j, agent_response = 5, self.agent_model.predict_messages(self.agents[example_index])
            while "Thought: " not in agent_response.content or "\nAnswer: " not in agent_response.content:
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                j += 1
                if j == 5: break
            print("agent_response.content =", agent_response.content)
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
            # Resampling
            j, result = 5, self.agent_model.predict_messages(self.agents[example_index][:message_index])
            while "Thought: " not in result.content or "\nAnswer: " not in result.content:
                result = self.agent_model.predict_messages(self.agents[example_index])
                j += 1
                if j == 5: break

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
                # Resampling
                j, agent_response = 5, self.agent_model.predict_messages(self.agents[example_index])
                while "Thought: " not in agent_response.content or "\nAnswer: " not in agent_response.content:
                    agent_response = self.agent_model.predict_messages(self.agents[example_index])
                    j += 1
                    if j == 5: break   
                            
                agent_response = self.agent_model.predict_messages(self.agents[example_index])
                self.agents[example_index].append(agent_response)
                print(agent_response.content + "\n")

    def play_start2end(self, task, num_turns):
        agent_messages = m2w_chat1 + [HumanMessage(content=task)]
        agent_messages[-1].content = self.creator_model.predict_messages(m2w_chat3 + [agent_messages[-1]]).content + \
            "\n\n" + agent_messages[-1].content
        # Resampling
        j, agent_response = 5, self.agent_model.predict_messages(agent_messages)
        while "Thought: " not in agent_response.content or ".\nAnswer: " not in agent_response.content:
            agent_response = self.agent_model.predict_messages(agent_messages)
            j += 1
            if j == 5: break
        agent_messages.append(agent_response)
        print(agent_response.content + "\n")        
        return agent_messages, [""]    
