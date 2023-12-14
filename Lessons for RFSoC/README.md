### Structure of the course

- Lesson 1: Loading an image and setting up the RFSoC
- Lesson 2: Setting up a TCP connection between the host computer (Client) and RFSoC (Server)
- Lesson 3: Installing VIVADO
- Lesson 4: Basic Vivado and Pynq tutorials

  
### Working with the RFSoC 2x2 remotely

The RFSoC 2x2 board is connected to a Workstation in Prof. Rangan's Wireless Lab at NYU. This machine can be accessed remotely using tools such as RealVCN or Screen Sharing (for MAC users) using the following credentials:
 
IP Address       : 172.24.113.58

RealVNC Password : nyu@1234

Login Password   : nyu@1234

### Enable internet connectivity on the RFSoC 2x2

Remember to enable internet connectivity on the board by connecting it to the host computer over Ethernet, and by selecting "Shared to other computers" under the IPv4 method in the network setting of the selected interface. After doing that, if you type 

```
nmap -sn 10.42.0.0/24 | grep report
```

on the host computer, you should see two addresses: 10.42.0.1 (the host computer), and 10.42.0.x (the RFSoC).  

Now, follow these steps: 

1) Enable IP forwarding
```
sudo nano /etc/sysctl.conf
```


1) Enable IP forwarding
```
sudo nano /etc/sysctl.conf
```
Uncomment or add this line: 
```
net.ipv4.ip_forward=1
```



### Other Educational material 
[Here](https://xilinx.github.io/RFSoC2x2-PYNQ/educational_resources.html) we can find a lot more educational material to support the Zynq RFSoC and the RFSoC2x2. This content has been developed by the University of Strathclyde in partnership with Xilinx. We recommend to follow these [RFSoC introductory notebooks](https://github.com/strath-sdr/rfsoc_notebooks). 
