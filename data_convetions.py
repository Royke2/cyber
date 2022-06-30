from enum import Enum


# Messages sent should be formatted as follows: MessagePrefixאdataאMessagePrefixאdata...
class MessagePrefix(Enum):
    DISCONNECT = ""
    CONNECTION = "con"
    KEY = "key"


SEPARATOR = 'א'
