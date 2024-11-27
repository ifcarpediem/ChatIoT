from actions.action import Action
from configs import CONFIG
from message import Message
from utils.logs import _logger
from llm import LLM
import json
from translator import Translator
import asyncio

SYSTEM_MESSAGE = '''
# Role
You are a useful assistant named ChatIoT in the field of smart home. Your task is to parse user input into commands.
"Commands" is a list expression in format of "id.service.property = <value>". For example, "1.light.on = true" means to turn on the light with id 1, using the service light and set the property on to true.

# Input
1. user request
2. device list: the information of devices related with user request {id, name, area, type and services}. Each service of the device may contains multiple properties.

# Solution
Based on the user request, you need to find the corresponding device and its services first. Then, you need to find the corresponding service and its properties. Finally, you need to generate the command based on the user request and the service properties. 

# TODO 如果都有且明确，或者可以明确推断
# TODO 不确定设备
# TODO 不确定服务
# TODO 不确定属性
# TODO 没有该设备、设备没有该服务、服务没有该属性

# Output
In AskUser type, you must return a json including "Action_type" and "Say_to_user". "Say_to_user" is the response to the user in oral language. Please note that the language of "Say_to_user" should be in the same language as the user request.
In Finish type,you must return a json including "Action_type""Thought" ,"Commands" and "Say_to_user". "Thought" is the reasoning process of how you generate the commands.

# TODO command为空的finish
# TODO command不为空的askuser

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
    "Say_to_user": "Ok, I have done it for you.",
    "Action_type": "Finish"
}'''

USER_MESSAGE = '''user_request: {user_request}
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
        _logger.info(f"DeviceControler run: {user_input}")
        user_request = user_input.content
        self.llm.add_system_msg(SYSTEM_MESSAGE)
        all_context = CONFIG.hass_data["all_context"]
        self.llm.add_user_msg(USER_MESSAGE.format(user_request=user_request, device_list=all_context))
        
        loop = asyncio.get_running_loop()
        rsp = await loop.run_in_executor(None, self.llm.chat_completion_json_v1, self.llm.history)

        _logger.info(f"DeviceControler rsp: {rsp}")
        rsp_json = self.parse_output(rsp)
        if rsp_json["Action_type"] == "Finish":
            self.llm.reset()
            commands = rsp_json["Commands"]
            say_to_user = rsp_json["Say_to_user"]
            # say_to_user = rsp_json["Say_to_user"] + "\n" + str(commands)
            TRANSLATOR = Translator()
            for command in commands:
                await TRANSLATOR.run_single_command(command)
            return Message(role=self.name, content=say_to_user, send_to=["User"], sent_from="DeviceControler", cause_by="Finish")
        elif rsp_json["Action_type"] == "AskUser":
            say_to_user = rsp_json["Say_to_user"]
            return Message(role=self.name, content=say_to_user, send_to=["User"], sent_from="DeviceControler", cause_by="AskUser")
        else:
            return Message(role=self.name, content="Sorry, something wrong.", send_to=["User"], sent_from="DeviceControler", cause_by="Finish")
