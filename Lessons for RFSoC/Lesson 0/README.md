
								
# 									MMWSDR Notes
# Lesson 0:

### Working with the RFSoC 2x2 remotely
The RFSoC 2x2 board is connected to a Workstation in the Wireless Lab at NYU Wireless. This machine can be accessed remotely with the cross-platform screen sharing system, VNC. In order to remotely login and use the board, the following steps can be followed,

**Important Note**:
To login to the remote system one must either be connected to the NYU Network directly or use the NYU VPN.
	Download a VNC application(in this case RealVNC has been used) by going to this link and choosing the download files based on your operating system.
	Using the downloaded file install the application on your Desktop or Mac
#### For Windows:
1) Go to the Start Menu and open RealVNC Viewer.
2) Once the window opens up, go to File -> New Connection, another window pops-up
3) In this new window enter the host name or IP address along with a Name of your choice.

#### Current Credentials:

IP Address       : 172.24.113.58

RealVNC Password : nyu@1234

Login Password   : nyu@1234

**Note**: The name doesn’t affect the connection to the system, it is simply a nickname that you give.
	Once done an icon with the nickname provided appears on the original RealVNC window. Double click on this, click continue and enter the password to connect to the system.
## Lesson 0.1: Introduction to RFSoC 2x2 board
The RFSoC 2x2 board is an SDR board that can be used to emulate a radio system. The 2x2 has high speed RF ADCs (2 no.s) to sample RF signals directly without the need of any mixer circuitry, which is then sent to the ZYNQ Ultrascale+ chip on the board; it also has 2 RF DACs to transmit data out from the board. The ZYNQ Ultrascale+ chip contains 2 processing components, that is, a set of ARM core processors (Processing System) and an FPGA (Programmable Logic) along with some memory elements such as DRAMs. The ARM core processors act as the host and the FPGA acts as the target. Using a framework called PYNQ we can communicate with the processing system through a browser where the browser acts as the terminal to send commands as well as a UI front end to display received data.

The RFSoC's architecture is as below.

![](Images/Picture1.png)

This [link](http://www.rfsoc-pynq.io/rfsoc_2x2_overview.html) has detailed information on the RFSoC's architecture.

**Important:** The RFSoC 2x2 board has been discontinued and most links leading from the above link would be redirected to the corresponding pages for the RFSoC 4x2. To go to the 2x2 board's corresponding page please replace the "….4x2…." in the URL to "….2x2…."

Example: When a link for the 2x2 is selected a 4x2 page is loaded with the following URL

![](Images/Picture2.png)

To go to the 2x2 page, the URL can be changed to

![](Images/Picture3.png)


