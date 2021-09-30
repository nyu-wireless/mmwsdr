"""
:description: This class creates an software defined radio (SDR) comprised with a Xilinx ZynqMP Ultrascale+ RFSoC FPGA
board and a Sivers IMA TRX BF/01. The TRX BF/01 is a 16+16 IEEE802.11ad beamforming transceiver with a compute radio
front-end operating in the 57-66 GHz bands. This class has been designed for the setup in the COSMOS testbed. More
information could be found in docs.

:organization: New York University

:authors: Panagiotis Skrimponis
          Tommy Azzino


:copyright: 2021
"""
import os
import sys
import time
import math
import mmwsdr
import socket
import numpy as np

path = os.path.abspath('../../../lib/ederenv/Eder_A/')
if path not in sys.path:
    sys.path.append(path)
import eder


class Sivers60GHz(object):
    """
    Sivers60GHz class
    """

    def __init__(self, ip='10.115.1.3', freq=60.48e9, unit_name='SN0240', board_type='MB1', eder_version='2',
                 isdebug=False, iscalibrated=False):
        self.ip = ip
        self.iscalibrated = iscalibrated
        self.isdebug = isdebug
        self.sock = None
        self.fpga = None
        self.array = None

        # Create the FPGA and the Array object
        self.array = eder.Eder(init=True, unit_name=unit_name, board_type=board_type, eder_version=eder_version)
        self.array.check()
        self.fpga = mmwsdr.fpga.ZCU111(ip=ip, isdebug=isdebug)
        self.freq = freq

        # Establish connection with the COSMOS TCP Server.
        self.__connect()

        if ip == '10.113.6.3':
            self.cal_iq_rx_a = 1.07426956483
            self.cal_iq_rx_v = -0.14
            self.cal_iq_tx_a = 0.966966841446
            self.cal_iq_tx_v = 0
        elif ip == '10.113.6.4':
            self.cal_iq_rx_a = 1.03818588691
            self.cal_iq_rx_v = -0.1
            self.cal_iq_tx_a = 1.0
            self.cal_iq_tx_v = 0.0
        else:
            self.cal_iq_rx_a = 1.0
            self.cal_iq_rx_v = 0.0
            self.cal_iq_tx_a = 1.0
            self.cal_iq_tx_v = 0


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
            time.sleep(0.2)
            self.sock.shutdown(socket.SHUT_RDWR)
            time.sleep(0.2)
            self.sock.close()

    def apply_cal_rx(self, rxtd):
        """

        :param rxtd:
        :type rxtd: np.array
        :return:
        :rtype:
        """

        # Apply RX IQ cal factors
        re = (1 / self.cal_iq_rx_a) * rxtd.real
        im = ((-1) * re * math.tan(self.cal_iq_rx_v)) + (rxtd.imag / math.cos(self.cal_iq_rx_v))
        return re + 1j * im

    def send(self, txtd):
        """

        :param txtd:
        :type txtd:
        :return:
        :rtype:
        """
        if self.mode is not 'TX':
            self.mode = 'TX'
        self.fpga.send(txtd)

    def recv(self, nread, nskip, nbatch):
        """

        :param nread:
        :type nread:
        :param nskip:
        :type nskip:
        :param nbatch:
        :type nbatch:
        :return: rxtd
        :rtype:
        """

        # Calculate the total number of samples to read:
        # (Number of batch) * (samples per batch) * (# of channel) * (I/Q)
        nsamp = nbatch * nread * self.fpga.nch * 2

        if self.mode is not 'RX':
            self.mode = 'RX'
        self.sock.sendall(b'+ %d %d %d\r\n' % (nread / self.fpga.npar, nskip / self.fpga.npar, nsamp * 2))

        rxtd = self.fpga.recv(nsamp)

        # remove mean
        rxtd -= np.mean(rxtd)

        rxtd = rxtd.reshape(nbatch, nread)
        if self.iscalibrated:
            rxtd = self.apply_cal_rx(rxtd)
        return rxtd

    @property
    def freq(self):
        """
        Get the carrier frequency of the SDR

        :return: The carrier frequency in Hz
        :rtype: float
        """
        return self.__freq

    @freq.setter
    def freq(self, freq):
        """
        Set the SDR carrier frequency

        :param freq: Carrier frequency in Hz
        :type freq: float
        """
        self.__freq = freq

        self.array.reset()
        self.array.tx_disable()
        self.array.rx_disable()
        self.mode = self.array.mode

    @property
    def mode(self):
        """
        Get the Sivers' array mode

        :return: 'RX' in receive mode or TX' in transmit mode
        :rtype: str
        """
        return self.array.mode

    @mode.setter
    def mode(self, array_mode):
        """
        Set the Sivers' array moded

        :param array_mode: 'RX' for receive mode or TX' for transmit mode
        :type array_mode: str
        """
        if array_mode == 'TX':
            self.array.run_tx(freq=self.freq)
            self.array.tx.dco.run()
            self.array.tx.regs.wr('tx_bb_ctrl', 0x17)
            self.array.tx.regs.wr('tx_bf_gain', 0x0e)
            self.array.tx.regs.wr('tx_rf_gain', 0x0e)
            self.array.tx.regs.wr('tx_bb_gain', 0x03)
        elif array_mode == 'RX':
            self.array.run_rx(freq=self.freq)
            self.array.rx.dco.run()
            self.array.rx.regs.wr('rx_bf_rf_gain', 0xee)

    @property
    def beam_index(self):
        """
        Get the SDR beamforming (BF) vector

        :return: Index of the RX or TX BF vector (row of the RX BF AWV Table)
        :rtype: int
        """
        return self.__beam_index

    @beam_index.setter
    def beam_index(self, index):
        """
        Set the receive (RX) and transmit (TX) beamforming (BF) vectors.

        :param index: Index of the RX BF vector (row of the RX BF AWV Table)
        :type index: int
        """
        self.array.tx.set_beam(index)
        self.array.rx.set_beam(index)
        self.__beam_index = index
