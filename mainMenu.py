import socket
import tkinter as tki
from server import openNewWindow

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


def know_ip():
    server = socket.socket()

    ip1 = socket.gethostbyname(socket.gethostname())
    return ip1


def show_local_ip():
    ip1 = know_ip()
    Output3 = tki.Text(root, height=1,
                       width=30,
                       bg="yellow")
    Output3.insert(tki.END, str(ip1))
    Output3.pack(pady=5)


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

    start_server = tki.Button(root,
                              text="yes",
                              command=lambda:
                              openNewWindow(ip, port, root))
    start_server.pack()


root.mainloop()
