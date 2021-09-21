"""

"""

# Import Libraries
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr

# Parameters
nread = 1024  # num of continuous samples per batch
nskip = 1024  # num of samples to skip between batches
nbatch = 10  # num of batches
tx_pwr = 10000  # transmit power
isdebug = True


def main():
    """

    :return:
    :rtype:
    """

    # Create an SDR object
    sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', unit_name='SN0243', isdebug=isdebug)
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Make sure that the nodes are not transmitting
    sdr0.send(np.zeros((nread,), dtype='int16'))

    while(1):
        # Receive data
        rxtd = sdr0.recv(nread, nskip, nbatch)

        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)
        f = np.linspace(-nfft / 2, nfft / 2)
        for ibatch in range(nbatch):
            plt.plot((abs(rxfd[ibatch, :])), '-')
        plt.show()
        
        ans = raw_input("Enter 'q' to exit or\n Press enter to receive again: ")
        if ans == 'q':
            break
    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
