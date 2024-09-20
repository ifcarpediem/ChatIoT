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
You are a useful assistant named ChatIoT in the field of smart home. Your task is to parse user input into commands.

# Input
1. user request
2. device list: the information of devices related with user request: id, area, type and services. Each service of the device may contains multiple properties.

# Solution
Based on the user request, you need to find the corresponding device and its services. Then, you need to find the corresponding service and its properties. Finally, you need to generate the command based on the user request and the service properties. If there is something vague in the user request and you cannot generate the exact command, you need to ask the user for more information. So There are two Action_type: AskUser and Finish.

# Output
In AskUser type, you must return a json including "Action_type" and "Say_to_user". "Say_to_user" is the response to the user in oral language. Please note that the language of "Say_to_user" should be in the same language as the user request.
In Finish type,you must return a json including "Action_type""Thought" ,"Commands" and "Say_to_user". "Thought" is the reasoning process of how you generate the commands. "Commands" is a list expression in format of "id.service.property = <value>". "Say_to_user" is the response to the user in oral language. Please note that the language of "Say_to_user" should be in the same language as the user request.

# Examples
Example 1:
USER:
user request: turn on the light in the laboratory and set the brightness to 50%
device list: [{'id': 1, 'area': 'laboratory', 'type': 'light', 'services': {'light': {'on': {'description': 'Switch Status', 'format': 'bool', 'access': ['read', 'write', 'notify']}, 'brightness': {'description': 'Brightness', 'format': 'uint16', 'access': ['read', 'write', 'notify'], 'unit': 'percentage', 'value-range': [1, 65535, 1]}}}}]
ASSISTANT:
{
    "Thought": "Based on the user request, the target device is the light in the laboratory. The device id is 1. It provide one service named light. The service contains two properties: on and brightness. The user request is to turn on the light and set the brightness to 50%. The value of on is true and the value of brightness is 32767.",
    "Commands": [
        "1.light.on = true",
        "1.light.brightness = 32767"
    ],
    "Say_to_user": "Ok, I have done it for you."
}'''

USER_MESSAGE = '''
user_request: {user_request}
device_list: {device_list}'''


FORMAT_EXAMPLE = ''''''

OUTPUT_MAPPING = {}

class ControlDevice(Action):
    def __init__(self, name="DeviceControler", context=None):
        super().__init__(name, context)
        self.llm = LLM()

    def parse_output(self, output: str) -> dict:
        # TODO error handling

        if output.startswith("```json"):
            output = output[7:]
            output = output[:-3]
            return json.loads(output.strip())
        elif output.startswith("```"):
            output = output[3:]
            output = output[:-3]
            return json.loads(output.strip())
        else:
            return json.loads(output.strip())

    async def run(self, history_msg: list[Message], user_input: Message) -> Message:
        logger.info(f"DeviceControler run: {user_input}")
        user_request = user_input.content
        self.llm.add_user_msg(SYSTEM_MESSAGE)
        devices_json = get_json("./temp/miot/device_context.json")
        self.llm.add_user_msg(USER_MESSAGE.format(user_request=user_request, device_list=devices_json))
        rsp = self.llm.ask(self.llm.history)
        logger.info(f"DeviceControler rsp: {rsp}")
        # rsp_json = json.loads(rsp)
        rsp_json = self.parse_output(rsp)
        if rsp_json["Action_type"] == "Finish":
            self.llm.reset()
            commands = rsp_json["Commands"]
            say_to_user = rsp_json["Say_to_user"]
            translator = Translator()
            for command in commands:
                translator.run_single_command(command)
            return Message(role=self.name, content=say_to_user, send_to=["User"], sent_from="DeviceControler", cause_by="Finish")
        elif rsp_json["Action_type"] == "AskUser":
            say_to_user = rsp_json["Say_to_user"]
            return Message(role=self.name, content=say_to_user, send_to=["User"], sent_from="DeviceControler", cause_by="AskUser")
        else:
            return Message(role=self.name, content="Sorry, something wrong.", send_to=["User"], sent_from="DeviceControler", cause_by="Finish")
