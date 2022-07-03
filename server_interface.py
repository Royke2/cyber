import select
import socket
import threading
import tkinter as tki
from scrolled_status_text import *
from data_convetions import *
import client

from cryptography.hazmat.primitives.serialization import load_pem_public_key


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
                              command=lambda: shutdown_server(new_window, server_socket, clients, connection_thread))
    shutdown_btn.pack()
    # if the window is manually closed the server is closed
    new_window.protocol("WM_DELETE_WINDOW",
                        lambda: shutdown_server(new_window, server_socket, clients, connection_thread))

    status_textbox.pack()

    server_socket.bind((ip, port))
    server_socket.listen()
    print("Server is up and running")

    connection_thread.start()


# Waits for a client to connect and receives the public key from the client.
def connect(server_socket, clients, status_textbox):
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
                    # Sends the client that connect a list of all connected clients.
                    client_list = ""
                    for c in clients:
                        if client_list != "":
                            client_list += SEPARATOR
                        client_list += (MessagePrefix.CONNECTION.value + SEPARATOR + c.client_address
                                        + SEPARATOR + MessagePrefix.KEY.value + SEPARATOR + c.public_key)
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
                    client_located = False
                    for current_client in clients:
                        # finds the client to match the socket passing data
                        if current_client.client_socket == current_socket:
                            client_located = True
                            # checks if the client has already sent a public key. if he hasn't then this message is the
                            # clients public key
                            if current_client.public_key == "":
                                public_key = receive_data(current_client, clients, status_textbox)
                                # public_key = load_pem_public_key(client_socket.recv(2048))
                                if public_key != "":
                                    current_client.public_key = public_key
                                    status_textbox.insert(
                                        "Key from: " + str(current_client.client_address) + " received!: \n" + str(
                                            public_key), TextColor.KEY)
                                    # Sends the current client address and public key to all connected clients.
                                    for c in clients:
                                        if c != current_client:
                                            msg = (MessagePrefix.CONNECTION.value + SEPARATOR +
                                                   current_client.client_address + SEPARATOR +
                                                   MessagePrefix.KEY.value + SEPARATOR + current_client.public_key)
                                            c.client_socket.send(msg.encode())
                            else:
                                receive_data(current_client, clients, status_textbox)
    except Exception as e:
        print("!!! error in connection method !!! " + str(e))


def shutdown_server(window, server_socket, clients, connect_thread):
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
def receive_data(client_sending_data, clients, status_textbox):
    data = MessagePrefix.DISCONNECT.value
    try:
        data = client_sending_data.client_socket.recv(2048).decode()
    except Exception as e:
        print("Failed to receive data from: " + str(client_sending_data.client_address) + str(e))
    if data == MessagePrefix.DISCONNECT.value:
        try:
            client_sending_data.client_socket.close()
        except Exception as e:
            print("Failed to close: " + client_sending_data.client_address + str(e))
        status_textbox.insert("Client: " + str(client_sending_data.client_address) + " has disconnected!",
                              TextColor.DISCONNECTION)
        clients.remove(client_sending_data)
    return data
