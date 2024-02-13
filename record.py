from tqdm.auto import tqdm
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import read_pickle, save_json, model, environment_model, creator_model
import os
from dotenv import load_dotenv
from chatcontent import DBBenchChatContent, OSChatContent

load_dotenv() 
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

    
def main(agentbench_split):
    if agentbench_split == "dbbench":
        cc = DBBenchChatContent(model, environment_model, creator_model)
    elif agentbench_split == "os":
        cc = OSChatContent(model, environment_model, creator_model)
    else:
        NotImplementedError
    tasks = read_pickle(f"./data/{agentbench_split}/{agentbench_split}_tasks-agentinstruct.pickle")

    all_conversations, num_correct = [], 0
    for i, task in tqdm(enumerate(tasks)):
        if isinstance(cc, DBBenchChatContent):
            _dict = {"conversations": [], "id": f"db_{i}"}
            agent_messages, _, correct_count = cc.play_start2end(task, 10)
            num_correct += correct_count
            print(f"-|-|-|-|-{num_correct}/{i+1}-|-|-|-|-")

        if isinstance(cc, DBBenchChatContent):
            del agent_messages[2:8]
            agent_messages[2].content = agent_messages[2].content.replace("Now, I will start a new problem in a new Database. My problem is: ", "")
            
        for msg in agent_messages:
            # save in sharegpt format
            if isinstance(msg, HumanMessage):
                _dict["conversations"].append({"from": "human", "value": msg.content})
            else:
                _dict["conversations"].append({"from": "gpt", "value": msg.content})
        print('*/'*100)
        print(_dict["conversations"])
        print('*/'*100)
        all_conversations.append(_dict)            

        save_json(all_conversations, f"./data/{agentbench_split}/{agentbench_split}-agentinstruct-env_gpt4-v5.json")
    

if __name__ == "__main__":
    agentbench_split = "dbbench" # choices: ["dbbench", "os"]
    main(agentbench_split)
