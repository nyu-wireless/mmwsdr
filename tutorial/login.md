# Logging into the NYU Wireless FPGA server

The NYU Wireless lab has a dedicated high performance machine for running the FPGA tools.  If you wish to avoid installing the software on your own computer, you can log into this machine.
The machine is shared, so you will need to coordinate with others to ensure you are not using the machine simultaneously.

## Logging into the server
To log into the machine:

* Email [Sundeep Rangan](mailto:srangan@nyu.edu) to request a user name and password for an account on the server.
* Install any ssh client on your local machine.
* Log in at the IP address:  172.24.113.58 with the requested user name and password.
* If you are not on the NYU network, you will need to log in with a [VPN](https://www.nyu.edu/life/information-technology/infrastructure/network-services/vpn.html)

## Installing Chrome Remote Desktop
The FPGA tools generally require that you have a GUI interface.  

* On your local computer, install Google Chrome browser
* Navigate to the [Chrome remote desktop](https://remotedesktop.google.com/)
* Select "Access my computer"
* Select "Set up via SSH".  You will see a "set up another computer" box.  Copy the link for Debian linux.  It should be something like https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb.
* SSH into the NYU FPGA server machine
* On the remote machine, download and install the file.  For example, if the file was named as above
~~~
   > wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
   > sudo dpkg -i https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
~~~
