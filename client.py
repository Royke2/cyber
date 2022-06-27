import socket
import tkinter as tki


def start_client(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("Client")
    new_window.geometry("500x500")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)
    tki.Label(new_window,
              text='connecting to server please wait...').pack()
    sock.connect((ip, port))
    