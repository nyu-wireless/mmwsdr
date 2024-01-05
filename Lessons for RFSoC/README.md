### Structure of the course

- Lesson 1: Loading an image and setting up the RFSoC
- Lesson 2: Setting up a TCP connection between the host computer (Client) and RFSoC (Server)
- Lesson 3: Installing VIVADO
- Lesson 4: Basic Vivado and Pynq tutorials

### Other Educational material 
[Here](https://xilinx.github.io/RFSoC2x2-PYNQ/educational_resources.html) you can find a lot more educational material to support the Zynq RFSoC and the RFSoC2x2. This content has been developed by the University of Strathclyde in partnership with Xilinx. We recommend following these [RFSoC introductory notebooks](https://github.com/strath-sdr/rfsoc_notebooks). We encourage you to begin this class by covering these notebooks first. [Lesson 1](http://192.168.3.1:9090/lab/workspaces/auto-a/tree/rfsoc-notebooks/01_rfsoc_architecture_overview.ipynb) is particularly insightful to get you started. 


### Working with the RFSoC 2x2 remotely

The RFSoC 2x2 board is connected to a Workstation in Prof. Rangan's Wireless Lab at NYU. This machine can be accessed remotely using tools such as RealVCN or Screen Sharing (for MAC users) using the following credentials:
 
IP Address       : 172.24.113.58

RealVNC Password : nyu@1234

Login Password   : nyu@1234


### Enable internet connectivity on the RFSoC 2x2

Remember to enable internet connectivity on the board. Ideally, you use a USB-Ethernet adapter on the host machine. Otherwise, if you connect the board directly to the host computer through the Ethernet port, you should follow these steps. 
First of all, select "Shared to other computers" under the IPv4 method in the network setting of the selected interface. After doing that, if you type 

```
nmap -sn 10.42.0.0/24 | grep report
```

on the host computer, you should see two addresses: 10.42.0.1 (the host computer), and 10.42.0.x (the RFSoC -- probably x=123).  

Now, follow these steps (on the host computer): 


1) Enable IP forwarding
```
sudo nano /etc/sysctl.conf
```
Then, uncomment or add this line: 
```
net.ipv4.ip_forward=1
```
Save and exit the editor, then apply the changes: 
```
sudo sysctl -p
```

2) Configure DHCP
```
sudo apt-get install isc-dhcp-server
```
Edit the DHCP server configuration:
```
sudo nano /etc/dhcp/dhcpd.conf
```
Add the following lines: 
```
subnet 10.42.0.0 netmask 255.255.255.0 {
  range 10.42.0.2 10.42.0.100;
  option routers 10.42.0.1;
  option domain-name-servers 8.8.8.8, 8.8.4.4;
}
```
Save, exit, and start the DHCP server: 
```
sudo service isc-dhcp-server start
```

3) Configure Network Address Translation (NAT)
```
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```
Save the iptables rules
```
sudo sh -c "iptables-save > /etc/iptables.rules"
```
Edit network interface 
```
sudo nano /etc/network/interfaces
```
Add the following line at the end 
```
pre-up iptables-restore < /etc/iptables.rules
```
Reboot: 
```
sudo reboot 
```


