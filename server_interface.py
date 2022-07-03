import select
import socket
import threading
import tkinter as tki

from cryptography.fernet import Fernet
from cryptography.hazmat import primitives
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

import client
from data_convetions import *
from scrolled_status_text import *


def start_server(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("1000x500")

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = []

    status_textbox = ScrolledStatusText(new_window, height='20', width='100', wrap=tki.WORD)
    status_textbox.insert("Connection Status: no client connected", TextColor.MESSAGE)

    # We separate the connecting and receiving phase from the rest of the code in order to not interrupt the tkinter
    # main thread.
    connection_thread = threading.Thread(
        target=lambda: connect(server_socket, clients, status_textbox))

    shutdown_btn = tki.Button(new_window,
                              text="Exit",
                              command=lambda: shutdown_server(new_window, server_socket, clients))
    shutdown_btn.pack()
    # if the window is manually closed the server is closed
    new_window.protocol("WM_DELETE_WINDOW",
                        lambda: shutdown_server(new_window, server_socket, clients))

    status_textbox.pack()

    server_socket.bind((ip, port))
    server_socket.listen()
    print("Server is up and running")

    connection_thread.start()


# Waits for a client to connect and receives the public key from the client.
def connect(server_socket, clients, status_textbox):
    # Creates a symmetrical key used for file encryption
    symmetrical_key = Fernet.generate_key()
    # Due to server shutting down sometimes before a connection has been made a try catch is required
    try:
        while True:
            client_sockets = []
            for current_client in clients:
                client_sockets.append(current_client.client_socket)

            print("attempting to connect to clients")
            ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [], [])
            for current_socket in ready_to_read:
                # if the socket is new add him to the connection.
                if current_socket == server_socket:
                    (client_socket, client_address) = server_socket.accept()
                    # Makes a list of all connected clients to send the new client.
                    client_list = ""
                    for c in clients:
                        # Sends the new client address to all connected clients.
                        msg = MessagePrefix.CONNECTION.value + SEPARATOR + current_client.client_address
                        c.client_socket.send(msg.encode())
                        if client_list != "":
                            client_list += SEPARATOR
                        client_list += MessagePrefix.CONNECTION.value + SEPARATOR + c.client_address
                    print(client_list)
                    if client_list != "":
                        client_socket.send(client_list.encode())

                    # Adds the current client to the list of clients.
                    clients.append(client.Client(client_address, client_socket))
                    status_textbox.insert("Connection Status: " + str(client_address) + " connected!",
                                          TextColor.CONNECTION)
                    print("Client connected")
                else:
                    print("received data from client")
                    for current_client in clients:
                        # finds the client to match the socket passing data
                        if current_client.client_socket == current_socket:
                            receive_data(current_client, clients, status_textbox, symmetrical_key)
    except Exception as e:
        print("!!! error in connection method !!! " + str(e))


def shutdown_server(window, server_socket, clients):
    try:
        # connect_thread.stop()
        for current_client in clients:
            current_client.client_socket.send("".encode())
            current_client.client_socket.close()
    except Exception as e:
        print("Attempted to tell client to close but failed.\n" + str(e))
    server_socket.close()
    print("Server successfully closed")
    window.destroy()


# Gets a client that has sent data and checks if the client sent a disconnection message or an error has occurred.
# If the client disconnected the server removes him from the client list.
# @returns data received from client
def receive_data(client_sending_data, clients, status_textbox, symmetrical_key):
    data = MessagePrefix.DISCONNECT.value
    try:
        data = client_sending_data.client_socket.recv(BUFFER_SIZE).decode()
    except Exception as e:
        print("Failed to receive data from: " + str(client_sending_data.client_address) + str(e))
    data = data.split(SEPARATOR)
    # Checks the prefix of each data received and acts accordingly
    for i in range(0, len(data), 2):
        # The client has announced that it has disconnected.
        if data[i] == MessagePrefix.DISCONNECT.value:
            client_disconnected(client_sending_data, status_textbox, clients)
            break

        # The client has given an asymmetrical public key in order to get the symmetrical key.
        elif data[i] == MessagePrefix.KEY.value:
            key_request(client_sending_data, data[i + 1], status_textbox, symmetrical_key)

        elif data[i] == MessagePrefix.FILE_RECIPIENT.value:
            received_file(client_sending_data, data, clients, status_textbox)


def client_disconnected(client_sending_data, status_textbox, clients):
    try:
        client_sending_data.client_socket.close()
    except Exception as e:
        print("Failed to close: " + client_sending_data.client_address + str(e))
    status_textbox.insert("Client: " + str(client_sending_data.client_address) + " has disconnected!",
                          TextColor.DISCONNECTION)
    clients.remove(client_sending_data)


# Sends the client an encrypted version the symmetrical key using the asymmetrical public key that the client sent
def key_request(client_sending_data, public_key, status_textbox, symmetrical_key):
    status_textbox.insert(
        "Key from: " + str(client_sending_data.client_address) + " received!: \n" + str(
            public_key), TextColor.KEY)
    public_key = primitives.serialization.load_pem_public_key(
        public_key.encode(), backend=default_backend())
    pad = padding.OAEP(mgf=padding.MGF1(algorithm=primitives.hashes.SHA256()),
                       algorithm=primitives.hashes.SHA256(),
                       label=None
                       )
    encrypted_symmetrical_key = public_key.encrypt(symmetrical_key, pad)
    # Sends key without prefix due to the fact the encrypted value may have any type of value
    client_sending_data.client_socket.send(encrypted_symmetrical_key)


def received_file(client_sending_data, data, clients, status_textbox):
    target_client_exists = False
    target_client = None
    for current_client in clients:
        if data[1] == current_client.client_address:
            target_client_exists = True
            target_client = current_client
            break
    if target_client_exists:
        status_textbox.insert("Received file from: " + str(client_sending_data.client_address),
                              TextColor.MESSAGE_SENT.value)
        file = client_sending_data.client_socket.recv(BUFFER_SIZE).decode()
        target_client.client_socket.send(file)
        status_textbox.insert("Sent file to: " + str(target_client.client_address), TextColor.MESSAGE_SENT)
