# -*- coding: utf-8 -*-
"""
@description: This class establishes a communication link over TCP 
between a host and a Xilinx ZynqMP Ultrascale+ RFSoC FPGA board. 
The host configures the RF data converter given a parameter file, 
receives samples from the ADCs, and sends samples to the DACs in
non-realtime mode. The application running in the processing system
(PS) of the FPGA is based on a modified version of Xilinx `rftool`.

@authors: Panagiotis Skrimponis

@organization: New York University

@copyright 2021
"""

import os
import socket
import time
import struct
import numpy as np


class RFSoC(object):
    """
    Base class for the RFSoC
    """
    __nco = 0e9  # frequency of the NCO in Hz
    __nch = 1  # num of channels
    __ndac = 2  # num of D/A converters
    __nadc = 2  # num of A/D converters
    __npar = 4  # num of parallel samples per clock cycle
    __pll = 3932.16e6  # base sample rate of the converters in Hz
    __drate = 4  # decimation rate
    __irate = 4  # interpolation rate
    __max_tx_samp = 32768  # store up to 16KB of tx data
    __max_rx_samp = 1024 ** 3  # store up to 1GB of rx data

    @property
    def fs(self):
        return self.__pll / self.__irate

    @property
    def nch(self):
        return self.__nch
    
    @property
    def npar(self):
        return self.__npar

    def __init__(self, ip='10.113.1.3', is_debug=False):
        """
        Class constructor
        """
        # Set the parameters from constructor arguments
        self.ip = ip
        self.is_debug = is_debug

        # Establish the TCP connections
        self.__connect()
        self.__send_cmd(b'TermMode 1')

    def __del__(self):
        """
        Class destructor
        """
        self.__disconnect()

    def __connect(self):
        """
        This function establishes a communication link between a 
        host and a Xilinx RFSoC device
        """
        self.sock_data = socket.create_connection((self.ip, 8082))
        self.sock_data.settimeout(5)

        self.sock_ctrl = socket.create_connection((self.ip, 8081))
        self.sock_ctrl.settimeout(5)

    def __disconnect(self):
        """
        This function disbands the communication link between a
        host and a Xilinx RFSoC device
        """
        if self.sock_data is not None:
            self.sock_data.close()

        if self.sock_ctrl is not None:
            self.sock_ctrl.close()

    def __send_cmd(self, cmd):
        """
        This function sends a command to the `rftool` running on
        the of the processing system (PS).
        """

        # Send a command to the FPGA
        self.sock_ctrl.sendall(cmd + b'\r\n')

        # Wait for the FPGA to process the command
        time.sleep(0.1)

        # Read the response and print if `isDebug` is true
        rsp = self.sock_ctrl.recv(32768)
        if self.is_debug:
            print(rsp)

    def configure(self, file):
        """
        Parse the output file from the RFDC.
        """
        # Check if the file exists
        if not os.path.isfile(file):
            print('File %s does not exist'%(file))
            return

        with open(file, 'r') as fid:
            lines = fid.readlines()
            for line in lines:
                if line[0] is not '%':
                    self.__send_cmd(line)
                else:
                    # if there is a comment pause. This will be helpful to 
                    # let the PLLs stabilize
                    time.sleep(0.1)

    def recv(self, nsamp):
        nbytes = 2 * nsamp

        self.sock_data.sendall(b'ReadDataFromMemory 0 0 %d 0\r\n' % (nbytes))

        time.sleep(0.1)
        tmp = self.sock_data.recv(nbytes)
        data = np.array([struct.unpack('<h', tmp[it*2:(it*2)+2]) for it in range(len(tmp)/2)], dtype='int16').flatten()
        #data = np.array([it for it in struct.unpack('<h', tmp)], dtype='int16').flatten()
        while data.nbytes < nbytes:
            tmp = self.sock_data.recv(nbytes - data.nbytes)
            #tmp = np.array([it for it in struct.unpack('<h', tmp)], dtype='int16').flatten()
            tmp = np.array([struct.unpack('<h', tmp[it*2:(it*2)+2]) for it in range(len(tmp)/2)], dtype='int16').flatten()
            data = np.append(data, tmp)

        rsp = self.sock_data.recv(32768)
        if self.is_debug:
            print(rsp)
        time.sleep(0.1)

        print(data.shape)
        data = data.reshape(-1, self.__npar).astype(np.float)
        rxtd = data[::2, :] + 1j * data[1::2, :]
        return rxtd.flatten()

    def send(self, txtd):
        """
        This class sends a buffer to the FPGA. For the moment we assume
        that we receive only one channel.
        """

        # Split the input data in real and imaginary. Since the FPGA
        # is processing multiple data points per clock cycle, we need
        # to split the data based on that
        x_real = np.int16(txtd.real).reshape(-1, self.__npar)
        x_imag = np.int16(txtd.imag).reshape(-1, self.__npar)

        # Combine the real and imaginary data. Flatten the output buffer.
        data = np.zeros((x_real.shape[0] * 2, self.__npar))
        data[::2, :] = x_real
        data[1::2, :] = x_imag
        data = data.flatten()
        nsamp = data.shape[0]

        # Send the data over TCP with the necessary commands in the
        # control and data channel
        self.__send_cmd(b'LocalMemTrigger 1 0 0 0x0000')
        self.sock_data.sendall(b'WriteDataToMemory 0 0 %d 0\r\n' % (2 * nsamp))
        self.sock_data.sendall(data.tobytes())
        time.sleep(0.1)

        # Read response from the Data TCP Socket
        rsp = self.sock_data.recv(32768)
        if self.is_debug:
            print(rsp)

        self.__send_cmd(b'LocalMemTrigger 1 2 0 0x0001')
