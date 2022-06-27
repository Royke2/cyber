import socket
import tkinter as tki


def start_client(ip, port, root):
    new_window = tki.Toplevel(root)

    new_window.title("Client")

    new_window.geometry("500x500")
