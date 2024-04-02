Instructions to build, set up and run the 60 GHz Channel Sounder developed by Notis. 


![IMG_8906](https://github.com/nyu-wireless/mmwsdr/assets/24817896/346ab6a4-8d33-41a2-9502-7f0f18a02c76)


# Table of Contents  

[1. Build](#1-build-the-testbed)

[2. Program](#2-program-the-testbed)

[3. Run](#3-run-the-testbed)

[4. RFSoC 4x2](#4-4x2)

## 1. Build the testbed

Carefully follow each step described in the [HW setup](https://github.com/nyu-wireless/mmwsdr/blob/main/2x2_sounder/HW_setup.pdf) document. You will learn how to connect the Sivers arrays (TX and RX) to the RFSoC 2x2 boards through the Broadband balun model Merkei BAL0006. 

## 2. Program the testbed

**Download the rx.img**

It is preferable to use Google Chrome. Other browsers might have a problem with big files. Click [here](https://drive.google.com/file/d/1YfHpmMC5HQftU6drCumDuZgqWMh2dPdv/view?usp=drive_link) to download it.

**Burn the rx.img to both SD Cards**

In Linux we can do the following. Insert the SD card in the computer, and run:

```
sudo fdisk -l
```

The SD card we need to flash should show something like this:

```
Disk /dev/sdd: 14.84 GiB, 15931539456 bytes, 31116288 sectors
Disk model: USB3.0 CRW   -SD
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xbc7f45e1
```

You may see /dev/sdb/ or other letters. That's ok. You are ready to flash it. 

```
sudo dd if=~/Downloads/rx.img of=/dev/sdd 
```

In Windows, you can use Rufus (https://rufus.ie/en/).

In OSX, you can use terminal comments.

More information can be found at https://pynq.readthedocs.io/en/latest/appendix/sdcard.html. 


**Configure the right static IP address on the TX**

The image will have a static IP address of 10.1.1.30. We will use this address for the RX. 

Hence, for the TX, we have to change it. To do so, please follow these steps:

 1) After flashing the SD cart, safely remove it, and re-insert it. It should appear as two filesystems (PYNQ and root);
 2) Open the root file system;
 3) Edit the /etc/network/interfaces.d/eth0 and modify the address. Let's set the TX to 10.1.1.40;
 4) Safely unmount the drive.

**Configure the right static IP address on the Host Computer**

Connect the switch to an host computer with an Ethernet cable, then set a static IP address (in our case the interface is named eno1). 

```
sudo ifconfig eno1 10.1.1.100 netmask 255.255.255.0 up
```

Unplug and replug if ping either the TX (10.1.1.40) or the RX (10.1.1.30) fails.

**SSH into the TX and RX and replace the scripts**

I recommend using Visual Studio to visually access the content of each board. You will have two VS instances running, one for the TX and one for the RX. 

Click on SSH (bottom-left) and:

1) Connect to the TX by typing ssh xilinx@10.1.1.40 (password: xilinx)
2) Connect to the RX by typing ssh xilinx@10.1.1.30 (password: xilinx)

Navigate to /home/xilinx/jupyter_notebooks/mmwsdr and upload & replace the following files (which you will find in this folder):
- run.sh
- server.py
- txtd.npy
- RxDebug.ipynb

## 3. Run the testbed

You are finally ready to launch your experiments. First of all, make sure the host computer is on the same network as the 2x2 boards. 
```
sudo ifconfig eno1 10.1.1.100 netmask 255.255.255.0 up
```
Ping the TX (10.1.1.40) and RX (10.1.1.30) to verify full connectivity among all the devices. 

Then, launch SSH to connect to the TX and the RX (either via terminal or using VS). 

From the TX, launch the python script that enables transmission of samples:
```
python tx.py
```

Then, from the RX, launch the python script that enables the capture of the transmitted samples:

```
python rx.py
```

The rx.py script will save the received IQ samples in .txt and .csv formats. Transfer these files to the host computer using these commands:
```
scp xilinx@10.1.1.30:/home/xilinx/hest.csv /home/ubuntu/Downloads/
scp xilinx@10.1.1.30:/home/xilinx/hest.txt /home/ubuntu/Downloads/
```

## 4. RFSoC 4x2 <a name="4x2"></a>

