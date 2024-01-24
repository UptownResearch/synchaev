from tqdm.auto import tqdm
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from helpers import read_pickle, save_json, model, environment_model, creator_model
import os
from dotenv import load_dotenv
from chatcontent import DBBenchChatContent

load_dotenv() 
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

    
def main():
    cc = DBBenchChatContent(model, environment_model, creator_model)
    tasks = read_pickle("./tasks/dbbench_tasks-db_std.pickle")

    all_conversations = []
    for task in tqdm(tasks):
        _dict = {"conversations": []}
        agent_messages, _ = cc.play_start2end(task, 6)
        for msg in agent_messages:
            # save in sharegpt format
            if isinstance(msg, HumanMessage):
                _dict["conversations"].append({"from": "human", "value": msg.content})
            else:
                _dict["conversations"].append({"from": "gpt", "value": msg.content})
        print('*'*100)
        all_conversations.append(_dict)            

        save_json(all_conversations, "dbbench-db_std-env_gpt4.json")
    

if __name__ == "__main__":
    main()
