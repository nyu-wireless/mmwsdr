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
    file_id = 0
    naoa = 91
    nfft = 1024  # num of continuous samples per frames
    nskip = 2 * 1024  # num of samples to skip between frames
    nframe = 100  # num of frames
    issave = True
    isprocess = True
    isdebug = True  # print debug messages
    iscalibrated = True  # print debug messages
    sc_min = -250  # min subcarrier index
    sc_max = 250  # max subcarrier index
    tx_pwr = 15000  # transmit power
    qam = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)

    # Find the angles of arrival
    aoa = np.linspace(-45, 45, naoa)


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

    # Create the tx signal (in frequency domain)
    txtd = mmwsdr.utils.waveform.wideband(sc_min=sc_min, sc_max=sc_max, nfft=nfft)
    # Main loop
    while (1):
        if args.mode == 'tx':
            sdr1.send(txtd)
        elif args.mode == 'rx':
            # Receive data
            rxtd = sdr2.recv(nfft, nskip, nframe)
            if isprocess:
                # Estimate the channel
                rxfd = np.fft.fft(rxtd, axis=1)
                Hest = rxfd * np.conj(np.fft.fft(txtd))
                hest = np.fft.ifft(Hest, axis=1)

                t = np.arange(nfft) / sdr2.fpga.fs / 1e-9
                plt.plot(t, 20 * np.log10(np.abs(hest[0, :]) / np.max(np.abs(hest[0, :]))))

                plt.xlabel('Delay (ns)', fontsize=13)
                plt.ylabel('Magnitude (dB)', fontsize=13)
                plt.tight_layout()
                plt.grid()
                plt.show()

                Hest = np.fft.fftshift(Hest, axis=1)
                plt.imshow(np.abs(Hest.T), aspect='auto', interpolation='none')
                plt.xlabel('Frame index')
                plt.ylabel('Subcarrier index')
                plt.show()

            if issave:
                np.savez_compressed('sounder_{}'.format(file_id), rxtd=rxtd)
        else:
            raise ValueError("SDR mode can be either 'tx' or 'rx'")

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break
    # Close the TPC connections
    del sdr1, sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
