import socket
import tkinter as tki
from tkinter import filedialog


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

    # label_file_explorer.tki.grid(column = 1, row = 1)

    # button_explore.tki.grid(column = 1, row = 2)

    # button_exit.grid(column = 1,row = 3)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    # data = client_socket.recv( 1024 ).decode()
    # print( "Client sent: " + data)
    # client_socket.send(data.encode())


def browse_files(file_explorer_lbl):
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    # Change label contents
    file_explorer_lbl.configure(text="File Opened: " + filename)
