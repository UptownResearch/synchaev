from tqdm.auto import tqdm
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import read_pickle, save_json, model, environment_model, creator_model
import os
from dotenv import load_dotenv
from chatcontent import DBBenchChatContent, OSChatContent

load_dotenv() 
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

    
def main():
    cc = DBBenchChatContent(model, environment_model, creator_model)
    # cc = OSChatContent(model, environment_model, creator_model)
    tasks = read_pickle("./data/dbbench/dbbench_tasks-agentinstruct.pickle")

    all_conversations = []
    for i, task in tqdm(enumerate(tasks)):
        _dict = {"conversations": [], "id": f"db_{i}"}
        agent_messages, _ = cc.play_start2end(task, 6)

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

        save_json(all_conversations, "./data/dbbench/dbbench-agentinstruct-env_gpt4-v3.json")
    

if __name__ == "__main__":
    main()
