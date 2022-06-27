import socket
import tkinter as tki
from server import start_server
from client import start_client

root = tki.Tk()
root.geometry("300x300")
T = 'CHAT'

opening_msg_txt = tki.Label(root, height=2, width=50,
                            text='DO YOU WANT TO EXCHANGE FILES?')
opening_msg_txt.pack(pady=10)

open_main_menu_btn = tki.Button(root,
                                text="yes",
                                command=lambda:
                                clear_frame())
open_main_menu_btn.pack()


def clear_frame():
    for widgets in root.winfo_children():
        widgets.destroy()

    main_menu()


def get_local_ip():
    server = socket.socket()

    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip


def show_local_ip():
    local_ip = get_local_ip()
    local_ip_txt = tki.Text(root, height=1,
                            width=30,
                            bg="yellow")
    local_ip_txt.insert(tki.END, str(local_ip))
    local_ip_txt.pack(pady=5)


def main_menu():
    ip_txt = tki.Text(root, height=1,
                      width=30,
                      bg="blue")
    ip_txt.insert(tki.END, 'PLEASE PUT YOUR IP INFO:')
    ip_txt.pack(pady=5)

    ip = tki.Text(root, height=1, width=15)
    ip.pack(pady=5)

    port_txt = tki.Text(root, height=1,
                        width=30,
                        bg="blue")
    port_txt.insert(tki.END, 'PLEASE PUT YOUR PORT INFO:')
    port_txt.pack(pady=5)

    port = tki.Text(root, height=1, width=15)
    port.pack(pady=5)

    local_ip_txt = tki.Text(root, height=1,
                            width=30,
                            bg="blue")
    local_ip_txt.insert(tki.END, 'DO YOU WANT TO KNOW YOUR IP?')
    local_ip_txt.pack(pady=5)

    local_ip_btn = tki.Button(root,
                              text="yes",
                              command=lambda:
                              show_local_ip())
    local_ip_btn.pack()

    confirmation_txt = tki.Text(root, height=1,
                                width=30,
                                bg="red")
    confirmation_txt.insert(tki.END, 'DONE?')
    confirmation_txt.pack(pady=5)

    start_server_btn = tki.Button(root,
                                  text="start server",
                                  command=lambda:
                                  start_server(ip, port, root))
    start_server_btn.pack()

    start_client_btn = tki.Button(root,
                                  text="start client",
                                  command=lambda:
                                  start_client(ip, port, root))
    start_client_btn.pack()


root.mainloop()
