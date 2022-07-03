from enum import Enum


# Messages sent should be formatted as follows: MessagePrefixאdataאMessagePrefixאdata...
class MessagePrefix(Enum):
    DISCONNECT = ""
    CONNECTION = "con"
    KEY = "מפתח"
    FILE_RECIPIENT = "rec"
    FILE_SIZE = "size"


SEPARATOR = 'א'
BUFFER_SIZE = 4096
