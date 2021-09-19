"""
:description: This class creates an software defined radio (SDR)
comprised with a Xilinx ZynqMP Ultrascale+ RFSoC FPGA board and
a Sivers IMA TRX BF/01. The TRX BF/01 is a 16+16 IEEE802.11ad
beamforming transceiver with a compute radio front-end operating
in the 57-66 GHz bands. This class has been designed for the
setup in the COSMOS testbed. More information could be found under
the docs.

:authors: Panagiotis Skrimponis
          Tommy Azzino

:organization: New York University

:copyright: 2021
"""
import os
import sys
import time
import mmwsdr
import socket
import numpy as np


class Sivers60GHz(object):
    """
    Sivers60GHz class
    """

    def __init__(self, ip='10.115.1.3', freq=60.48e9, unit_name='SN0240', board_type='MB1', eder_version='2',
                 isdebug=False):
        self.ip = ip
        self.fc = freq
        self.isdebug = isdebug
        self.sock = None

        # Establish connection with the COSMOS TCP Server.
        self.__connect()

        # Create the FPGA and the Array object
        self.fpga = mmwsdr.fpga.ZCU111(ip=ip, isdebug=isdebug)

    def __del__(self):
        self.__disconnect()
        del self.fpga
        del self.array

    def __connect(self):
        self.sock = socket.create_connection((self.ip, 8083))
        self.sock.settimeout(5)

    def __disconnect(self):
        if self.sock != None:
            self.sock.sendall(b'disconnect\r\n')
            time.sleep(0.1)
            self.sock.close()

    def send(self, txtd):
        self.fpga.send(txtd)

    def recv(self, nread, nskip, nbatch):
        # Calculate the total number of samples to read:
        # (Number of batch) * (samples per batch) * (# of channel) * (I/Q)
        nsamp = nbatch * nread * self.fpga.nch * 2

        self.mode = 'RX'
        self.sock.sendall(b'+ %d %d %d\r\n' % (nread / self.fpga.npar, nskip / self.fpga.npar, nsamp * 2))

        rxtd = self.fpga.recv(nsamp)

        # remove mean
        rxtd -= np.mean(rxtd)

        rxtd = rxtd.reshape(nbatch, nread)
        return rxtd
