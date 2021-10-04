"""

"""

# Import Libraries
import os
import sys
import time
import argparse
import matplotlib
import subprocess
import numpy as np
import configparser

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
    sc = 400  # subcarrier index
    tx_pwr = 4000  # transmit power
    f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)  # subcarrier index vector for plotting

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
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=args.freq,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=args.freq,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in2'), iscalibrated=iscalibrated)

    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))

    # Main experimentation loop
    while (1):
        txtd = mmwsdr.utils.waveform.onetone(sc=sc, nfft=nfft) * tx_pwr  # Create a tone in frequency domain

        if args.node == 'srv1-in1':
            if args.mode == 'tx':
                sdr1.send(txtd)
                rxtd = sdr2.recv(nfft, nskip, nframe)
            else:
                sdr2.send(txtd)
                rxtd = sdr1.recv(nfft, nskip, nframe)
        else:
            if args.mode == 'tx':
                sdr2.send(txtd)
                rxtd = sdr1.recv(nfft, nskip, nframe)
            else:
                sdr1.send(txtd)
                rxtd = sdr2.recv(nfft, nskip, nframe)

        # Convert the received data to frequncy domain
        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)

        # Plot the data
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

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break

    # Close the TPC connections
    del sdr1
    del sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
