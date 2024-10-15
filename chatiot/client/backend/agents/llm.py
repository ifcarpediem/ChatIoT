import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))

from typing import NamedTuple
from config import CONFIG
from backend.agents.utils.singleton import Singleton
import requests
from backend.agents.utils.logs import logger

class Costs(NamedTuple):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost: float

class CostManager(metaclass=Singleton):
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0

    def update_cost(self, completion_tokens, prompt_tokens, cost):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost += cost
        CONFIG.total_cost = self.total_cost

    def get_total_prompt_tokens(self):
        return self.total_prompt_tokens
    
    def get_total_completion_tokens(self):
        return self.total_completion_tokens
    
    def get_total_cost(self):
        return self.total_cost
    
    # def get_costs(self):
    #     return Costs(self.total_prompt_tokens, self.total_completion_tokens, self.total_cost)
    
    @property
    def costs(self):
        return Costs(self.total_prompt_tokens, self.total_completion_tokens, self.total_cost)

class LLM():
    def __init__(self):
        self._cost_manager = CostManager()
        self.total_completion_tokens = 0
        self.total_prompt_tokens = 0
        self.total_cost = 0.0
        self.model = CONFIG.configs["llm_server"]['model']
        self.history = []
    
    @property
    def costs(self):
        return Costs(self.total_prompt_tokens, self.total_completion_tokens, self.total_cost)

    def add_system_msg(self, msg):
        self.history.append({"role": "system", "content": msg})

    def add_user_msg(self, msg):
        self.history.append({"role": "user", "content": msg})

    def add_assistant_msg(self, msg):
        self.history.append({"role": "assistant", "content": msg})
    
    def ask(self, messages: list, rsp_format: str="") -> str:
        '''
        response是一个json对象，包含rsp，completion_tokens，prompt_tokens, cost
        rsp根据rsp_format返回text或json_string
        '''
        chat_request = {
            "model": self.model,
            "messages": messages,
            "format": rsp_format # text or json
        }
        llm_server_host = CONFIG.configs['llm_server']['host']
        llm_server_port = CONFIG.configs['llm_server']['port']
        response = requests.post(f"http://{llm_server_host}:{llm_server_port}/llm/ask", json=chat_request).json()
        logger.debug(f"response: {response}")
        # 更新cost
        self._cost_manager.update_cost(response['completion_tokens'], response['prompt_tokens'], response['cost'])
        self._update_llm_cost(response['completion_tokens'], response['prompt_tokens'], response['cost'])
        return response['rsp']

    def _update_llm_cost(self, completion_tokens, prompt_tokens, cost):
        self.total_completion_tokens += completion_tokens
        self.total_prompt_tokens += prompt_tokens
        self.total_cost += cost
    
    def reset(self, model=None):
        self.history = []
        self.total_completion_tokens = 0
        self.total_prompt_tokens = 0
        self.total_cost = 0.0
        if model:
            self.model = model
        else:
            self.model = CONFIG.configs["llm_server"]['model']

if __name__ == "__main__":
    # 测试连续对话
    llm = LLM()
    llm.add_user_msg("我是李明。")
    rsp = llm.ask(llm.history, "")
    print(rsp)
    print(llm._cost_manager.costs)
    print(llm.costs)
    llm.add_system_msg(rsp)
    llm.add_user_msg("我的名字是什么？")
    rsp = llm.ask(llm.history, "")
    print(rsp)
    print(llm._cost_manager.costs)
    print(llm.costs)