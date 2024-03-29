### Structure of the course

- Lesson 1: Loading an image and setting up the RFSoC
- Lesson 2: Setting up a TCP connection between the host computer (Client) and RFSoC (Server)
- Lesson 3: Installing VIVADO
- Lesson 4: Basic Vivado and Pynq tutorials
- Lesson 5: Writing logic in Vitis
  
### Other Educational material 
[Here](https://xilinx.github.io/RFSoC2x2-PYNQ/educational_resources.html) you can find a lot more educational material to support the Zynq RFSoC and the RFSoC2x2. This content has been developed by the University of Strathclyde in partnership with Xilinx. We recommend following these [RFSoC introductory notebooks](https://github.com/strath-sdr/rfsoc_notebooks). We encourage you to begin this class by covering these notebooks first. [Lesson 1](http://192.168.3.1:9090/lab/workspaces/auto-a/tree/rfsoc-notebooks/01_rfsoc_architecture_overview.ipynb) is particularly insightful to get you started. 


### Working with the RFSoC remotely

The RFSoC 2x2 board is connected to a Workstation in Prof. Rangan's Wireless Lab at NYU. This machine can be accessed remotely using tools such as RealVCN or Screen Sharing (for MAC users) using the following credentials:
 
IP Address       : 172.24.113.58

RealVNC Password : ask Prof. Rangan

Login Password   : ask Prof. Rangan


### Enable internet connectivity 

Enable network connectivity on the RFSoC through an Ethernet cable connected to your host computer

On the RFSoC board (open a terminal at http://192.168.3.1:9090/lab to get root access):

```
sudo route add default gw 192.168.2.1 dev eth0
sudo ip route add 0.0.0.0/0 dev eth0
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
sudo resolvectl dns eth0 8.8.8.8
```


On the workstation (note that, in this example, _enp2s0_ is the interface connected to the internet, whereas _enp0s31f6_ is the interface connected to the RFSoC):
```
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo ip route add 0.0.0.0/0 dev enp2s0
sudo iptables -t nat -A POSTROUTING -o enp02s0 -s 192.168.2.0/24 -j MASQUERADE
sudo systemctl restart NetworkManager
sudo ip address add 192.168.2.1/24 dev enp0s31f6
```

