import socket
import threading
from queue import Queue

HOST = '192.168.3.1'  # TRFSoC hostname or IP address
PORT = 9002# The port used by the server
message_buffer = Queue(maxsize=0)
class Compute_instance(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        #self.q = message_buffer
        self.host = host
        self.host_port = port
        
        self.header_size =64
        self.disconnect_msg = "!DISCONNECT"
        self.recved_msg = str()
        self.continue_ = True
        
    def initiate(self):
        while(True):
            print("Start")
            self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.message_socket.bind((self.host, self.host_port))
            print("First Conn")
            self.message_socket.listen()
            conn, addr = self.message_socket.accept()
            conn.send("9100".encode("utf-8"))
            self.recv_msg(conn)
            if (self.recved_msg==self.disconnect_msg):
                print("Conn 1 close")
                conn.close()

    def send_msg(self,message,conn):
        self.header = str(len(message)).encode("utf-8")
        self.header += b' '*(self.header_size - len(message))
        conn.send(self.header)
        conn.sendall(message.encode("utf-8"))

    def recv_msg(self,conn):
        #print((conn.recv(self.header_size).decode("utf-8")))
        self.header = int((conn.recv(self.header_size).decode("utf-8")))
        self.recved_msg = conn.recv(self.header).decode("utf-8")
        print(self.header)
        #print(self.recved_msg)
    def data_transceive(self):
        print("Trasceive ident is"+str(threading.get_ident))
        print("In transceive")
        self.message_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_socket2.bind((self.host, 9100))
        #self.message_socket2.settimeout(1000)
        self.message_socket2.listen()
        conn, addr = self.message_socket2.accept()
        while(self.continue_):
            self.recv_msg(conn)
            
            #self._unwrap(self.recved_msg)
            #__unwarp(self.recved_msg)
            if self.recved_msg == 'eof':
                self.message_socket2.close()
                print("Samples fully processed")
                break
            #Insert unwrapping method
            #Insert code for ADC and DAC interaction
            #Currently the data is being looped back into the client
            self.send_msg(self.recved_msg,conn)

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
            for j in range(int((len(words)-1)/2)):
                i.append(words[2*j+1])
                q.append(words[2*j+2])
                #(i,q) = words[2*i+1:2*i+2]
                
            print(f"I = {i} | \n\n Q = {q}")
        elif(words[0] == 'eof'):
            
            self.continue_ = False
        else:
            print(f"Other : {words}")
        

    def run(self):
        
        try:
            Thread_initiate = threading.Thread(name = "initiate",target = self.initiate())
            Thread_initiate.start()
            Thread_transceive = threading.Thread(name = "transceive",target = self.data_transceive())
            Thread_transceive.start()
            print("Its done")
        except Exception as e:
            print("The error is_____________")
            print(e)
            self.message_socket.close()
            #self.message_socket2.close()
            
        #finally:
            #self.message_socketPORT.close()

if __name__ == '__main__':
    #Msg = Compute_instance(message_buffer, HOST, PORT)
    Msg = Compute_instance( HOST, PORT)
    Msg.start()
    Msg.join()

