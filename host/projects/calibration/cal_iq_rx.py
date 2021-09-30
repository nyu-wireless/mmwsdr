"""

"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib
import math

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
    nfft = 1024  # num of continuous samples per batch
    nskip = 1024 * 5  # num of samples to skip between batches
    nbatch = 100  # num of batches
    isdebug = True  # print debug messages
    tx_pwr = 12000  # transmit power

    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="sdr mode (i.e., rx)")
    args = parser.parse_args()

    if args.mode == 'tx':
        freq = 61.29e9  # carrier frequency in Hz
        sc = -256  # tx subcarrier index
    elif args.mode == 'rx':
        freq = 60.48e9  # carrier frequency in Hz
        sc = 166  # rx subcarrier index
    else:
        raise Exception

    # Create an SDR object and the XY table
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=freq, unit_name='SN0240', isdebug=isdebug)
        xytable0 = mmwsdr.utils.XYTable('xytable1', isdebug=isdebug)

        # Move the SDR to the lower-right corner
        xytable0.move(x=0, y=0, angle=0)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=freq, unit_name='SN0243', isdebug=isdebug)
        xytable0 = mmwsdr.utils.XYTable('xytable2', isdebug=isdebug)

        # Move the SDR to the lower-left conrner
        xytable0.move(x=1300, y=0, angle=0)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    # Configure the RFSoC
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Main loop
    while (1):
        if args.mode == 'tx':
            # Create a signal in frequency domain
            txfd = np.zeros((nfft,), dtype='complex')
            txfd[(nfft >> 1) + sc] = 1
            txfd = np.fft.fftshift(txfd, axes=0)

            # Then, convert it to time domain
            txtd = np.fft.ifft(txfd, axis=0)

            # Set the tx power
            txtd = txtd / np.max([np.abs(txtd.real), np.abs(txtd.imag)]) * tx_pwr

            # Transmit data
            sdr0.send(txtd)
        elif args.mode == 'rx':
            # Make sure that the node is not transmitting
            # sdr0.send(np.zeros((nfft,), dtype='int16'))

            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nbatch)

            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)

            print("Max subcarrier: {}".format(f[np.argmax(abs(rxfd[0, :]))]))

            sum_re = 0.0
            sum_im = 0.0
            for ibatch in range(nbatch):
                fd = np.zeros((nfft,), dtype='complex')
                fd[(nfft >> 1) + sc] = rxfd[ibatch, (nfft >> 1) + sc]
                fd[(nfft >> 1) - sc] = rxfd[ibatch, (nfft >> 1) - sc]
                fd = np.fft.fftshift(fd)
                td = np.fft.ifft(fd)
                sum_re += np.sqrt(np.mean(td.real ** 2))
                sum_im += np.sqrt(np.mean(td.imag ** 2))

            # Find the alpha
            a = sum_re / sum_im
            nvhypo = 101
            vhypos = np.linspace(-1, 1, nvhypo)
            re = (1 / a) * rxtd.real.reshape(nbatch, nfft, 1)
            im = rxtd.real.reshape(nbatch, nfft, 1) * (-1 * np.tan(vhypos) / a) + rxtd.imag.reshape(nbatch, nfft, 1) * (
                    1 / np.cos(vhypos))
            td = re + 1j * im
            fd = np.fft.fft(td, axis=1)
            fd = np.fft.fftshift(fd, axes=1)
            sbs = np.sum(np.abs(fd[:, (nfft >> 1) - sc, :] / fd[:, (nfft >> 1) + sc, :]), axis=0)
            m = sbs / np.min(sbs)
            plt.plot(vhypos, 20 * np.log10(m))
            plt.show()

            v = vhypos[np.argmin(m)]
            print('Alpha: {}'.format(a))
            print('V: {}'.format(v))

            td = rxtd[0, :]
            re = (1 / a) * td.real
            im = td.real * (-1 * np.tan(v) / a) + td.imag * (1 / np.cos(v))
            td = re + 1j * im

            fd = np.fft.fftshift(np.fft.fft(td))
            fd0 = np.fft.fftshift(np.fft.fft(rxtd[0, :]))
            plt.plot(f, np.abs(fd0))
            plt.plot(f, np.abs(fd))
            plt.grid()
            plt.show()

            plt.plot(f, 20 * np.log10(np.abs(fd0)))
            plt.plot(f, 20 * np.log10(np.abs(fd)))
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
