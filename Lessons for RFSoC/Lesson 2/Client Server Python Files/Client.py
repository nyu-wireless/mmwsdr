import socket
import threading
from queue import Queue
from datetime import datetime
import time
message_buffer = Queue(maxsize=0)

class Messaging(threading.Thread):
    def __init__(self, queue, remote_ip=None, remote_port=None):
        super().__init__()
        self.q = queue
        self.count = 0
        self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.remote_ip = "192.168.3.1"
        self.remote_port = 9027
        self.disconnect_msg = "!DISCONNECT"
        self.header_size = 64
        self.header = str()
        self.recved_msg = str()
        #self.message_sock.bind((self.remote_ip, self.remote_port))


    def __wrap(self, message):
        print(message)
    
    def send_msg(self,message,sock):
        self.header = str(len(message)).encode("utf-8")
        self.header += b' '*(self.header_size - len(self.header))
        sock.send(self.header)
        sock.sendall(message.encode("utf-8"))

    def recv_msg(self,sock):
        self.header = int(sock.recv(self.header_size).decode("utf-8"))
        self.recved_msg = sock.recv(self.header).decode("utf-8")

    def read_file(self):
        # Open the file for reading
        with open('your_file.txt', 'r') as file:
        # Loop through each line in the file
            for line in file:
        # Process the line as needed
                print(line.strip())  # This will print each line without the newline character
    
            

    def run(self):
        #Initial connection to thread whose port number is known
        
        self.message_socket.connect((self.remote_ip,self.remote_port))
        print("Start")
        self.remote_port = int(self.message_socket.recv(4).decode("utf-8"))
        print(f"The new thread port info is {self.remote_port}")
        self.send_msg(self.disconnect_msg,self.message_socket)
        #self.message_socket.send("hello".encode("utf-8"))

        #Connection to new thread that was formed upon request
        self.message_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
        #self.message_socket2.settimeout(1000)
        time.sleep(1)
        self.message_socket2.connect((self.remote_ip,self.remote_port))
        
        #Change Later
        while True:
                #if (not(self.q.empty())):
                try:
                    f= open('Test_samples_output.txt','w')
                    with open('Test_samples.txt', 'r') as file:
                        for line in file:
                            #print("Line size is")
                            #print(len(line))
                            #print(line)
                            self.count = self.count + 1
                            self.send_msg(line,self.message_socket2)
                            #print("Msg is sent")
                            self.recv_msg(self.message_socket2)
                            f.write(self.recved_msg)
                            #time.sleep(0.001)
                            #time.sleep(0.001)
                        self.send_msg("eof",self.message_socket2)
                        f.close()
                        
                        break
                except Exception as e:
                    print(e)
                    break
                        #write code to dump into new output file

                            #   if self.count == 100 : break
                #message = self.q.get()

                #self.message_socket.sendall(message.encode("utf-8"))
                # else:
                #     incoming_size = self.message_socket.recv(self.header_size).decode()
                #     incoming_msg = self.message_socket.recv(incoming_size)
                #     #self.__unwrap(incoming_msg)
                #     print(incoming_msg)

    

if __name__ == '__main__':
    Msg = Messaging(message_buffer)
    #Msg.q.put('xxxxx')
    #Msg.q.put('xxxxx')
    Msg.start()
    Msg.join()
   
