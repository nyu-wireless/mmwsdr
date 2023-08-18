Instructions to build, set up and run the 60 GHz Channel Sounder developed by Notis. 

# Table of Contents  

[1. Build](#1-build-the-testbed)

[2. Program](#2-program-the-testbed)

[3. Run](#3-run-the-testbed)

## 1. Build the testbed

Carefully follow each step described in the HW_setup.pdf document. You will learn how to connect the Sivers arrays (TX and RX) to the RFSoC 2x2 boards through the Broadband balun model Merkei BAL0006. 

## 2. Program the testbed

## 2.1. Download the rx.img

It is preferable to use google chrome. Other browsers might have a problem with big files. Click [here](https://drive.google.com/file/d/1YfHpmMC5HQftU6drCumDuZgqWMh2dPdv/view?usp=drive_link).

> Burn the rx.img to both SD Cards

In Linux we can do the following. Insert the SD card in the computer [Somehow it did not work well, make sure to check the DONE LEDs on RFSoC turns to green]

```
sudo fdisk -l
```


Disk /dev/sdd: 14.84 GiB, 15931539456 bytes, 31116288 sectors
Disk model: USB3.0 CRW   -SD
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xbc7f45e1

$ sudo dd if=~/Downloads/rx.img of=/dev/sdd 

In Windows, I think that we can use Rufus (https://rufus.ie/en/)

In MAC, flashing can be done with terminal comments

More information can be found at https://pynq.readthedocs.io/en/latest/appendix/sdcard.html

> Change the ip address of the Tx to 10.1.1.40 
The image will have a static ip address of 10.1.1.30. Therefore, we need to change at least one of the nodes. 
To change the static ip address we need to follow these steps:
 1) Insert the SD card to a computer. This should appear as two filesystems (PYNQ and root)
 2) Open the root file system
 3) Edit the /etc/network/interfaces.d/eth0 and modify the address
 4) Safely unmount the drive

> Connect the switch to the computer with a cable, then set a static IP address of the desktop/laptop:
IP 10.1.1.100, netmask 255.255.255.0
Command (for interface named eno1)
To check: How to find the right interface name?
sudo ifconfig eno1 10.1.1.100 netmask 255.255.255.0 up
Plug and unplug if the ping fails.

> Replace the files 
in /home/xilinx/jupyter_notebooks/mmwsdr
upload either using the web interface or scp the following files:
- run.sh
- server.py
- txtd.npy
- RxDebug.ipynb

## 3. Run the testbed

> Run the transmitter FIRST (10.1.1.40)
$ ssh xilinx@10.1.1.40 password: xilinx
$ ping 10.1.1.40
$ python tx.py

To check: Does it matter whether to start Tx or Rx first?
To check: Red LEDs on the Tx board USB port?


> Run the receiver (10.1.1.30). 
$ ssh xilinx@10.1.1.30 password: xilinx
$ ping 10.1.1.30
$ python rx.py
