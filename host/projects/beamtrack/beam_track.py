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
    file_id = 0  #
    naoa = 91  #
    nfft = 1024  # num of continuous samples per frames
    nskip = 100  # num of samples to skip between frames
    nframe = 20  # num of frames
    isprocess = True  #
    islocal = True  # True if the array is connected locally. False to connect to the Eder server
    isdebug = True  # print debug messages
    iscalibrated = True  # print debug messages
    issave = True  # save the receive and transmit time domain data
    sc_min = -250  # min subcarrier index
    sc_max = 250  # max subcarrier index
    tx_pwr = 15000  # transmit power

    # Find the angles of arrival
    aoa = np.linspace(-45, 45, naoa)

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

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

    if issave:
        np.savez_compressed("txtd.npz", txtd=txtd)

    while (1):
        if args.mode == 'tx':
            try:
                while True:
                    sdr0.beamsweep()
            except KeyboardInterrupt:
                print('Received termination signal')
                break
        elif args.mode == 'rx':
            rxtd = sdr0.recv(nfft, nskip, nframe)

            if isprocess:
                rxfd = np.fft.fft(rxtd, axis=1)
                Hest = rxfd * np.conj(np.fft.fft(txtd))
                hest = np.fft.ifft(Hest, axis=1)

                val = np.max(np.abs(hest) ** 2, axis=1)
                plt.plot(20 * np.log10(val))
                plt.grid()
                plt.show()

            if issave:
                np.savez_compressed("rxtd_{}.npz".format(file_id), rxtd=rxtd)
                file_id += 1
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
