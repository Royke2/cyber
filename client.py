import socket
import tkinter as tki
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def start_client(ip, port, root):
    new_window = tki.Toplevel(root)
    new_window.title("Client")
    new_window.geometry("500x500")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.getaddrinfo('localhost', 8080)

    ip = ip.get("1.0", "end-1c")
    port = port.get("1.0", 'end')
    port = int(port)
    print("ip: " + ip)
    print("port: " + str(port))
    connection_txt = tki.Label(new_window,
                               text='connecting to server please wait...')
    connection_txt.pack()
    root.update()

    connection_attempt_wait_time = 0
    root.after(connection_attempt_wait_time,
               lambda: attempt_connection(sock, ip, port, root, connection_txt, connection_attempt_wait_time))


# attempts to connect to the server in an incrementing loop till it succeeds
def attempt_connection(sock, ip, port, root, connection_txt, connection_attempt_wait_time):
    wait_time_increment = 2.5  # in seconds
    max_wait_time = 10  # in seconds

    try:
        sock.connect((ip, port))

    except Exception as e:
        # increases wait time each time due to the fact if it hasn't work up till then it most likely won't work
        # immediately, so the system conserves resources.
        if connection_attempt_wait_time < max_wait_time:
            connection_attempt_wait_time += wait_time_increment
        connection_txt['text'] = "connection refused trying in: " + str(
            connection_attempt_wait_time) + " seconds"
        print(str(e))
        print("connection refused trying in: " + str(connection_attempt_wait_time) + " seconds")
        root.after(int(connection_attempt_wait_time * 1000),
                   lambda: attempt_connection(sock, ip, port, root, connection_txt, connection_attempt_wait_time))

    else:
        client_connected(sock, root, connection_txt)


# run when the client has successfully connected to the server
def client_connected(sock, root, connection_txt):
    connection_txt['text'] = "the client has successfully connected to the server"
    connection_txt['fg'] = "green"

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    # serializing the key in order to be able to send the key to the server
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                  format=serialization.PublicFormat.SubjectPublicKeyInfo)
    sock.send(pem)

    print("client: sent key to server.")


def send_key(sock, public_key):
    sock.send(public_key.encode())
