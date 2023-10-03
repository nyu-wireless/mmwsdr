import socket
import threading
from queue import Queue
from datetime import datetime

message_buffer = Queue(maxsize=0)

class Messaging(threading.Thread):
    def __init__(self, queue, remote_ip=None, remote_port=None):
        super().__init__()
        self.q = queue
        self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.remote_ip = '192.168.3.1'
        self.remote_port = 9000
        #self.message_sock.bind(("127.0.0.1", 9000))

    def __unwrap(self, message):
        print(message)

    def read_file(self):
        # Open the file for reading
        with open('your_file.txt', 'r') as file:
        # Loop through each line in the file
            for line in file:
        # Process the line as needed
                print(line.strip())  # This will print each line without the newline character

    def run(self):
        self.message_socket.connect((self.remote_ip,self.remote_port))
        self.message_socket.send("hello".encode("utf-8"))
        while True:
                if (not(self.q.empty())):
                    with open('your_file.txt', 'r') as file:
                        for line in file:
                            self.message_socket.sendall(line.encode("utf-8"))
                    message = self.q.get()
                    self.message_socket.sendall(message.encode("utf-8"))
                else:
                    incoming_msg = self.message_socket.recv(4096)
                    #self.__unwrap(incoming_msg)
                    print(incoming_msg)

    

if __name__ == '__main__':
    Msg = Messaging(message_buffer)
    Msg.start()
    Msg.join()
