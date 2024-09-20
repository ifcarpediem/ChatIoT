from .role import Role
from backend.agents.actions.generate_tap import GenerateTAP

class TapGenerator(Role):
    def __init__(self, name="", profile="TapGenerator", goal="Generate TAP based on user requests", **kwargs):
        super().__init__(name=name, profile=profile, goal=goal, **kwargs)
        self._init_actions([GenerateTAP])
        self._watch(["UserInput"])