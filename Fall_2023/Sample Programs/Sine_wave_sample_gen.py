from fixed_to_u32 import fxp_2_hex
import math
#import socket
duration =  3
Fs = 10**6
freq = 70000
t = duration*Fs

signal = str()
yi = str()
yq = str()
#add = '192.168.3.100'
#port = 9093
#ssock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#ssock.bind((add,port))
#ssock.listen(5)
#csock,cadd = ssock.accept()

f= open('Test_samples.txt','w')
f.write("#|")
for i in range(t):
    yi = math.cos(2*math.pi*70000*i/10**6)
    yq = math.cos(2*math.pi*freq*i/Fs+math.pi/2)
    I,Q= fxp_2_hex(yi,yq)
    signal = I+"|"+Q+"|"
    f.write(signal)
f.close
#ssock.close()
#csock.close()
