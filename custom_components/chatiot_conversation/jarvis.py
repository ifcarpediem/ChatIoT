from utils.singleton import Singleton
import asyncio
from utils.logs import _logger
from roles.role import Role
from roles.manager import Manager
from roles.device_controler import DeviceControler
from roles.tap_generator import TapGenerator
from environment import Environment
from configs import CONFIG
from message import Message
from utils.singleton import Singleton

class Jarvis(metaclass=Singleton):
    def __init__(self):
        self.environment = Environment()
        self.flag = True
        self.last_message_from = None
        self.equip([Manager(), DeviceControler(), TapGenerator()])

    def equip(self, roles):
        self.environment.add_roles(roles)

    async def run(self, request: str):
        if self.flag:
            await self.environment.publish_message(Message(role="Jarvis", content=request, send_to= ["Manager"], sent_from= "User", cause_by="UserInput"))
        else:
            if self.last_message_from == None:
                raise Exception("last_message_from is None")
            else:
                await self.environment.publish_message(Message(role="Jarvis", content=request, send_to= [self.last_message_from], sent_from= "User",cause_by="UserResponse"))
        msg, flag = await self.environment.run()
        if flag:
            self.flag = True
            self.last_message_from = None
            self.environment.reset()
        else:
            self.flag = False
            self.last_message_from = msg.role
        return msg.content

JARVIS = Jarvis()