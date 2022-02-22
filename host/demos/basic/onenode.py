"""
:description: In this demo we control a single SDR node. We create an SDR object and an XY-Table object using the
`mmwsdr` library. The SDR object configures and controls a Xilinx RFSoC ZCU111 eval board and a Sivers IMA transceiver
board. A user can provide arguments to the script, such as the carrier frequency, the COSMOS node id and the transceiver
mode. The script by default starts a local connection with a carrier frequency at 60.48 GHz in receive mode.

:organization: New York University

:author: Panagiotis Skrimponis

:copyright: 2021
"""

# Import Libraries
import os
import sys
import socket
import argparse
import numpy as np
import matplotlib
import configparser

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

path = os.path.relpath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr


# Define Main
def main():
    """
    Main function
    """

    # Parameters
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024  # num of samples to skip between frames
    nframe = 5  # num of frames
    iscalibrated = True  # apply rx and tx calibration factors
    isdebug = True  # print debug messages
    islocal = True  # Eder array is connected directly to the node over USB
    sc = 400  # sub-carrier index
    tx_pwr = 4000  # transmit power
    f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)  # sub-carrier index vector for plotting

    # Create an argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default="", help="COSMOS-SB1 node name (i.e., srv1-in1)")
    parser.add_argument("--mode", type=str, default="rx", help="SDR mode (i.e., rx)")
    args = parser.parse_args()

    # Create a configuration parser.
    config = configparser.ConfigParser()
    config.read("../../config/sivers.ini")

    # If the user is not providing a target node use the local node.
    if not args.node:
        node = socket.gethostname().split('.')[0]
    else:
        node = args.node

    # Create the SDR object
    sdr0 = mmwsdr.sdr.Sivers60GHz(config=config, node=node, freq=args.freq,
                                  islocal=islocal, isdebug=isdebug, iscalibrated=iscalibrated)

    # Create the XY-Table object
    if config[node]['table_name'] != None:
        xytable0 = mmwsdr.utils.XYTable(config[node]['table_name'], isdebug=isdebug)
        xytable0.move(x=float(config[node]['x']), y=float(config[node]['y']),
                      angle=float(config[node]['angle']))

    # Main loop
    while (1):
        if args.mode == 'tx':
            # Create a tone in frequency domain
            txtd = mmwsdr.utils.waveform.onetone(sc=sc, nfft=nfft)

            # Scale the data from [-1,1] to increase the baseband tx power.
            txtd *= tx_pwr

            # Transmit data
            sdr0.send(txtd)
        elif args.mode == 'rx':
            # Receive nframe x nfft samples
            # 1. save nfft samples
            # 2. pause for nskip samples
            # 3. repeat steps 1, 2 nframe times
            rxtd = sdr0.recv(nfft, nskip, nframe)

            # Convert the received data to frequency-domain using FFT
            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            # Find the magnitude of the data in dB
            mag = 20 * np.log10(np.abs(rxfd))

            # Plot the data
            for iframe in range(nframe):
                plt.plot(f, mag[iframe, :], '-')
            plt.xlabel('Sub-carrier index')
            plt.ylabel('Magnitude [dB]')
            plt.tight_layout()
            y_min = np.mean(mag) - 20
            y_max = np.max(mag) + 20
            plt.ylim([y_min, y_max])
            plt.grid()
            plt.show()
        else:
            raise ValueError("SDR mode can be either 'tx' or 'rx'")

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        # Exit from the loop when the input is 'q'. Otherwise continue.
        if ans == 'q':
            break

    # Delete the SDR object. Close the TCP connections.
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
