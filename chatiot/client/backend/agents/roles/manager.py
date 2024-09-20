from .role import Role
from backend.agents.actions.router import Router

class Manager(Role):
    def __init__(self, name="", profile="Manager", goal="Analyze user request and decide which agent to handle it", **kwargs):
        super().__init__(name=name, profile=profile, goal=goal, **kwargs)
        self._init_actions([Router])
        self._watch(["UserInput"])