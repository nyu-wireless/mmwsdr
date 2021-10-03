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
    nvhypo = 11
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024 * 5  # num of samples to skip between frames
    nframe = 100  # num of frames
    iscalibrated = False  # apply rx and tx calibration factors
    isdebug = True  # print debug messages
    tx_pwr = 12000  # transmit power
    sc = 256  # tx subcarrier index

    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="sdr mode (i.e., rx)")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    if args.mode == 'tx':
        freq = 60.48e9  # carrier frequency in Hz
    elif args.mode == 'rx':
        freq = 60.48e9  # carrier frequency in Hz
    else:
        raise ValueError("SDR mode can be either 'tx' or 'rx'")

    # Create the SDR
    sdr0 = mmwsdr.sdr.Sivers60GHz(config=config, node=args.node, freq=freq,
                                  isdebug=isdebug, iscalibrated=iscalibrated)
    if config[args.node]['table_name'] != None:
        xytable0 = mmwsdr.utils.XYTable(config[args.node]['table_name'], isdebug=isdebug)
        xytable0.move(x=float(config[args.node]['x']), y=float(config[args.node]['y']),
                      angle=float(config[args.node]['angle']))

    # Main loop
    if args.mode == 'tx':
        # Create a signal in frequency domain
        txfd = np.zeros((nfft,), dtype='complex')
        txfd[(nfft >> 1) + sc] = 1
        txfd = np.fft.fftshift(txfd, axes=0)

        # Then, convert it to time domain
        txtd = np.fft.ifft(txfd, axis=0)

        # Set the tx power
        txtd = txtd / np.max([np.abs(txtd.real), np.abs(txtd.imag)]) * tx_pwr
    sum = np.zeros((2,))

    # Calculate the alpha
    for it in range(2):
        if args.mode == 'tx':
            # Transmit data
            if it == 0:
                sdr0.send(txtd.real)
            elif it == 1:
                sdr0.send(txtd.imag)
        elif args.mode == 'rx':
            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nframe)
            rxtd = sdr0.apply_cal_rx(rxtd)

            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            fd = np.zeros_like(rxfd)
            fd[:, (nfft >> 1) + sc] = rxfd[:, (nfft >> 1) + sc]
            fd[:, (nfft >> 1) - sc] = rxfd[:, (nfft >> 1) - sc]
            fd = np.fft.fftshift(fd, axes=1)
            td = np.fft.ifft(fd, axis=1)
            sum[it] = np.sum(np.sqrt(np.mean(np.abs(td) ** 2, axis=1)))
        else:
            raise ValueError("SDR mode can be either 'tx' or 'rx'")

        if sys.version_info[0] == 2:
            ans = raw_input("Press enter to continue ")
        else:
            ans = input("Press enter to continue ")

    if args.mode == 'tx':
        sdr0.freq = 61.29e9
        a = 1.03751928222
    elif args.mode == 'rx':
        sc = 166
        a = sum[0] / sum[1]
    else:
        raise ValueError("SDR mode can be either 'tx' or 'rx'")

    vhypos = np.linspace(-1, 1, nvhypo)
    sbs = np.zeros((nvhypo,))

    # Calculate the v
    for ivhypo in range(nvhypo):
        if args.mode == 'tx':
            v = vhypos[ivhypo]
            re = (1 / a) * txtd.real
            im = ((-1) * re * math.tan(v)) + (txtd.imag / math.cos(v))
            sdr0.send(re + 1j * im)
        elif args.mode == 'rx':
            # Receive data
            rxtd = sdr0.recv(nfft, nskip, nframe)
            rxtd = sdr0.apply_cal_rx(rxtd)

            rxfd = np.fft.fft(rxtd, axis=1)
            rxfd = np.fft.fftshift(rxfd, axes=1)

            sbs[ivhypo] = np.sum(np.abs(rxfd[:, (nfft >> 1) + sc]), axis=0)

        if sys.version_info[0] == 2:
            ans = raw_input("Press enter to continue ")
        else:
            ans = input("Press enter to continue ")

    if args.mode == 'rx':
        m = sbs / np.min(sbs)
        plt.plot(vhypos, 20 * np.log10(m))
        plt.show()

        v = vhypos[np.argmin(m)]
        print('Alpha: {}'.format(a))
        print('V: {}'.format(v))

    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
