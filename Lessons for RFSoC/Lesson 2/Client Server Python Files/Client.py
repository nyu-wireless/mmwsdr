import socket
import threading
from queue import Queue
from datetime import datetime
import time
import sys
import math as m
 
class Messaging(threading.Thread):
    def __init__(self, remote_ip=None, remote_port=None):
        super().__init__()
        self.count = 0
        self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.remote_ip = "192.168.3.1"
        self.remote_port = 9133
        self.disconnect_msg = "!DISCONNECT"
        self.header_size = 1024
        self.header = str()
        self.recved_msg = str()
        

    
    def send_msg(self,message,sock,byt):
        self.header = str(len(message)).encode("utf-8")
        self.header += b' '*(self.header_size - len(self.header))
        
        sock.send(self.header)
        if (byt):
            sock.send(message)
        else:
            sock.send(message.encode("utf-8"))

    def recv_msg(self,sock):
        self.recved_msg = b""
        self.header = int(sock.recv(self.header_size))
        print(self.header)
        header_init_size = self.header
        while self.header>0:
            self.recved_msg += sock.recv(self.header)
            self.header = header_init_size - len(self.recved_msg)
           

    def run(self):
        #Initial connection to thread whose port number is known
        
        self.message_socket.connect((self.remote_ip,self.remote_port))
        print("Start")
        self.remote_port = int(self.message_socket.recv(4).decode("utf-8"))
        self.send_msg(self.disconnect_msg,self.message_socket,False)
       
        print("New port information received")
        #Connection to new thread that was formed upon request
        self.message_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
     
        time.sleep(1)
        self.message_socket2.connect((self.remote_ip,self.remote_port))
        
        
        while True:
               
                try:
                    f= open('Test_samples_output.txt','wb')
                    file =  open('Test_samples.txt', 'rb')
                    a = (file.read())
                    print(f"Size of file is {len(a)}")
                    self.send_msg(a,self.message_socket2,True)
                    print("Pickled file data has been sent to RFSoC")
                    print("Waiting to receive samples...")
                    self.recv_msg(self.message_socket2)
                    print("Successfully received samples from RFSoC")
                    f.write(self.recved_msg)
                    print("Samples have been written into the output file")
                  
                    f.close()
                    file.close()
                    break
                except Exception as e:
                    print(e)
                    break    

if __name__ == '__main__':
    Msg = Messaging()

    Msg.start()
    Msg.join()
   
