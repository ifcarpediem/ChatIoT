from .action import Action
from config import CONFIG
from backend.agents.message import Message
from backend.agents.utils.logs import logger
from backend.agents.llm import LLM
import json
from backend.agents.tools.translator import Translator
from backend.agents.utils.utils import get_json

SYSTEM_MESSAGE = '''
# Role
You are a useful assistant named TapGenerator in the field of smart home. Your task is to parse user input into trigger-action program.

# Input
1. user request
2. device list: the information of devices related with user request: id, area, type and services. Each service of the device may contains multiple properties.

# Solution
Based on the user request, you need to find the tirgger, condition and action, then find the corresponding device, service and its properties. If you need use camera to detect something, you need to check the model zoo to see if there is a model that supports the detection service of the camera. If not, you need to request a model to support the detection service. Then you need to create a service for the camera. So There are three Action_type: AskUser, CreateService and Finish.

# Output
In AskUser type, you must return a json including "Thought", "Action_type" and "Say_to_user". "Say_to_user" is the response to the user to ask for more information. Please note that the language of "Say_to_user" should be in the same language as the user request.
In CreateService type, you must return a json including "Thought", "Action_type" "camera_id" and "service". "camera_id" is the id of the camera. "service" is the service you need to create for the camera.
In Finish type,you must return a json including "Thought" ,"Action_type", "TAP" and "Say_to_user". "Thought" is the reasoning process of how you generate the TAP. "TAP" is a json expression in format of {"trigger": <trigger>, "condition": <condition>, "action": <action>}. <trigger>, <condition> and <action> are formed by basic elements "id.service.property<op><value>". The <op> in <trigger> and <condition> is chosen from "<", ">", or "==" while the <op> in <action> must be "=" . The <value> is a value which can be of various types based on the property type, including bool, int, and string. In <trigger> and <action>, elements are separated by ",". In <condition>, elements are combined using "&&", "||" and "()", such as "condition_1&& (condition_2||condition_3)".

# Examples
Example 1:
USER:
user request: If the camera detects a cat, turn on the light in the laboratory.
device list: [{'id': 1, 'area': 'laboratory', 'type': 'light', 'services': {'light': {'on': {}}}}, {"id":2,"area":"laboratory","type":"camera","services":{'cat_detect': {'description': 'Detect Cat', 'format': 'bool', 'access': ['read']}}}]
model zoo: []

ASSISTANT:
{
    "Thought": "Based on the user request, the target device is the light in the laboratory. The device id is 1. It provide one service named light. The service contains one property: on. The user request is to open the light when the camera detects a cat. The trigger is 2.camera.cat_detect==true. The action is 1.light.on=true.",
    "Action_type": "Finish",
    "TAP": {"trigger": "2.camera.cat_detect==true", "condition": "", "action": "1.light.on=true"}, 
    "Say_to_user": "Yes, I have done it for you."
}
'''

USER_MESSAGE = '''user_request: {user_request}'''

FORMAT_EXAMPLE = ''''''

OUTPUT_MAPPING = {}

class GenerateTAP(Action):
    def __init__(self, name="TAPGenerator", context=None):
        super().__init__(name, context)
        self.llm = LLM()
        self.user_request = None

    def parse_output(self, output: str) -> dict:
        # TODO error handling
        pass

    async def run(self, history_msg: list[Message], user_input: Message) -> Message:
        if user_input.cause_by == "UserInput":
            self.user_request = user_input.content
        user_request = user_input.content
        self.llm.add_user_msg(SYSTEM_MESSAGE)
        self.llm.add_user_msg(USER_MESSAGE.format(user_request=user_request))
        rsp = self.llm.ask(self.llm.history)
        # TODO error handling
        rsp_json = json.loads(rsp)
        if rsp_json["Action_type"] == "Finish":
            self.llm.reset()
            tap = rsp_json["TAP"]
            say_to_user = rsp_json["Say_to_user"]
            translator = Translator()
            translator.deploy_tap(self.user_request, tap)
            return Message(role=self.name, content=say_to_user, send_to=["User"], cause_by="Finish")
        elif rsp_json["AskUser"] == "AskUser":
            say_to_user = rsp_json["Say_to_user"]
            return Message(role=self.name, content=say_to_user, send_to=["User"], cause_by="AskUser")
        else:
            return Message(role=self.name, content="Sorry, something wrong.", send_to=["User"], cause_by="Finish", sent_from="TAPGenerator")
