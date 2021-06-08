# -*- coding: utf-8 -*-
"""
@description: This class establishes a communication link over TCP between a host and a Xilinx ZynqMP Ultrascale+ RFSoC
FPGA board. The host configures the RF data converter given a parameter file, receives samples from the ADCs, and sends
samples to the DACs in non-realtime mode. The application running in the processing system (PS) of the FPGA is based on
a modified version of Xilinx `rftool`.

@authors: Panagiotis Skrimponis

@organization: New York University
"""

class RFSoC(object):
    """
    Base class for the RFSoC
    """
    def __init__(self, ip=10.115.1.1, debug=False):
        self.ip = ip
        self.debug = debug