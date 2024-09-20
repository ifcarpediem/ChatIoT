from abc import ABC, abstractmethod
# from backend.agents.llm import LLM
from backend.agents.utils.logs import logger
# from backend.agents.utils.common import OutputParser

class Action(ABC):
    def __init__(self, name='', context=None):
        print("Action init")
        print(f"name: {name}")
        self.name: str = name
        self.context = context
        # self.llm = LLM()
        self.prefix = ""
        self.profile = ""
        self.desc = ""
        self.content = ""

    def set_prefix(self, prefix, profile):
        """Set prefix for later usage"""
        self.prefix = prefix
        self.profile = profile
    
    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()
    
    # async def _aask(self, prompt: str) -> str:
    #     self.llm.add_user_msg(prompt)
    #     rsp = self.llm.ask(self.llm.history)
    #     logger.debug(rsp)
    #     return rsp

    # async def _aask_v1(self, prompt: str, output_data_mapping: dict) -> str:
    #     self.llm.add_user_msg(prompt)
    #     rsp = self.llm.ask(self.llm.history)
    #     logger.debug(rsp)
    #     parsed_data = OutputParser.parse_data_with_mapping(rsp, output_data_mapping)
    #     return parsed_data
        
    @abstractmethod
    async def run(self, *args, **kwargs):
        """Run action"""
        raise NotImplementedError("The run method should be implemented in a subclass.")