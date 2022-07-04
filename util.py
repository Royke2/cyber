import math
from data_convetions import BUFFER_SIZE


# @param data The data sent that includes the file name prefix at the start and then file size.
# @param sending_socket The socket sending the file.
# Returns a byte array containing a file sent in parts from a given socket.
def get_file(data, sending_socket):
    file_size = int(data[3])
    read_count = math.ceil(file_size / BUFFER_SIZE)
    # There is a bug that merges the file size and the first part of the file. This should handle this issue
    file = data[4].encode()
    for i in range(read_count):
        file += sending_socket.recv(BUFFER_SIZE)
    return file
