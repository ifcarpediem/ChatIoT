from collections import defaultdict
from .message import Message

class Memory():
    def __init__(self):
        self.storage: list[Message] = []
        self.index: dict[str, list[Message]] = defaultdict(list)

    def add(self, message: Message):
        if message in self.storage:
            return
        self.storage.append(message)
        if message.cause_by:
            self.index[message.cause_by].append(message)
        
    def get_by_role(self, role: str) -> list[Message]:
        """Return all messages of a specified role"""
        return [message for message in self.storage if message.role == role]
    
    def get_by_content(self, content: str) -> list[Message]:
        """Return all messages containing a specified content"""
        return [message for message in self.storage if content in message.content]

    def delete(self, message: Message):
        """Delete the specified message from storage, while updating the index"""
        self.storage.remove(message)
        if message.cause_by and message in self.index[message.cause_by]:
            self.index[message.cause_by].remove(message)

    def clear(self):
        """Clear storage and index"""
        self.storage = []
        self.index = defaultdict(list)

    def count(self):
        """Return the number of messages in storage"""
        return len(self.storage)

    def remember_by_keyword(self, keyword: str) -> list[Message]:
        """Try to recall all messages containing a specified keyword"""
        return [message for message in self.storage if keyword in message.content]

    def remember_by_keywords(self, keywords: list[str]) -> list[Message]:
        """Try to recall all messages containing all specified keywords"""
        return [message for message in self.storage if all(keyword in message.content for keyword in keywords)]

    def get(self, k=0) -> list[Message]:
        """Return the most recent k memories, return all when k=0"""
        return self.storage[-k:]

    def find_news(self, obsereved: list[Message], k=10) -> list[Message]:
        """Try to find new messages from the observed messages"""
        already_remembered = self.get(k)
        news = []
        for message in obsereved:
            if message not in already_remembered:
                news.append(message)
        return news

    def get_by_action(self, action: str) -> list[Message]:
        """Return all messages triggered by a specified Action"""
        return self.index[action]

    def get_by_actions(self, actions: list[str]) -> list[Message]:
        """Return all messages triggered by any specified Actions"""
        return [message for action in actions for message in self.index[action]]
    
    def get_latest_message(self) -> Message:
        """Return the latest message"""
        return self.storage[-1]

