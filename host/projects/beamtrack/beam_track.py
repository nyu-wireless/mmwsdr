"""

"""

# Import Libraries
import os
import sys
import argparse
import time
import configparser
import subprocess

import numpy as np
import matplotlib

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr


def main():
    """

    :return:
    :rtype:
    """
    # Parameters
    naoa = 91
    nfft = 1024  # num of continuous samples per frames
    nskip = 2 * 1024  # num of samples to skip between frames
    nframe = 20  # num of frames
    islocal = True
    isdebug = True  # print debug messages
    iscalibrated = True  # print debug messages
    sc_min = -450  # min subcarrier index
    sc_max = 450  # max subcarrier index
    tx_pwr = 15000  # transmit power

    # Find the angles of arrival
    aoa = np.linspace(-45, 45, naoa)

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='srv1-in1', help="COSMOS-SB1 node name (i.e., srv1-in1)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='srv1-in1', help="COSMOS-SB1 node name (i.e., srv1-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="SDR mode (i.e., rx)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create the SDR
    sdr0 = mmwsdr.sdr.Sivers60GHz(config=config, node=args.node, freq=args.freq,
                                  islocal=islocal, isdebug=isdebug, iscalibrated=iscalibrated)
    if config[args.node]['table_name'] != None:
        xytable0 = mmwsdr.utils.XYTable(config[args.node]['table_name'], isdebug=isdebug)
        xytable0.move(x=float(config[args.node]['x']), y=float(config[args.node]['y']),
                      angle=float(config[args.node]['angle']))

    # Generate the tx sequence
    txtd = mmwsdr.utils.waveform.wideband(sc_min=sc_min, sc_max=sc_max, nfft=nfft)
    if args.mode == 'tx':
        sdr0.send(txtd * tx_pwr)
    while (1):
        if args.mode == 'tx':
            sdr0.beamsweep()
        elif args.mode == 'rx':
            rxtd = sdr0.recv(nfft * nframe, nskip, 1)
            rxtd = rxtd.reshape(nframe, nfft)
            rxfd = np.fft.fft(rxtd, axis=1)
            Hest = rxfd * np.conj(np.fft.fft(txtd))
            hest = np.fft.ifft(Hest, axis=1)

            t = np.arange(nfft) / sdr0.fpga.fs / 1e-9
            plt.plot(t, 20 * np.log10(np.abs(hest[0, :]) / np.max(np.abs(hest[0, :]))))
            plt.xlabel('Delay [ns]')
            plt.ylabel('Magnitude [dB]')
            plt.tight_layout()
            plt.grid()
            plt.show()
        else:
            raise ValueError("SDR mode can be either 'tx' or 'rx'")

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break

        # Close the TPC connections
    del sdr0