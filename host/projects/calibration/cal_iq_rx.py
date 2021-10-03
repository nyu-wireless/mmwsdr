"""

"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib
import math
import configparser
import subprocess

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
    nvhypo = 101
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024 * 5  # num of samples to skip between frames
    nframe = 100  # num of frames
    isdebug = True  # print debug messages
    iscalibrated = False  # apply rx and tx calibration factors
    tx_pwr = 12000  # transmit power

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default='sdr2-in1', help="COSMOS-SB1 node name (i.e., sdr2-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="SDR mode (i.e., rx)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    if args.mode == 'tx':
        freq = 61.29e9  # carrier frequency in Hz
        sc = -422  # tx subcarrier index
    elif args.mode == 'rx':
        freq = 60.48e9  # carrier frequency in Hz
        sc = 422  # rx subcarrier index
    else:
        raise Exception

    # Create the SDR
    sdr0 = mmwsdr.sdr.Sivers60GHz(config=config, node=args.node, freq=freq,
                                  isdebug=isdebug, iscalibrated=iscalibrated)
    if config[args.node]['table_name'] != None:
        xytable0 = mmwsdr.utils.XYTable(config[args.node]['table_name'], isdebug=isdebug)
        xytable0.move(x=float(config[args.node]['x']), y=float(config[args.node]['y']),
                      angle=float(config[args.node]['angle']))

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
            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nframe)

            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)

            print("Max subcarrier: {}".format(int(f[np.argmax(abs(rxfd[0, :]))])))

            sum_re = 0.0
            sum_im = 0.0
            for iframe in range(nframe):
                fd = np.zeros((nfft,), dtype='complex')
                fd[(nfft >> 1) + sc] = rxfd[iframe, (nfft >> 1) + sc]
                fd[(nfft >> 1) - sc] = rxfd[iframe, (nfft >> 1) - sc]
                fd = np.fft.fftshift(fd)
                td = np.fft.ifft(fd)
                sum_re += np.sqrt(np.mean(td.real ** 2))
                sum_im += np.sqrt(np.mean(td.imag ** 2))

            # Find the alpha
            a = sum_re / sum_im

            vhypos = np.linspace(-1, 1, nvhypo)
            re = (1 / a) * rxtd.real.reshape(nframe, nfft, 1)
            im = rxtd.real.reshape(nframe, nfft, 1) * (-1 * np.tan(vhypos) / a) + rxtd.imag.reshape(nframe, nfft, 1) * (
                    1 / np.cos(vhypos))
            td = re + 1j * im
            fd = np.fft.fft(td, axis=1)
            fd = np.fft.fftshift(fd, axes=1)
            sbs = np.sum(np.abs(fd[:, (nfft >> 1) - sc, :] / fd[:, (nfft >> 1) + sc, :]), axis=0)
            m = sbs / np.min(sbs)
            plt.plot(vhypos, 20 * np.log10(m))
            plt.show()

            v = vhypos[np.argmin(m)]

            config[args.node]['cal_iq_rx_a'] = str(a)
            config[args.node]['cal_iq_rx_v'] = str(v)

            print('Alpha: {}'.format(a))
            print('V: {}'.format(v))
        else:
            raise ValueError("SDR mode can be either 'tx' or 'rx'")

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")


        if ans == 'q':
            break

    # Update calibration parameters
    with open('../../config/sivers.ini', 'w') as file:
        config.write(file)

    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
