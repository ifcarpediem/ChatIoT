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
Based on the user request, you need to find the tirgger, condition and action, then find the corresponding device, service and its properties. If you cannot generate the exact TAP, you need to ask the user for more information.
So There are three Action_type: AskUser and Finish.

# Output
In AskUser type, you must return a json including "Thought", "Action_type" and "Say_to_user". "Say_to_user" is the response to the user to ask for more information. Please note that the language of "Say_to_user" should be in the same language as the user request.

In Finish type,you must return a json including "Thought" ,"Action_type", "TAP" and "Say_to_user". "Thought" is the reasoning process of how you generate the TAP. "TAP" is a json expression in format of {"trigger": <trigger>, "condition": <condition>, "action": <action>}. <trigger>, <condition> and <action> are formed by basic elements "id.service.property<op><value>". The <op> in <trigger> and <condition> is chosen from "<", ">", or "==" while the <op> in <action> must be "=" . The <value> is a value which can be of various types based on the property type, including bool, int, and string. In <trigger> and <action>, elements are separated by ",". In <condition>, elements are combined using "&&", "||" and "()", such as "condition_1&& (condition_2||condition_3)".

# Examples
Example 1:
USER:
user request: If the door of lab is opened, turn on the light.
device list: [{"id":1,"area":"laboratory","type":"light","services":{"light":{"on":{"description":"Switch Status","format":"bool","access":["read","write","notify"]},"brightness":{"description":"Brightness","format":"uint16","access":["read","write","notify"],"unit":"percentage","value-range":[1,65535,1]},"color_temperature":{"description":"Color Temperature","format":"uint32","access":["read","write","notify"],"unit":"kelvin","value-range":[2700,6500,1]}},"yeelight_scene":{"delay_off":{"description":"","format":"int16","access":["read","write","notify"],"unit":"minutes","value-range":[0,60,1]},"smart_switch":{"description":"","format":"int32","access":["read","write","notify"],"value-range":[0,1,1]},"powerup_setting":{"description":"上电开关灯状态","format":"uint32","access":["notify","write","read"],"unit":"none","value-list":[{"value":0,"description":"关灯000"},{"value":1,"description":"恢复默认状态100"},{"value":256,"description":"关灯010"},{"value":257,"description":"恢复上次状态110"},{"value":65536,"description":"设置默认状态001"},{"value":65537,"description":"设置默认状态101"}]}}}},{"id":2,"area":"laboratory","type":"magnet_sensor","services":{"magnet_sensor":{"illumination":{"description":"Illumination","format":"uint8","access":["read","notify"],"value-list":[{"value":1,"description":"Weak"},{"value":2,"description":"Strong"}]},"contact_state":{"description":"Contact State","format":"bool","access":["read","notify"]}}}}]

ASSISTANT:
{
    "Thought": "Based on the user request, use the magnet_sensor in the laboratory as the trigger. The device id is 2. The service is magnet_sensor. The property is contact_state. The value is true. The light in the laboratory is the action. The device id is 1. The service is light. The property is on. The value is true.",
    "Action_type": "Finish",
    "TAP": {"trigger": "2.magnet_sensor.contact_state==true", "condition": "", "action": "1.light.on=true"},
    "Say_to_user": "Yes, I have done it for you."
}
'''

USER_MESSAGE = '''user_request: {user_request}
device_list: {device_list}'''

FORMAT_EXAMPLE = ''''''

OUTPUT_MAPPING = {}

class GenerateTAP(Action):
    def __init__(self, name="TAPGenerator", context=None):
        super().__init__(name, context)
        self.llm = LLM()
        self.user_request = None

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
        logger.info(f"TapGenerator run: {user_input}")
        if self.user_request is None:
            self.user_request = user_input.content
        user_request = user_input.content
        self.llm.add_user_msg(SYSTEM_MESSAGE)
        devices_json = get_json("./temp/miot/device_context.json")
        self.llm.add_user_msg(USER_MESSAGE.format(user_request=user_request, device_list=devices_json))
        rsp = self.llm.ask(self.llm.history)
        logger.info(f"TapGenerator rsp: {rsp}")
        # TODO error handling
        rsp_json = self.parse_output(rsp)
        if rsp_json["Action_type"] == "Finish":
            self.llm.reset()
            tap = rsp_json["TAP"]
            say_to_user = rsp_json["Say_to_user"]
            translator = Translator()
            translator.deploy_tap(self.user_request, tap)
            return Message(role=self.name, content=say_to_user, send_to=["User"], cause_by="Finish", sent_from="TAPGenerator")
        elif rsp_json["AskUser"] == "AskUser":
            say_to_user = rsp_json["Say_to_user"]
            return Message(role=self.name, content=say_to_user, send_to=["User"], cause_by="AskUser", sent_from="TAPGenerator")
        else:
            return Message(role=self.name, content="Sorry, something wrong.", send_to=["User"], cause_by="Finish", sent_from="TAPGenerator")
