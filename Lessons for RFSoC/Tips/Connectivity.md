Enable network connectivity on the RFSoC through an Ethernet cable connected to your host computer

On RFSoC board:
```
sudo route add default gw 192.168.2.1 dev eth0
sudo ip route add 0.0.0.0/0 dev eth0
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
sudo resolvectl dns eth0 8.8.8.8
```


On the workstation (note that, in this example, _enp02s0_ is the interface connected to the internet, whereas _enp0s31f6_ is the interface connected to the RFSoC):
```
sudo ufw disable
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
sudo ip route add 0.0.0.0/0 dev enp02s0
sudo iptables -t nat -A POSTROUTING -o enp02s0 -s 192.168.2.0/24 -j MASQUERADE
sudo systemctl restart NetworkManager
sudo ip address add 192.168.2.1/24 dev enp0s31f6
```

