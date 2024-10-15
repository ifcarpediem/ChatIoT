from pydantic import BaseModel, Field
from .roles.role import Role
from .memory import Memory
from .message import Message
from .roles.manager import Manager
from .roles.device_controler import DeviceControler
from .roles.tap_generator import TapGenerator
import asyncio
from .tools.home_assistant import HomeAssistantApi
from backend.agents.utils.logs import logger

class Environment(BaseModel):
    roles: dict[str, Role] = Field(default_factory=dict)
    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default="")
    message_cnt: int = Field(default=0)
    home_assistant: HomeAssistantApi = Field(default_factory=HomeAssistantApi)
    devices: list = Field(default_factory=list)
    model_zoo: list = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self):
        super().__init__()
        self.devices = self.home_assistant.get_device_context()
        self.add_roles([Manager(), DeviceControler(), TapGenerator()])

    def add_role(self, role: Role):
        """增加一个在当前环境的Role"""
        role.set_env(self)
        self.roles[role.profile] = role

    def add_roles(self, roles: list[Role]):
        """增加一批在当前环境的Role"""
        for role in roles:
            self.add_role(role)

    async def publish_message(self, message: Message):
        """向当前环境发布信息"""
        self.memory.add(message)
        self.history += f"\n{message}"
        self.message_cnt += 1

    async def run(self, k=10) -> tuple[Message, bool]:
        # 默认允许角色之间对话10轮
        logger.info(f"-----------------run-----------------")
        for i in range(k):
            logger.info(f"-----------------{i}-----------------")
            # 判断是否有新消息，如果没有则退出
            if i==0:
                current_message_cnt = self.message_cnt
            else:
                if self.message_cnt > current_message_cnt:
                    current_message_cnt = self.message_cnt
                else:
                    break
            futures = []
            for key in self.roles.keys():
                role = self.roles[key]
                future = role.run()
                futures.append(future)
            await asyncio.gather(*futures)
        latest_message = self.memory.get_latest_message()
        logger.info(f"latest_message: {latest_message.to_dict()}")
        if latest_message.cause_by not in ["AskUser", "Finish"]:
            return ("运行出错，请检查", True)
        elif latest_message.cause_by == "Finish":
            return (latest_message, True)
        elif latest_message.cause_by == "AskUser":
            return (latest_message, False)
        
    def get_roles(self):
        """获得环境内的所有Role"""
        return self.roles

    def get_role(self, role_name: str) -> Role:
        """获得环境内的指定Role"""
        return self.roles.get(role_name, None)

    # 重置环境
    def reset(self):
        self.memory = Memory()
        self.history = ""
        self.message_cnt = 0
        for key in self.roles.keys():
            role = self.roles[key]
            role.reset()