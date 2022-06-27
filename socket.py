import socket
import tkinter as tki
from tkinter import filedialog
root = tki.Tk()
root.geometry("300x300")
T = 'CHAT'
label = tki.Label(root, height = 2, width = 50,
              text = 'DO YOU WANT TO CHAT?')
label.pack(pady = 10)

def openNewWindow(IP66,PORT66):
                
                newWindow = tki.Toplevel(root)
 
                newWindow.title("New Window")
 
                newWindow.geometry("500x500")
                IP = IP66.get("1.0", "end-1c")
                PORT2 = PORT66.get("1.0", 'end')
                PORT = int(PORT2)
                tki.Label(newWindow,
                        text = 'CHAT').pack()
                def browseFiles():
                    filename = filedialog.askopenfilename(initialdir = "/",
                                                          title = "Select a File",
                                                          filetypes = (("Text files",
                                                                        "*.txt*"),
                                                                       ("all files",
                                                                        "*.*")))
                      
                    # Change label contents
                    label_file_explorer.configure(text="File Opened: "+filename)

                label_file_explorer = tki.Label(newWindow,
                            text = "File Explorer using Tkinter",
                            width = 100, height = 4,
                            fg = "blue")
                label_file_explorer.pack()
                button_explore = tki.Button(newWindow,
                        text = "Browse Files",
                        command = browseFiles)
                button_explore.pack()
                button_exit = tki.Button(newWindow,
                                     text = "Exit",
                                     command = exit)
                button_exit.pack()
                #label_file_explorer.tki.grid(column = 1, row = 1)
  
                #button_explore.tki.grid(column = 1, row = 2)
  
                #button_exit.grid(column = 1,row = 3)
                
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind((IP, PORT))
                server_socket.listen()
                print( "Server is up and running" )
                (client_socket, client_address) = server_socket.accept()
                print( "Client connected" )
                #data = client_socket.recv( 1024 ).decode()
                #print( "Client sent: " + data)
                #client_socket.send(data.encode())

def clear_frame():
   for widgets in root.winfo_children():
      widgets.destroy()
      
   PORTnIPin()
printButton = tki.Button(root,
                        text = "yes", 
                        command = lambda:
                         clear_frame() )
printButton.pack()

def know_ip():
   server=socket.socket()

   ip1=socket.gethostbyname(socket.gethostname())
   return ip1
def putIN():
   ip1 = know_ip()
   Output3 = tki.Text(root, height = 1,
              width = 30,
              bg = "yellow")
   Output3.insert(tki.END, str(ip1))
   Output3.pack(pady = 5)
   
def PORTnIPin():
     Output = tki.Text(root, height = 1,
              width = 30,
              bg = "blue")
     Output.insert(tki.END, 'PLEASE PUT YOUR IP INFO:')
     Output.pack(pady = 5)
     IP5 = tki.Text(root, height = 1, width =15)
     IP5.pack(pady = 5)
     Output1 = tki.Text(root, height = 1 ,
              width = 30,
              bg = "blue")
     Output1.insert(tki.END, 'PLEASE PUT YOUR PORT INFO:')
     Output1.pack(pady = 5)
     PORT1 = tki.Text(root, height = 1, width =15)
     PORT1.pack(pady = 5)
     Output2 = tki.Text(root, height = 1,
              width = 30,
              bg = "blue")
     Output2.insert(tki.END, 'DO YOU WANT TO KNOW YOUR IP?')
     Output2.pack(pady = 5)
     printButton1 = tki.Button(root,
                        text = "yes", 
                        command = lambda:
                          putIN())
     printButton1.pack()
     Output4 = tki.Text(root, height = 1,
              width = 30,
              bg = "red")
     Output4.insert(tki.END, 'DONE?')
     Output4.pack(pady = 5)
     printButton2 = tki.Button(root,
                        text = "yes", 
                        command = lambda:
                          openNewWindow(IP5,PORT1))
     printButton2.pack()
     
    




root.mainloop()
