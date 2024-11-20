from abc import ABC, abstractmethod
from utils.logs import _logger

class Action(ABC):
    def __init__(self, name='', context=None):
        _logger.debug("Action init")
        _logger.debug(f"Action name: {name}")
        self.name: str = name
        self.context = context
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
        
    @abstractmethod
    async def run(self, *args, **kwargs):
        """Run action"""
        raise NotImplementedError("The run method should be implemented in a subclass.")