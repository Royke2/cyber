from enum import Enum


# Messages sent should be formatted as follows: MessagePrefix, data, MessagePrefix, data...
class MessagePrefix(Enum):
    DISCONNECT = ""
    CONNECTION = "con"
    KEY = "key"
