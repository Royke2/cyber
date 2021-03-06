import socket
import tkinter as tki
from tkinter import filedialog
from scrolled_status_text import *
from threading import Thread
from time import sleep
from data_convetions import *
import os
import util
import pathlib

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# This class includes a string version of the servers symmetrical_key. Used in order to pass the key between methods.
class SymmetricalKey:
    def __init__(self, symmetrical_key=""):
        self.symmetrical_key = symmetrical_key


def start_client(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("Client")
    new_window.geometry("500x750")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Sets a buffer size for the socket
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)

    # TODO: fix
    socket.getaddrinfo('localhost', 8080)

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)
    print("ip: " + ip)
    print("port: " + str(port))

    status_textbox = ScrolledStatusText(new_window, height='20', width='100', wrap=tki.WORD)
    status_textbox.insert("connecting to server please wait...", TextColor.MESSAGE)
    status_textbox.pack()

    # File uploader GUI
    file_explorer_lbl = tki.Label(new_window,
                                  text="File Explorer:",
                                  width=100, height=4,
                                  fg="blue")
    file_explorer_lbl.pack()

    send_btn = tki.Button(new_window, text="Waiting for key from server",
                          command=lambda: None,
                          state=tki.DISABLED)

    explore_files_btn = tki.Button(new_window,
                                   text="Browse Files",
                                   command=lambda: browse_files(file_explorer_lbl, send_btn))
    explore_files_btn.pack()

    send_btn.pack()

    # File downloader GUI
    destination_folder_explorer_lbl = tki.Label(new_window,
                                                text="Destination Folder Explorer:",
                                                width=100, height=4,
                                                fg="blue")
    destination_folder_explorer_lbl.pack()

    default_save_text = "Waiting for destination folder and file to download"

    save_btn = tki.Button(new_window, text=default_save_text,
                          command=lambda: None,
                          state=tki.DISABLED)

    explore_destination_folder_btn = tki.Button(new_window,
                                                text="Browse folders",
                                                command=lambda: browse_folders(
                                                    destination_folder_explorer_lbl, save_btn, default_save_text))

    explore_destination_folder_btn.pack()

    save_btn.pack()

    connection_thread = Thread(
        target=lambda: attempt_connection(new_window, client_socket, ip, port, status_textbox, send_btn,
                                          file_explorer_lbl, save_btn, destination_folder_explorer_lbl,
                                          default_save_text))

    shutdown_btn = tki.Button(new_window,
                              text="Exit",
                              command=lambda: shutdown_client(new_window, client_socket))
    shutdown_btn.pack()
    # if the window is manually closed the client is closed
    new_window.protocol("WM_DELETE_WINDOW",
                        lambda: shutdown_client(new_window, client_socket))

    connection_thread.start()


# Adds a file explorer in order to choose the file to upload.
def browse_files(file_explorer_lbl, send_btn):
    file_name = filedialog.askopenfilename(initialdir="/",
                                           title="Select a File",
                                           filetypes=(("Text files",
                                                       "*.txt*"),
                                                      ("all files",
                                                       "*.*")))

    # Change label contents
    if file_name != "":
        file_explorer_lbl.configure(text=file_name)
        send_btn["state"] = tki.NORMAL


# Adds a folder explorer in order to choose the folder to download to.
def browse_folders(destination_folder_explorer_lbl, save_btn, default_save_text):
    folder_name = filedialog.askdirectory(initialdir="/",
                                          title="Select a Folder")

    # Change label contents
    if folder_name != "":
        destination_folder_explorer_lbl.configure(text=folder_name)
        # If client has received a file the button can be used else it waits for file.
        if save_btn["text"] != default_save_text:
            save_btn['text'] = "save"
            save_btn["state"] = tki.NORMAL
        else:
            save_btn["text"] = "Waiting for destination"


# attempts to connect to the server in an incrementing loop till it succeeds
def attempt_connection(window, client_socket, ip, port, status_textbox, send_btn, file_explorer_lbl, save_btn,
                       destination_folder_explorer_lbl, default_save_text):
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
            client_connected(window, client_socket, status_textbox, send_btn, file_explorer_lbl, save_btn,
                             destination_folder_explorer_lbl, default_save_text)


# run when the client has successfully connected to the server
def client_connected(window, client_socket, status_textbox, send_btn, file_explorer_lbl, save_btn,
                     destination_folder_explorer_lbl, default_save_text):
    status_textbox.insert("The client has successfully connected to the server!", TextColor.CONNECTION)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=BUFFER_SIZE,
        backend=default_backend()
    )
    print("pry: " + str(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    ))

    public_key = private_key.public_key()
    # serializing the key in order to be able to send the key to the server
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                  format=serialization.PublicFormat.SubjectPublicKeyInfo)
    print("Client: public key:" + str(pem))
    client_socket.send(pem)

    print("client: sent key to server.")
    symmetrical_key = SymmetricalKey()
    try:
        while True:
            data = receive_from_server(window, client_socket)
            if data == MessagePrefix.DISCONNECT.value:
                break
            data = data.split(SEPARATOR)
            if data[0] == MessagePrefix.KEY.value:
                receive_key(client_socket, private_key, send_btn, status_textbox, file_explorer_lbl, symmetrical_key)
            if data[0] == MessagePrefix.CONNECTION.value:
                receive_connection(data, status_textbox)
            if data[0] == MessagePrefix.FILE_NAME.value:
                receive_file(data, client_socket, status_textbox, save_btn, destination_folder_explorer_lbl,
                             default_save_text, symmetrical_key)

    except Exception as e:
        print("client failed to receive data: " + str(e))


def receive_connection(data, status_textbox):
    for i in range(0, len(data), 2):
        if data[i] == MessagePrefix.CONNECTION.value:
            fellow_client_address = data[i + 1]
        if fellow_client_address != "":
            msg = "A client has successfully connected to the server! \n" + "Address:\t" + str(
                fellow_client_address)
            status_textbox.insert(msg, TextColor.CONNECTION)
            fellow_client_address = ""


def receive_key(client_socket, private_key, send_btn, status_textbox, file_explorer_lbl, symmetrical_key):
    key = client_socket.recv(BUFFER_SIZE)
    pad = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
    key = private_key.decrypt(key, pad)
    symmetrical_key.symmetrical_key = key
    send_btn['command'] = lambda: send_file(client_socket, file_explorer_lbl, status_textbox,
                                            Fernet(key))
    send_btn['text'] = "send"


def receive_file(data, client_socket, status_textbox, save_btn, destination_folder_explorer_lbl, default_save_text,
                 symmetrical_key):
    file = util.get_file(data, client_socket)
    if len(file) == 0:
        status_textbox.insert(
            "File not fully received!  desired: " + str(int(data[3])) + "received: " + str(len(file)),
            TextColor.FAILURE.value)
    else:
        status_textbox.insert("Received file from server!",
                              TextColor.MESSAGE.value)
        save_btn['command'] = lambda: save_file(file, data[1], destination_folder_explorer_lbl, status_textbox,
                                                Fernet(symmetrical_key.symmetrical_key))
        if save_btn['text'] == default_save_text:
            save_btn['text'] = "Waiting for save location"
        else:
            save_btn['text'] = "save"
            save_btn['state'] = tki.NORMAL


def save_file(file, file_name, destination_folder_explorer_lbl, status_textbox, symmetrical_key):
    with open(destination_folder_explorer_lbl['text'] + "/" + "(encrypted) " + file_name, "wb+") as f:
        # Write bytes to file
        f.write(file)
    file = symmetrical_key.decrypt(file)
    with open(destination_folder_explorer_lbl['text'] + "/" + file_name, "wb+") as f:
        # Write bytes to file
        f.write(file)
    status_textbox.insert("File saved", TextColor.MESSAGE.value)


# Sends a different encrypted file to each client connected to the server.
def send_file(sock, file_explorer_lbl, status_textbox, symmetrical_key):
    # if len() == 0:
    #     status_textbox.insert("No clients connected", TextColor.FAILURE)

    # Checks if a file is selected.
    if file_explorer_lbl["text"] != "":
        file_size = os.stat(file_explorer_lbl["text"]).st_size != 0
        # Checks if file isn't empty.
        if file_size != 0:
            with open(file_explorer_lbl["text"], "rb") as f:
                file = f.read()
                encrypted_file = symmetrical_key.encrypt(file)
                file_name = pathlib.PurePosixPath(file_explorer_lbl["text"]).name
                file_size = len(encrypted_file)
                opening_message = (
                        MessagePrefix.FILE_NAME.value + SEPARATOR + file_name + SEPARATOR
                        + MessagePrefix.FILE_SIZE.value + SEPARATOR + str(file_size) + SEPARATOR)
                sock.send(opening_message.encode())
                for i in range(0, file_size, BUFFER_SIZE):
                    bytes_read = encrypted_file[i:i + BUFFER_SIZE]
                    # we use sendall to assure transmission in busy networks
                    sock.sendall(bytes_read)
                status_textbox.insert("Sent file to server", TextColor.MESSAGE_SENT.value)
    else:
        status_textbox.insert("File is empty", TextColor.FAILURE)


# checks if the server has closed and if so shuts down the client
# @returns data from the client
def receive_from_server(window, client_socket):
    data = client_socket.recv(BUFFER_SIZE).decode()
    if data == MessagePrefix.DISCONNECT:
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
