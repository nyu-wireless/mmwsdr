"""

"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr

# Parameters
nfft = 1024  # num of continuous samples per batch
nskip = 1024  # num of samples to skip between batches
nbatch = 10  # num of batches
isdebug = True  # print debug messages
node = 'rfdev3-in1'  # 'rfdev3-in1' or 'rfdev3-in2'


def main():
    """

    :return:
    :rtype:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    args = parser.parse_args()

    # Create an SDR object
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=args.freq, unit_name='SN0240', isdebug=isdebug)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=args.freq, unit_name='SN0243', isdebug=isdebug)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Make sure that the nodes are not transmitting
    sdr0.send(np.zeros((nfft,), dtype='int16'))

    while (1):
        # Receive data
        rxtd = sdr0.recv(nfft, nskip, nbatch)

        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)
        f = np.linspace(-nfft / 2, nfft / 2)
        for ibatch in range(nbatch):
            plt.plot((abs(rxfd[ibatch, :])), '-')
        plt.show()

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n Press enter to receive again: ")
        else:
            ans = input("Enter 'q' to exit or\n Press enter to receive again: ")

        if ans == 'q':
            break
    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
