"""

"""

# Import Libraries
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

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
    sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', unit_name='SN0243', isdebug=isdebug)
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Make sure that the node is not transmitting
    sdr0.send(np.zeros((nread,), dtype='int16'))

    # Create a signal in frequency domain
    sc = 100  # subcarrier index.
    nfft = nread
    txfd = np.zeros((nfft,), dtype='int16')
    txfd[(nfft >> 1) + sc] = 1
    txfd = np.fft.fftshift(txfd, axes=0)

    # Then, convert it to time domain
    txtd = np.fft.ifft(txfd, axis=0)

    # Set the tx power
    txtd = txtd / np.mean(np.abs(txfd)) * tx_pwr

    # Transmit data
    sdr0.send(txtd)

    # The ZCU111 will keep transmitting the same data until we close the socket
    input("Press Enter to stop transmitting...")

    # Disconnect
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
