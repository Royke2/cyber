import socket
import tkinter as tki
from tkinter import filedialog
import threading
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def start_server(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("500x500")

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)

    tki.Label(new_window,
              text='CHAT').pack()

    file_explorer_lbl = tki.Label(new_window,
                                  text="File Explorer:",
                                  width=100, height=4,
                                  fg="blue")
    file_explorer_lbl.pack()

    explore_files_btn = tki.Button(new_window,
                                   text="Browse Files",
                                   command=lambda: browse_files(file_explorer_lbl))
    explore_files_btn.pack()

    exit_btn = tki.Button(new_window,
                          text="Exit",
                          command=exit)
    exit_btn.pack()

    connection_status_lbl = tki.Label(new_window, text="Connection Status: no client connected", fg="red")
    connection_status_lbl.pack()

    # label_file_explorer.tki.grid(column = 1, row = 1)

    # button_explore.tki.grid(column = 1, row = 2)

    # button_exit.grid(column = 1,row = 3)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    print("Server is up and running")

    # We separate the connecting and reciving phase from the rest of the code in order to not interrupt the tkinter
    # main thread.
    connection_thread = threading.Thread(target=lambda: connect(new_window, server_socket, connection_status_lbl))
    connection_thread.start()


# Waits for a client to connect and receives the public key from the client.
def connect(new_window, server_socket, connection_status_lbl):
    print("attempting to connect to client")
    (client_socket, client_address) = server_socket.accept()

    connection_status_lbl['text'] = "Connection Status: " + str(client_address) + " connected!"
    connection_status_lbl["fg"] = "green"

    print("Client connected")

    key_status_lbl = tki.Label(new_window, text="Public key status: not received! ", fg="red")
    key_status_lbl.pack()

    public_key = load_pem_public_key(client_socket.recv(2048))

    key_status_lbl['text'] = "Key Status: " + str(public_key) + " received!"
    key_status_lbl["fg"] = "green"

    print("Public key received")


# Adds a file explorer in order to choose the file to upload.
def browse_files(file_explorer_lbl):
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    # Change label contents
    file_explorer_lbl.configure(text="File Opened: " + filename)
