import select
import socket
import threading
import tkinter as tki
from enum import Enum
from tkinter import scrolledtext
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

    status_textbox = scrolledtext.ScrolledText(new_window, height='20', width='100', wrap=tki.WORD)
    for color in TextColor:
        status_textbox.tag_config(color, foreground=color.value)
    status_textbox.insert(tki.END, "Connection Status: no client connected", TextColor.DISCONNECTION)
    # We separate the connecting and receiving phase from the rest of the code in order to not interrupt the tkinter
    # main thread.
    connection_thread = threading.Thread(
        target=lambda: connect(new_window, server_socket, clients,
                               status_textbox))

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


class TextColor(Enum):
    CONNECTION = 'green'
    DISCONNECTION = 'red'
    KEY = 'blue'


# Waits for a client to connect and receives the public key from the client.
def connect(new_window, server_socket, clients, status_textbox):
    # Due to server shutting down sometimes before a connection has been made a try catch is required
    try:
        while True:
            client_sockets = []
            for current_client in clients:
                client_sockets.append(current_client.client_socket)

            print("attempting to connect to clients")
            ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [], [])
            for current_socket in ready_to_read:
                # if the socket is new add him to the connection
                if current_socket == server_socket:
                    (client_socket, client_address) = server_socket.accept()
                    clients.append(client.Client(client_socket, client_socket))
                    status_textbox.insert(tki.END, "\nConnection Status: " + str(client_address) + " connected!",
                                          TextColor.CONNECTION)
                    status_textbox.yview(tki.END)
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
                                    status_textbox.insert(tki.END,
                                                          "\nKey from: " + str(
                                                              current_client.client_address) + " received!: \n" + str(
                                                              public_key),
                                                          TextColor.KEY)
                                    status_textbox.yview(tki.END)
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
    data = ""
    try:
        data = client_sending_data.client_socket.recv(2048).decode()
    except Exception as e:
        print("Failed to receive data from: " + client_sending_data.client_address + str(e))
    if data == "":
        try:
            client_sending_data.client_socket.close()
        except Exception as e:
            print("Failed to close: " + client_sending_data.client_address + str(e))
        status_textbox.insert(tki.END, "\nClient: " + str(client_sending_data.client_address) + " has disconnected!",
                              TextColor.DISCONNECTION)
        status_textbox.yview(tki.END)
        clients.remove(client_sending_data)
    return data
