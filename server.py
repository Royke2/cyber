import socket
import threading
import tkinter as tki
from enum import Enum
from tkinter import scrolledtext

from cryptography.hazmat.primitives.serialization import load_pem_public_key


def start_server(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("1000x500")

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sockets = []

    shutdown_btn = tki.Button(new_window,
                              text="Exit",
                              command=lambda: shutdown_server(new_window, server_socket, client_sockets))
    shutdown_btn.pack()
    # if the window is manually closed the server is closed
    new_window.protocol("WM_DELETE_WINDOW", lambda: shutdown_server(new_window, server_socket, client_sockets))

    status_textbox = scrolledtext.ScrolledText(new_window, height='20', width='100', wrap=tki.WORD)
    for color in TextColor:
        status_textbox.tag_config(color, foreground=color.value)
    status_textbox.insert(tki.END, "Connection Status: no client connected", TextColor.DISCONNECTION)
    status_textbox.pack()

    server_socket.bind((ip, port))
    server_socket.listen()
    print("Server is up and running")

    # We separate the connecting and receiving phase from the rest of the code in order to not interrupt the tkinter
    # main thread.
    connection_thread = threading.Thread(
        target=lambda: connect(new_window, server_socket, client_sockets,
                               status_textbox))
    connection_thread.start()


class TextColor(Enum):
    CONNECTION = 'green'
    DISCONNECTION = 'red'
    KEY = 'blue'


# Waits for a client to connect and receives the public key from the client.
def connect(new_window, server_socket, client_sockets, status_textbox):
    # Due to server shutting down sometimes before a connection has been made a try catch is required
    try:
        print("attempting to connect to client")

        (client_socket, client_address) = server_socket.accept()

        status_textbox.insert(tki.END, "\nConnection Status: " + str(client_address) + " connected!",
                              TextColor.CONNECTION)
        status_textbox.yview(tki.END)

        print("Client connected")

        public_key = client_socket.recv(2048)
        # public_key = load_pem_public_key(client_socket.recv(2048))

        status_textbox.insert(tki.END, "\nKey from: " + str(client_address) + " received!: \n" + str(public_key),
                              TextColor.KEY)
        status_textbox.yview(tki.END)

        print("Public key received")

    except Exception as e:
        print(e)


def shutdown_server(window, server_socket, client_sockets):
    try:
        for client in client_sockets:
            client.send("".encode())
    except Exception as e:
        print("Attempted to tell client to close but failed.\n" + str(e))
    server_socket.close()
    print("Server successfully closed")
    window.destroy()
