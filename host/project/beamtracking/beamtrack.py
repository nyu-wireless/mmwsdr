"""
:organization: New York University
:author: Panagiotis Skrimponis

:copyright: 2022
"""
# Import Libraries
import os
import sys
import time
import socket
import argparse
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
    Main function
    """

    # Parameters
    file_id = 0  # file id
    nfft = 1024  # num of continuous samples per frames
    nskip = 1024  # num of samples to skip between frames
    nframe = 16  # num of frames
    issave = False  # save the received IQ samples
    isdebug = False  # print debug messages
    iscalibrated = True  # apply calibration parameters
    sc_min = -400  # min sub-carrier index
    sc_max = 400  # max sub-carrier index
    tx_pwr = 12000  # transmit power
    file_id = 0

    node = socket.gethostname().split('.')[0]  # Find the local hostname

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create the SDR objects
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=args.freq,
                                  isdebug=isdebug, islocal=(node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=args.freq,
                                  isdebug=isdebug, islocal=(node == 'srv1-in2'), iscalibrated=iscalibrated)

    # Create the XY table controllers. Load the default location.
    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))

    # Create a wide-band tx signal
    txtd = mmwsdr.utils.waveform.wideband(sc_min=sc_min, sc_max=sc_max, nfft=nfft)

    # Step 1. Tx send sequence (cyclic rotation)
    sdr1.send(txtd*tx_pwr)

    x_test = np.linspace(0, 1300, 14, dtype=int);
    y_test = np.linspace(0, 1300, 14, dtype=int);
    angle_test = np.linspace(-45, 45, 7)


    # Move TX at the center facing at 0 deg
    xytable1.move(x=650, y=650, angle=0)

    # Main loop
    data = []

    while (1):
        loc = 0
        for x in x_test:
            for y in y_test:
                for angle in angle_test:
                    print("({:4d}) X: {:4d}, Y: {:4d}, A: {:2f}".format(loc, x, y, angle))
                    loc = loc + 1
                    xytable2.move(x, y, angle)
                    time.sleep(2)
                    for beam_index in [1, 5, 9, 13, 17, 21, 25, 29, 32, 35, 39, 43, 47, 51, 55, 59, 63]:
                        sdr2.beam_index = beam_index
                        time.sleep(1)

                        # Receive data
                        rxtd = sdr2.recv(nfft, nskip, nframe)
                        rxfd = np.fft.fft(rxtd, axis=1)
                        Hest = rxfd * np.conj(np.fft.fft(txtd))
                        hest = np.fft.ifft(Hest, axis=1)
                        pdp = 20 * np.log10(np.abs(hest))
                        sig_max = np.max(pdp, axis=1)
                        sig_avg = np.mean(pdp, axis=1)
                        snr = np.mean(sig_max - sig_avg)
                        data.append([x, y, angle, beam_index, snr])

        data = np.array(data)

        np.savez_compressed('beamtracking_data_{}'.format(file_id), data=data)
        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break
        else:
            file_id += 1

    # Delete the SDR object. Close the TCP connections.
    del sdr1, sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
