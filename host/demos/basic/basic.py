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
nskip = 1024 * 5  # num of samples to skip between batches
nbatch = 10  # num of batches
isdebug = True  # print debug messages
sc = 400  # subcarrier index
tx_pwr = 10000  # transmit power


def main():
    """

    :return:
    :rtype:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="sdr mode (i.e., rx)")
    args = parser.parse_args()

    # Create an SDR object and the XY table
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=args.freq, unit_name='SN0240', isdebug=isdebug)
        xytable0 = mmwsdr.utils.XYTable('xytable1')

        # Move the SDR to the lower-right corner
        xytable0.move(x=0, y=0, angle=0)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=args.freq, unit_name='SN0243', isdebug=isdebug)
        xytable0 = mmwsdr.utils.XYTable('xytable2')

        # Move the SDR to the lower-left conrner
        xytable0.move(x=1300, y=0, angle=0)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    # Configure the RFSoC
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Main loop
    while (1):
        if args.mode == 'tx':
            # Make sure that the nodes are not transmitting
            sdr0.send(np.zeros((nfft,), dtype='int16'))

            # Create a signal in frequency domain
            txfd = np.zeros((nfft,), dtype='int16')
            txfd[(nfft >> 1) + sc] = 1
            txfd = np.fft.fftshift(txfd, axes=0)

            # Then, convert it to time domain
            txtd = np.fft.ifft(txfd, axis=0)

            # Set the tx power
            txtd = txtd / np.mean(np.abs(txfd)) * tx_pwr

            # Transmit data
            sdr0.send(txtd)
        elif args.mode == 'rx':
            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nbatch)

            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)
            f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)
            plt.plot(f, abs(np.mean(rxfd, axis=0)), '-')
            plt.xlabel('Subcarrier index')
            plt.xlabel('Magnitude')
            plt.tight_layout()
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
