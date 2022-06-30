import socket
import tkinter as tki
from tkinter import filedialog
from scrolled_status_text import *
from threading import Thread
from time import sleep
from data_convetions import *
from client import Client

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def start_client(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("Client")
    new_window.geometry("500x500")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.getaddrinfo('localhost', 8080)

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)
    print("ip: " + ip)
    print("port: " + str(port))

    status_textbox = ScrolledStatusText(new_window, height='20', width='100', wrap=tki.WORD)
    status_textbox.insert("connecting to server please wait...", TextColor.MESSAGE)
    status_textbox.pack()

    file_explorer_lbl = tki.Label(new_window,
                                  text="File Explorer:",
                                  width=100, height=4,
                                  fg="blue")
    file_explorer_lbl.pack()
    explore_files_btn = tki.Button(new_window,
                                   text="Browse Files",
                                   command=lambda: browse_files(file_explorer_lbl))
    explore_files_btn.pack()

    connection_thread = Thread(
        target=lambda: attempt_connection(new_window, client_socket, ip, port, status_textbox))

    shutdown_btn = tki.Button(new_window,
                              text="Exit",
                              command=lambda: shutdown_client(new_window, client_socket))
    shutdown_btn.pack()
    # if the window is manually closed the client is closed
    new_window.protocol("WM_DELETE_WINDOW",
                        lambda: shutdown_client(new_window, client_socket))

    connection_thread.start()


# Adds a file explorer in order to choose the file to upload.
def browse_files(file_explorer_lbl):
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    # Change label contents
    if filename != "":
        file_explorer_lbl.configure(text="File Opened: " + filename)


# attempts to connect to the server in an incrementing loop till it succeeds
def attempt_connection(window, client_socket, ip, port, status_textbox):
    wait_time_increment = 2.5  # in seconds
    max_wait_time = 10  # in seconds
    connection_attempt_wait_time = 0
    connected = False
    while not connected:
        try:
            client_socket.connect((ip, port))
        except Exception as e:
            # increases wait time each time due to the fact if it hasn't work up till then it most likely won't work
            # immediately, so the system conserves resources.
            if connection_attempt_wait_time < max_wait_time:
                connection_attempt_wait_time += wait_time_increment
            try:
                status_textbox.insert("connection refused trying in: " + str(
                    connection_attempt_wait_time) + " seconds", TextColor.MESSAGE)
            except Exception as e:
                print(str(e))
            print(str(e))
            print("connection refused trying in: " + str(connection_attempt_wait_time) + " seconds")
            sleep(connection_attempt_wait_time)
        else:
            connected = True
            client_connected(window, client_socket, status_textbox)


# run when the client has successfully connected to the server
def client_connected(window, client_socket, status_textbox):
    status_textbox.insert("The client has successfully connected to the server!", TextColor.CONNECTION)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    # serializing the key in order to be able to send the key to the server
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                  format=serialization.PublicFormat.SubjectPublicKeyInfo)
    print("Client: public key:" + str(pem))
    client_socket.send(pem)

    print("client: sent key to server.")

    fellow_clients = []

    try:
        while True:
            data = receive_from_server(window, client_socket)
            if data == MessagePrefix.DISCONNECT.value:
                break
            data = data.split(SEPARATOR)
            fellow_client_address = ""
            fellow_client_key = ""
            for i in range(0, len(data), 2):
                if data[i] == MessagePrefix.CONNECTION.value:
                    fellow_client_address = data[i + 1]
                elif data[i] == MessagePrefix.KEY.value:
                    fellow_client_key = data[i + 1]
                if fellow_client_address != "" and fellow_client_key != "":
                    msg = "A client has successfully connected to the server! \n" + "Address:\t" + str(
                        fellow_client_address)
                    status_textbox.insert(msg, TextColor.CONNECTION)
                    msg = "key: " + fellow_client_key
                    status_textbox.insert(msg, TextColor.KEY)
                    fellow_clients.append(Client(fellow_client_address, public_key=fellow_client_key))
                    fellow_client_address = ""
                    fellow_client_key = ""
    except Exception as e:
        print("client failed to receive data: " + str(e))


def send_key(sock, public_key):
    sock.send(public_key.encode())


# checks if the server has closed and if so shuts down the client
# @returns data from the client
def receive_from_server(window, client_socket):
    data = client_socket.recv(2048).decode()
    if data == "":
        shutdown_client(window, client_socket)
    return data


# closes the client and notifies the server
def shutdown_client(window, client_socket):
    try:
        client_socket.send(MessagePrefix.DISCONNECT.value.encode())
    except Exception as e:
        print("Attempted to notify server of client shutdown.\n" + str(e))
    print("Client successfully closed!")
    window.destroy()
