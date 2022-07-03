import socket


# This class stores all the necessary information needed about a given client socket
# when a value is unknown it is left blank.
class Client:
    def __init__(self, client_address, client_socket=""):
        self.client_address = str(client_address)
        self.client_socket = client_socket
