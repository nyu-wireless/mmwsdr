# -*- coding: utf-8 -*-
"""
@description: This class establishes a communication link over TCP 
between a host and a Xilinx ZynqMP Ultrascale+ RFSoC FPGA board. 
The host configures the RF data converter given a parameter file, 
receives samples from the ADCs, and sends samples to the DACs in
non-realtime mode. The application running in the processing system
(PS) of the FPGA is based on a modified version of Xilinx `rftool`.

@authors: Panagiotis Skrimponis
          Aditya Dhananjay

@organization: New York University
               Pi-Radio

@copyright 2021
"""

import sys
import socket
import time
import struct
import numpy as np

class RFSoC(object):
    """
    Base class for the RFSoC
    """
    __nco = 0e9             # frequency of the NCO in Hz
    __nch = 1               # num of channels
    __ndac = 2              # num of D/A converters
    __nadc = 2              # num of A/D converters
    __npar = 4              # num of parallel samples per clock cycle
    __pll = 3932.16e6       # base sample rate of the converters in Hz
    __drate = 4             # decimation rate
    __irate = 4             # interpolation rate
    __max_tx_samp = 32768   # store up to 16KB of tx data
    __max_rx_samp = 1024**3 # store up to 1GB of rx data

    @property
    def fs(self):
        return self.__pll/self.__irate

    def __init__(self, ip=10.113.1.3, isDebug=False):
        """
        Class constructor
        """
        # Set the parameters from constructor arguments
        self.ip = ip
        self.isDebug = isDebug
        
        # Establish the TCP connections
        self.__connect__()
        self.__send_cmd__(b'TermMode 1')
    
    def __del__(self):
        """
        Class destructor
        """
        self.__disconnect()

    def __connect__(self):
        """
        This function establishes a communication link between a 
        host and a Xilinx RFSoC device
        """
        self.sock_data = socket.create_connection((self.ip, 8082))
        self.sock_ctrl = socket.create_connection((self.ip, 8081))
        self.sock_data.settimeout(5)
        self.sock_ctrl.settimeout(5)
    
    def __disconnect__(self):
        """
        This function disbands the communication link between a
        host and a Xilinx RFSoC device
        """
        self.sock_ctrl.close()
        self.sock_data.close()

    def __send_cmd__(self, cmd):
        """
        This function sends a command to the `rftool` running on
        the of the processing system (PS).
        """
        
        # Send a command to the FPGA
        self.sock_ctrl.sendall(cmd+b'\r\n')
        
        # Wait for the FPGA to process the command
        time.sleep(0.1)

        # Read the response and print if `isDebug` is true
        rsp = self.sock_ctrl.recv(32768)
        if self.isDebug:
            print(rsp)
