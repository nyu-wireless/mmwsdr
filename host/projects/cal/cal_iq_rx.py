"""

"""

# Import Libraries
import os
import sys
import numpy as np
import argparse
import matplotlib

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr

# Parameters
sc = 400  # subcarrier index
nread = 1024  # num of continuous samples per batch
nskip = 1024 * 5  # num of samples to skip between batches
nbatch = 100  # num of batches
tx_pwr = 20000  # transmit power
isdebug = True  # print debug messages


def cal_rx(sdr0, freq):
    """

    :param sdr0:
    :type sdr0:
    :param freq:
    :type freq:
    :return:
    :rtype:
    """
    sdr0.freq = freq  # set the receiver carrier frequency in Hz

    # Receive data
    rxtd = sdr0.recv(nread, nskip, nbatch)

    rxfd = np.fft.fft(rxtd, axis=1)
    rxfd = np.fft.fftshift(rxfd, axes=1)
    f = np.linspace(-nread / 2, nread / 2)
    for ibatch in range(nbatch):
        plt.plot((abs(rxfd[ibatch, :])), '-')
    plt.show()

    np.savez_compressed('rxtd.npz', rxtd)


def cal_tx(sdr0, freq):
    """

    :param sdr0:
    :type sdr0:
    :param freq:
    :type freq:
    :return:
    :rtype:
    """
    nfft = nread  # num of FFT points
    sdr0.freq = freq + 1.08e9  # set the transmitter carrier frequency in Hz

    # Create the tx signal in frequency domain
    txfd = np.zeros((nfft,), dtype='int16')
    txfd[(nfft >> 1) - sc] = 1
    txfd = np.fft.fftshift(txfd, axes=0)

    # Then, convert it to time domain
    txtd = np.fft.ifft(txfd, axis=0)

    # Set the tx power
    txtd = txtd / np.mean(np.abs(txfd)) * tx_pwr

    # Transmit data
    sdr0.send(txtd)

    if sys.version_info[0] == 2:
        ans = raw_input("Press enter to continue: ")
    else:
        ans = input("Press enter to continue: ")


def main():
    """

    :return:
    :rtype:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, const=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, const='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    args = parser.parse_args()

    # Create an SDR object
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=args.freq, unit_name='SN0240', isdebug=isdebug)

        # Configure the FPGA
        sdr0.fpga.configure('../../config/rfsoc.cfg')

        # Make sure that the node is not transmitting any signal
        sdr0.send(np.zeros((nread,), dtype='int16'))

        cal_tx(sdr0, args.freq)
        cal_rx(sdr0, args.freq)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=args.freq, unit_name='SN0243', isdebug=isdebug)

        # Configure the FPGA
        sdr0.fpga.configure('../../config/rfsoc.cfg')

        # Make sure that the node is not transmitting any signal
        sdr0.send(np.zeros((nread,), dtype='int16'))

        cal_rx(sdr0, args.freq)
        cal_tx(sdr0, args.freq)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
