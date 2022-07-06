from enum import Enum


# Messages sent should be formatted as follows: MessagePrefixאdataאMessagePrefixאdata...
class MessagePrefix(Enum):
    DISCONNECT = ""
    CONNECTION = "con"
    KEY = "key"
    # We use these letter due to the fact Fernet uses base64 which does not support these letters avoiding all confusion
    FILE_SIZE = "גודל"
    FILE_NAME = "שם"


SEPARATOR = 'א'
BUFFER_SIZE = 1024*4
