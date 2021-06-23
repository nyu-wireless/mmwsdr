# -*- coding: utf-8 -*-
"""
@description: This class creates an software defined radio (SDR)
comprised with a Xilinx ZynqMP Ultrascale+ RFSoC FPGA board and
a Sivers IMA TRX BF/01. The TRX BF/01 is a 16+16 IEEE802.11ad
beamforming transceiver with a compute radio front-end operating
in the 57-66 GHz bands. This class has been designed for the
setup in the COSMOS testbed. More information could be found under
the docs.

@authors: Panagiotis Skrimponis
          Tommy Azzino

@organization: New York University

@copyright 2021
"""
import os
import sys
import time
import mmwsdr
import socket

path = os.path.abspath('../../../lib/ederenv/Eder_A/')
if path not in sys.path:
    sys.path.append(path)
import eder

class Sivers60GHz(object):
    """
    Sivers60GHz class
    """

    def __init__(self, ip='10.115.1.3', freq=60.48e9, unit_name='SN0240', board_type='MB1', eder_version='2', is_debug=False):
        self.ip = ip
        self.fc = freq
        self.is_debug = is_debug
        self.sock = None

        # Establish connection with the COSMOS TCP Server.
        self.__connect()

        # Create the FPGA and the Array object
        self.fpga = mmwsdr.fpga.RFSoC(ip=ip, is_debug=is_debug)
        self.array = eder.Eder(init=True, unit_name=unit_name, board_type=board_type, eder_version=eder_version)
        self.array.check()

        # Initialize the beam-forming vectors
        self.beam_index = 0

    def __del__(self):
        self.__disconnect()
        del self.fpga
        del self.array

    def __connect(self):
        self.sock = socket.create_connection((self.ip, 8083))
        self.sock.settimeout(5)

    def __disconnect(self):
        if self.sock is not None:
            self.sock.sendall(b'disconnect\r\n')
            time.sleep(0.1)
            self.sock.close()

    def send(self, txtd):
        self.mode = 'TX'
        self.fpga.send(txtd)

    def recv(self, nread, nskip, nbatch):
        # Calculate the total number of samples to read:
        # (Number of batch) * (samples per batch) * (# of channel) * (I/Q)
        nsamp = nbatch * nread * self.nch * 2

        self.mode = 'RX'
        self.sock.sendall(b'+ %d %d %d' % (nread / self.fpga.npar, nskip / self.fpga.npar, nsamp * 2))

        rxtd = self.fpga.recv(nsamp)
        rxtd = rxtd.reshape(nread, nbatch)
        return rxtd

    @property
    def fc(self):
        return self.__fc

    @fc.setter
    def fc(self, freq):
        if freq == 58.32e9 or freq == 60.48e9 or freq == 62.64e9 or freq == 64.8e9:
            self.__fc = freq
        else:
            raise NotImplemented

    @property
    def nch(self):
        return self.fpga.nch

    @property
    def mode(self):
        return self.array.mode

    @mode.setter
    def mode(self, array_mode):
        if array_mode is 'TX':
            self.array.run_tx(freq=self.fc)
        elif array_mode is 'RX':
            self.array.run_rx(freq=self.fc)
        else:
            raise NotImplemented

    @property
    def beam_index(self):
        """
        Set the SDR beamforming (BF) direction

        Returns
        ----------
        beam_index : int
            Index of the RX or TX BF vector (row of the RX BF AWV Table)
        """
        return self.__beam_index

    @beam_index.setter
    def beam_index(self, index):
        """
        Set the receive (RX) beamforming (BF) vector.

        Parameters
        ----------
        index : int
            Index of the RX BF vector (row of the RX BF AWV Table)

        Returns
        -------
        None
        """
        self.array.tx.set_beam(index)
        self.array.rx.set_beam(index)
        self.__beam_index = index


