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
    nskip = 1 * 1024  # num of samples to skip between frames
    nframe = 32  # num of frames
    issave = True  # save the received IQ samples
    isdebug = False  # print debug messages
    iscalibrated = True  # apply calibration parameters
    sc_min = -250  # min sub-carrier index
    sc_max = 250  # max sub-carrier index
    tx_pwr = 15000  # transmit power

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

    x = np.random.randint(low = 0, high = 1300, size = (512,))
    y = np.random.randint(low = 0, high = 1300, size = (512,))
    angle = np.random.randint(low = -45, high = 45, size = (512,))
    # Main loop
    data = []
    while (1):
        for loc in range(8):
            # Step 2. Moce Rx to location (x_i, y_i, a_i)
            xytable2.move(x=x[loc], y=y[loc], angle=angle[loc])
            time.sleep(5);
            for beam_index in [0,8,16,24,32,50,48,56,63]:
                sdr1.beam_index = beam_index
                time.sleep(2)

                # Receive data
                rxtd = sdr2.recv(nfft, nskip, nframe)
                rxfd = np.fft.fft(rxtd, axis=1)
                Hest = rxfd * np.conj(np.fft.fft(txtd))
                hest = np.fft.ifft(Hest, axis=1)
                pdp = 20 * np.log10(np.abs(hest))
                sig_max = np.max(pdp, axis=1)
                sig_avg = np.mean(pdp, axis=1)
                snr = np.mean(sig_max - sig_avg)
                print("X: {:3d}, Y: {:3d}, A: {:2d}, BF {:2d}, SNR: {:2.2f} dB".format(x[loc], y[loc], angle[loc], beam_index, snr))
                data.append([x[loc], y[loc], angle[loc], beam_index, snr])

        A = np.array(data)
        print(A.shape)

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break

    # Delete the SDR object. Close the TCP connections.
    del sdr1, sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
