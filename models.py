from dataclasses import dataclass
from enum import StrEnum


class MessageType(StrEnum):
    START = "start"
    STREAM = "stream"
    END = "end"
    ERROR = "error"

@dataclass
class Message:
    title: str | None = None
    haiku: str | None = None
    content: str | None = None

@dataclass
class ChatResponse:
    source: str
    message: Message
    type: MessageType
