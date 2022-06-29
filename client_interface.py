import socket
import tkinter as tki
from tkinter import filedialog
from scrolled_status_text import *

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

    shutdown_btn = tki.Button(new_window,
                              text="Exit",
                              command=lambda: shutdown_client(new_window, client_socket))
    shutdown_btn.pack()
    # if the window is manually closed the client is closed
    new_window.protocol("WM_DELETE_WINDOW", lambda: shutdown_client(new_window, client_socket))

    root.update()

    connection_attempt_wait_time = 0
    root.after(connection_attempt_wait_time,
               lambda: attempt_connection(client_socket, ip, port, root, status_textbox, connection_attempt_wait_time,
                                          shutdown_btn, new_window))


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
def attempt_connection(client_socket, ip, port, root, status_textbox, connection_attempt_wait_time, shutdown_btn,
                       new_window):
    wait_time_increment = 2.5  # in seconds
    max_wait_time = 10  # in seconds

    try:
        client_socket.connect((ip, port))
    except Exception as e:
        # increases wait time each time due to the fact if it hasn't work up till then it most likely won't work
        # immediately, so the system conserves resources.
        if connection_attempt_wait_time < max_wait_time:
            connection_attempt_wait_time += wait_time_increment
        status_textbox.insert("connection refused trying in: " + str(
            connection_attempt_wait_time) + " seconds", TextColor.MESSAGE)
        print(str(e))
        print("connection refused trying in: " + str(connection_attempt_wait_time) + " seconds")
        root.after(int(connection_attempt_wait_time * 1000),
                   lambda: attempt_connection(client_socket, ip, port, root, status_textbox,
                                              connection_attempt_wait_time, shutdown_btn, new_window))

    else:
        client_connected(client_socket, root, status_textbox, shutdown_btn, new_window)


# run when the client has successfully connected to the server
def client_connected(client_socket, root, status_textbox, shutdown_btn, new_window):
    status_textbox.insert("The client has successfully connected to the server!", TextColor.CONNECTION)

    shutdown_btn['command'] = lambda: shutdown_client(new_window, client_socket)
    new_window.protocol("WM_DELETE_WINDOW", lambda: shutdown_client(new_window, client_socket))

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


def send_key(sock, public_key):
    sock.send(public_key.encode())


# checks if the server has closed and if so shuts down the client
# @returns data from the client
def receive_from_server(window, client_socket, server_socket):
    data = server_socket.recv(2048).decode()
    if data == "":
        shutdown_client(window, client_socket)
    return data


# closes the client and notifies the server
def shutdown_client(window, client_socket):
    try:
        client_socket.send("".encode())
    except Exception as e:
        print("Attempted to notify server of client shutdown.\n" + str(e))
    client_socket.close()
    print("Client successfully closed!")
    window.destroy()
