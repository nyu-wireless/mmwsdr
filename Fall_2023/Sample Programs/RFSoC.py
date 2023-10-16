import socket
import threading
from queue import Queue

HOST = '192.168.3.1'  # TRFSoC hostname or IP address
PORT = 9093  # The port used by the server
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
        #print(message)
        words = message.split("|")
        words
        i = list()
        q = list()
        if words[0] == 'info':
            [freq, bandwidth, sampling_rate] = words[1:-1]
            print(f"Freq:{freq}MHz | Bandwidth: {bandwidth}MHz | Sampling rate: {sampling_rate} ")
        elif(words[0] == '#'):
            #The following for loop and its contents was changed from the single line code
            #(i,q) = words[1:-1]
            for j in range(int((len(words)-1)/2)):
                i.append(words[2*j+1])
                q.append(words[2*j+2])
                
                #(i,q) = words[2*i+1:2*i+2]
            print(f"I = {i} | \n\n Q = {q}")
        else:
            print(f"Other : {words}")
            

    def run(self):
        try:
            self.message_socket.listen()
            conn, addr = self.message_socket.accept()
            with conn:
                while True:
                    if not self.q.empty():
                        message = self.q.get()
                        conn.sendall(message.encode("utf-8"))
                    else:
                        incoming_msg = (conn.recv(4096)).decode()
                        self.__unwrap(incoming_msg)
                        #print(f"{incoming_msg} \n")
                        __unwrap(incoming_msg) #This line seems to be giving the error "name '_Messaging__unwrap' is not defined" but when removed the  
                                               #host program seems to freeze
                        print("That's the end of the message")
                        
        except Exception as e:
            print(e)
            self.message_socket.close()
        #finally:
            #self.message_socket.close()

if __name__ == '__main__':
    Msg = Messaging( message_buffer, HOST, PORT)
    Msg.start()
    Msg.join()
