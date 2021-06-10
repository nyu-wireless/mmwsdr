# -*- coding: utf-8 -*-
"""
@description: This class creates an object that contains an FPGA object
and an Array object. The latter object is used to control the Sivers arrays of Cosmos's Testbed.

@authors: Panagiotis Skrimponis
          Tommy Azzino

@organization: New York University

@copyright 2021
"""

import eder
import requests


class SDR(object):
    """
    SDR class.
    ...

    Attributes
    ----------
    fpga : obj
        fpga object associated with this class
    eder_array : obj
        object to configure and control the Sivers arrays

    Methods
    -------
    send():
        send data to be transmitted to the testbed.

    recv():
        receive and collect the data from the testbed
    """

    def __init__(self, fpga, fc=60.48e9):  # give a default value for the carrier freq
        """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            fpga : obj
                fpga object associated with this class
            fc : float
                the carrier frequency of the experiment
        """

        self.fpga = fpga
        self.fc = fc
        self.eder_array = eder.Eder(init=True, unit_name='array')
        # self.eder_array.reset() # reset is already performed in init()

        # TODO: check that Eder is present
        assert self.eder_array.check(), "An error occurred: chip not present"

    def send(self, data=None):
        """
        Sends data to be transmitted in the testbed.

        Parameters
        ----------
        data : array, optional
            The data to be sent (default is None)

        Returns
        -------
        None
        """

        if data is None:
            # create some data ??
            data = 0

        # configure the Sivers array in TX mode
        self.__array_mode__('TX')

    def recv(self):
        """
        Receives and processes the data received in the testbed.

        Returns
        -------
        Array with the received data to be processed
        """

        # configure the Sivers array in RX mode
        self.__array_mode__('RX')

    def __array_mode__(self, mode):
        """
        Sets up the mode (TX/RX) for the Sivers array.

        Parameters
        ----------
        mode : str
            The mode of the array ('TX' or 'RX')

        Returns
        -------
        None
        """

        # self.eder_array.reset() # maybe need to perform a reset when changing mode

        # TODO: do we need to disable TX or RX before switching to a different mode?
        # get current mode from Eder
        curr_mode = self.eder_array.mode
        if curr_mode is not None:
            # disable the current mode
            if curr_mode == mode:
                # the array is already in the required setup
                return
            else:
                if curr_mode == 'TX':
                    # disable current TX mode (switching to RX mode)
                    self.eder_array.tx_disable()
                elif curr_mode == 'RX':
                    # disable current RX mode (switching to TX mode)
                    self.eder_array.rx_disable()
                else:
                    raise NotImplemented

        if mode == 'TX':
            self.eder_array.tx_setup(self.fc)
            self.eder_array.tx_enable()
        elif mode == 'RX':
            self.eder_array.rx_setup(self.fc)
            self.eder_array.rx_enable()
        else:
            raise NotImplemented

    def set_tx_bf(self, beam_idx):
        """
        Sets a TX beam-forming vector.

        Parameters
        ----------
        beam_idx : int
            Index of the TX BF vector to set (row of the TX BF AWV Table)

        Returns
        -------
        None
        """
        self.eder_array.tx.set_beam(beam_idx)  # provided by the class Tx
        # self.eder_array.tx.bf.awv.set(beam_idx)

    def set_rx_bf(self, beam_idx):
        """
        Sets a RX beam-forming vector.

        Parameters
        ----------
        beam_idx : int
            Index of the RX BF vector to set (row of the RX BF AWV Table)

        Returns
        -------
        None
        """
        self.eder_array.rx.set_beam(beam_idx)  # provided by the class Rx
        # self.eder_array.rx.bf.awv.set(beam_idx)
