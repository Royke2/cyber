import socket
import tkinter as tki
from tkinter import filedialog

def openNewWindow(IP66, PORT66, root):
    newWindow = tki.Toplevel(root)

    newWindow.title("New Window")

    newWindow.geometry("500x500")
    IP = IP66.get("1.0", "end-1c")
    PORT2 = PORT66.get("1.0", 'end')
    PORT = int(PORT2)
    tki.Label(newWindow,
              text='CHAT').pack()

    def browseFiles():
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                          "*.txt*"),
                                                         ("all files",
                                                          "*.*")))

        # Change label contents
        label_file_explorer.configure(text="File Opened: " + filename)

    label_file_explorer = tki.Label(newWindow,
                                    text="File Explorer using Tkinter",
                                    width=100, height=4,
                                    fg="blue")
    label_file_explorer.pack()
    button_explore = tki.Button(newWindow,
                                text="Browse Files",
                                command=browseFiles)
    button_explore.pack()
    button_exit = tki.Button(newWindow,
                             text="Exit",
                             command=exit)
    button_exit.pack()
    # label_file_explorer.tki.grid(column = 1, row = 1)

    # button_explore.tki.grid(column = 1, row = 2)

    # button_exit.grid(column = 1,row = 3)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    # data = client_socket.recv( 1024 ).decode()
    # print( "Client sent: " + data)
    # client_socket.send(data.encode())