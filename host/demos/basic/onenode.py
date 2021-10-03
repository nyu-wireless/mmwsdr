"""

"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib
import configparser
import subprocess

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
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024  # num of samples to skip between frames
    nframe = 5  # num of frames
    iscalibrated = True  # apply rx and tx calibration factors
    isdebug = True  # print debug messages
    islocal = True
    sc = 400  # subcarrier index
    tx_pwr = 4000  # transmit power

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='sdr2-in1', help="COSMOS-SB1 node name (i.e., sdr2-in1)")
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

    # Main experimentation loop
    while (1):
        if args.mode == 'tx':
            # Create a tone in frequency domain
            txfd = np.zeros((nfft,), dtype='complex')
            txfd[(nfft >> 1) + sc] = 1
            txfd = np.fft.fftshift(txfd, axes=0)

            # Then, convert it to time domain
            txtd = np.fft.ifft(txfd, axis=0)

            # Set the tx power
            txtd = txtd / np.max([np.abs(txtd.real), np.abs(txtd.imag)]) * tx_pwr

            # Transmit data
            sdr0.send(txtd)
        elif args.mode == 'rx':
            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nframe)

            # Convert the received data to frequncy domain
            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            # Plot the data
            f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)
            for iframe in range(nframe):
                plt.plot(f, 20 * np.log10(abs(rxfd[iframe, :])), '-')
            plt.xlabel('Subcarrier index')
            plt.ylabel('Magnitude [dB]')
            plt.tight_layout()
            y_min = np.mean(20 * np.log10(abs(rxfd))) - 20
            y_max = np.max(20 * np.log10(abs(rxfd))) + 20
            plt.ylim([y_min, y_max])
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
