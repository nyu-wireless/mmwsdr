import socket
import threading
from queue import Queue

HOST = "127.0.0.1"  # TRFSoC hostname or IP address
PORT = 9000  # The port used by the server
message_buffer = Queue(maxsize=0)

class Messaging(threading.Thread):
    def __init__(self, message_buffer, host, port):
        super().__init__()
        self.q = message_buffer
        self.host = host
        self.host_port = port
        self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_socket.bind((self.host, self.host_port))

    def __unwrap(self, message):
        print(message)
        words = message.split("|")
        if words[0] == 'info':
            [freq, bandwidth, sampling_rate] = words[1:-1]
            print(f"Freq:{freq}MHz | Bandwidth: {bandwidth}MHz | Sampling rate: {sampling_rate} ")
        elif(words[0] == '#'):
            (i,q) = words[1:-1]
            print(f"I = {i} | Q = {q}")
        else:
            print(f"Other : {words}")
            

    def run(self):
        self.message_socket.listen()
        conn, addr = self.message_socket.accept()
        with conn:
            while True:
                if not self.q.empty():
                    message = self.q.get()
                    conn.sendall(message.encode("utf-8"))
                else:
                    incoming_msg = conn.recv(4096)
                    self.__unwrap(incoming_msg)
                    print(incoming_msg)

if __name__ == '__main__':
    Msg = Messaging( message_buffer, HOST, PORT)
    Msg.start()
    Msg.join()
