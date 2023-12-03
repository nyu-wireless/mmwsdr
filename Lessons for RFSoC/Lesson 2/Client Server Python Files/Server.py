import socket
import threading
from queue import Queue
import pickle as pk
import sys
import time
import json
from pynq import allocate, Overlay

ol = Overlay('dma_test.bit')

HOST = '192.168.3.1'  # TRFSoC hostname or IP address
PORT = 9133 #The port used by the server
TR_PORT = 9035

class Compute_instance(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.count = 0
        self.host = host
        self.host_port = port
        
        self.header_size = 1024
        self.disconnect_msg = "!DISCONNECT"
        self.recved_msg = str()
        self.continue_ = True
        
    def connect(self):
        print("Start")
        self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_socket.bind((self.host, self.host_port))
        print("Waiting for Connection...")
        self.message_socket.listen()
        conn, addr = self.message_socket.accept()
        print("New Connetion Accepted")
        conn.send(str(TR_PORT).encode("utf-8"))
        self.recv_msg(conn)
        if (self.recved_msg.decode("utf-8")==self.disconnect_msg):
            conn.close()
            self.message_socket.close()
        
    def send_msg(self,message,conn,byt):
        self.header = str(len(message)).encode("utf-8")
        self.header += b' '*(self.header_size - len(self.header))
        
        conn.send(self.header)
        if (byt):
            conn.send(message)
        else:
            conn.send(message.encode("utf-8"))

    def recv_msg(self,conn):      
        self.recved_msg = b""
        self.header = int(conn.recv(self.header_size))
        
        header_init_size = self.header
        while self.header>0:
            self.recved_msg += conn.recv(self.header)
            self.header = header_init_size - len(self.recved_msg)
        return header_init_size
            
    def data_transceive(self):
        print("Transceive Thread Running...")
        self.message_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_socket2.bind((self.host, TR_PORT))
        self.message_socket2.listen()
        conn, addr = self.message_socket2.accept()
        start = time.time()
        list_msg = list()
        
        data_size = self.recv_msg(conn)
        print("Successfully received data from host")
        print(f"Length of received data: {len(self.recved_msg)}")
        list_msg =pk.loads(self.recved_msg)
        self.message_socket2.close()
        
        end = time.time()
        print(f"Total time is to transfer from host: {end-start}seconds")
        data_size = 1000
        
        self.input_mem = allocate(shape=(data_size,1),dtype=np.int32)
        self.output_mem = allocate(shape=(data_size,1),dtype=np.int32)
        
        self.input_mem = np.int32(np.real(list_msg[i]))
        
        ol.axi_dma_0.sendchannel.transfer(self.input_mem)
        print("Data sent from PS to PL")
        ol.axi_dma_0.recvchannel.transfer(self.output_mem)
        print(f"Output {type(np.array(self.output_mem))}")
        #f= open('reflected_samples.txt','wb')
        print("Data received from PL to PS")
        reflected_samples = self.output_mem#np.array(list())
       
        reflected_samples_byt = pk.dumps(reflected_samples)
         
        self.send_msg(reflected_samples_byt,conn,True)
        print("Samples have been sent back to Host")
       

    def run(self):
        #while True:
            try:
                Thread_connect =threading.Thread(target=self.connect())
                Thread_connect.start()                    
                Thread_transceive = threading.Thread(target = self.data_transceive())
                Thread_transceive.start()
                
                self.message_socket.close()
                #self.message_socket2.close()
            except Exception as e:
                print(e)
                self.message_socket.close()
                self.message_socket2.close()
 

if __name__ == '__main__':
    Msg = Compute_instance(HOST, PORT)
    Msg.start()
    Msg.join()
