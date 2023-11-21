from fixed_to_u32 import fxp_2_hex
import math
import pickle as pk
import numpy as np
import sys
#import socket
duration = 0.01
Fs = 10**6
freq = 70000
t = duration*Fs
print(t)
signal = str()
yi = str()
yq = str()
#add = '192.168.3.100'
#port = 9093
#ssock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#ssock.bind((add,port))
#ssock.listen(5)
#csock,cadd = ssock.accept()
linesize = 32
f= open('Test_samples.txt','w')
count = 0
samps = []
for i in range(int(t)):
    count +=1
    yi = int(math.cos(2*math.pi*70000*i/10**6)*2**13)
    yq = int(math.cos(2*math.pi*freq*i/Fs+math.pi/2)*2**13)
    samps = np.append(samps,yi+1j*yq)
    
    #temp = yi<<18
    #temp += yq<<2
    #samps = np.append(samps,bin(temp))
    
    if count%linesize==0:
        samps = pk.dumps(samps)
        #print(len(str((samps))))
        f.write(str(samps))
        f.write("\n")
        samps = []

f.write("a")
    
    
f.close
#ssock.close()
#csock.close()
