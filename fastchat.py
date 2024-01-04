import json
import time
from typing import List, Dict, Union, Any
from conversation import Conversation, SeparatorStyle 
from langchain.schema import HumanMessage, AIMessage, SystemMessage

import requests
# import TimeoutException
from requests.exceptions import Timeout, ConnectionError


# Code taken from AgentBench: https://github.com/THUDM/AgentBench
class AgentClient:
    def __init__(self, *args, **kwargs):
        pass

    def inference(self, history: List[dict]) -> str:
        raise NotImplementedError()
    
def get_conversation_template(model_name):
    return Conversation(
        name="llama-2",
        system_template="[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n",
        roles=("[INST]", "[/INST]"),
        sep_style=SeparatorStyle.LLAMA2,
        sep=" ",
        sep2=" </s><s>",
    )



def langchain_to_fastchat(chat):
    new_chat = []
    for side in chat:
        if side.type == "human":
            new_chat.append({"role": "user", "content": side.content})
        else:
            new_chat.append({"role": "agent", "content": side.content})
    return new_chat

class FastChatAgent(AgentClient):
    """This agent is a test agent, which does nothing. (return empty string for each action)"""

    def __init__(
        self,
        model_name,
        controller_address=None,
        worker_address=None,
        temperature=0,
        max_new_tokens=32,
        top_p=0,
        prompter=None,
        args=None,
        **kwargs,
    ) -> None:
        if controller_address is None and worker_address is None:
            raise ValueError(
                "Either controller_address or worker_address must be specified."
            )
        self.controller_address = controller_address
        self.worker_address = worker_address
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.top_p = top_p
        if isinstance(prompter, dict):
            self.prompter = Prompter.get_prompter(prompter)
        else:
            self.prompter = prompter
        self.args = args or {}
        super().__init__(**kwargs)

    def predict_messages(self, history: List[dict]) -> str:
        return AIMessage(content=self.inference(langchain_to_fastchat(history)))

    def inference(self, history: List[dict]) -> str:
        if self.worker_address:
            worker_addr = self.worker_address
        else:
            controller_addr = self.controller_address
            worker_addr = controller_addr
        if worker_addr == "":
            raise ValueError
        gen_params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_new_tokens": self.max_new_tokens,
            "echo": False,
            "top_p": self.top_p,
            **self.args,
        }
        if self.prompter:
            prompt = self.prompter(history)
            gen_params.update(prompt)
        else:
            conv = get_conversation_template(self.model_name)
            for history_item in history:
                role = history_item["role"]
                content = history_item["content"]
                if role == "user":
                    conv.append_message(conv.roles[0], content)
                elif role == "agent":
                    conv.append_message(conv.roles[1], content)
                else:
                    raise ValueError(f"Unknown role: {role}")
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()
            gen_params.update(
                {
                    "prompt": prompt,
                    "stop": conv.stop_str,
                    "stop_token_ids": conv.stop_token_ids,
                }
            )
        headers = {"User-Agent": "FastChat Client"}
        for _ in range(3):
            try:
                response = requests.post(
                    self.worker_address + "/worker_generate_stream",
                    headers=headers,
                    json=gen_params,
                    stream=True,
                    timeout=120,
                )
                text = ""
                print(response)
                for line in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
                    if line:
                        data = json.loads(line)
                        if data["error_code"] != 0:
                            raise AgentNetworkException(data["text"])
                        text = data["text"]
                return text
            # if timeout or connection error, retry
            except Timeout:
                print("Timeout, retrying...")
            except ConnectionError:
                print("Connection error, retrying...")
            time.sleep(5)
        else:
            raise Exception("Timeout after 3 retries.")