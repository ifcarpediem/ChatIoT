from dataclasses import dataclass, field
from pydantic import BaseModel

# @dataclass
# class Message(BaseModel):
#     """list[<role>: <content>]"""
#     role: str = field(default="")
#     content: str = field(default="")
#     # instruct_content: BaseModel = field(default=None)
#     cause_by: str = field(default="")
#     sent_from: str = field(default="")
#     send_to: list = field(default=[])

#     def __str__(self):
#         return f"{self.role}: {self.content}"
    
#     def to_dict(self):
#         return {
#             "role": self.role,
#             "content": self.content,
#             "cause_by": self.cause_by,
#             "sent_from": self.sent_from,
#             "send_to": self.send_to
#         }

class Message(BaseModel):
    role: str
    content: str
    cause_by: str
    sent_from: str
    send_to: list

    def __str__(self):
        return f"{self.role}: {self.content}"

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "cause_by": self.cause_by,
            "sent_from": self.sent_from,
            "send_to": self.send_to
        }



