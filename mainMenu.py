import socket
import tkinter as tki
from server import openNewWindow

root = tki.Tk()
root.geometry("300x300")
T = 'CHAT'
label = tki.Label(root, height=2, width=50,
                  text='DO YOU WANT TO CHAT?')
label.pack(pady=10)


def clear_frame():
    for widgets in root.winfo_children():
        widgets.destroy()

    PORTnIPin()


printButton = tki.Button(root,
                         text="yes",
                         command=lambda:
                         clear_frame())
printButton.pack()


def know_ip():
    server = socket.socket()

    ip1 = socket.gethostbyname(socket.gethostname())
    return ip1


def putIN():
    ip1 = know_ip()
    Output3 = tki.Text(root, height=1,
                       width=30,
                       bg="yellow")
    Output3.insert(tki.END, str(ip1))
    Output3.pack(pady=5)


def PORTnIPin():
    Output = tki.Text(root, height=1,
                      width=30,
                      bg="blue")
    Output.insert(tki.END, 'PLEASE PUT YOUR IP INFO:')
    Output.pack(pady=5)
    IP5 = tki.Text(root, height=1, width=15)
    IP5.pack(pady=5)
    Output1 = tki.Text(root, height=1,
                       width=30,
                       bg="blue")
    Output1.insert(tki.END, 'PLEASE PUT YOUR PORT INFO:')
    Output1.pack(pady=5)
    PORT1 = tki.Text(root, height=1, width=15)
    PORT1.pack(pady=5)
    Output2 = tki.Text(root, height=1,
                       width=30,
                       bg="blue")
    Output2.insert(tki.END, 'DO YOU WANT TO KNOW YOUR IP?')
    Output2.pack(pady=5)
    printButton1 = tki.Button(root,
                              text="yes",
                              command=lambda:
                              putIN())
    printButton1.pack()
    Output4 = tki.Text(root, height=1,
                       width=30,
                       bg="red")
    Output4.insert(tki.END, 'DONE?')
    Output4.pack(pady=5)
    printButton2 = tki.Button(root,
                              text="yes",
                              command=lambda:
                              openNewWindow(IP5, PORT1, root))
    printButton2.pack()


root.mainloop()