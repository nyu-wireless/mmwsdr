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

