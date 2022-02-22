"""
:description:

:organizations: New York University
               Pi-Radio

:author: Panagiotis Skrimponis
         Aditya Dhananjay

:copyright: 2021
"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib
import socket
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
    Main function
    """

    # Parameters
    nvhypo = 101
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024 * 5  # num of samples to skip between frames
    nframe = 100  # num of frames
    isdebug = True  # print debug messages
    iscalibrated = False  # apply rx and tx calibration factors
    tx_pwr = 12000  # transmit power
    sc = 422  # rx sub-carrier index

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Find the COSMOS node id
    node = socket.gethostname().split('.')[0]

    # Create the SDR
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=args.freq + 0.81e9,
                                  isdebug=isdebug, islocal=(node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=args.freq,
                                  isdebug=isdebug, islocal=(node == 'srv1-in2'), iscalibrated=iscalibrated)

    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))

    # Create a signal in frequency domain
    txfd = np.zeros((nfft,), dtype='complex')
    txfd[(nfft >> 1) - sc] = 1
    txfd = np.fft.fftshift(txfd, axes=0)

    # Then, convert it to time domain
    txtd = np.fft.ifft(txfd, axis=0)

    # Set the tx power
    txtd = txtd / np.max([np.abs(txtd.real), np.abs(txtd.imag)]) * tx_pwr

    for it in range(2):
        if it == 0:
            sdr1.send(txtd)
            rxtd = sdr2.recv(nfft, nskip, nframe)
        else:
            # Change the carrier frequency
            sdr1.freq = args.freq
            sdr2.freq = args.freq + 0.81e9

            sdr2.send(txtd)
            rxtd = sdr1.recv(nfft, nskip, nframe)

        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)

        # Find the magnitude error
        fd = np.zeros((nframe, nfft), dtype='complex')
        fd[:, (nfft >> 1) + sc] = rxfd[:, (nfft >> 1) + sc]
        fd[:, (nfft >> 1) - sc] = rxfd[:, (nfft >> 1) - sc]
        fd = np.fft.fftshift(fd, axes=1)
        td = np.fft.ifft(fd, axis=1)
        sum_re = np.sum(np.sqrt(np.mean(td.real ** 2, axis=1)))
        sum_im = np.sum(np.sqrt(np.mean(td.imag ** 2, axis=1)))
        a = sum_re / sum_im

        # Find phase error
        vhypos = np.linspace(-1, 1, nvhypo)
        re = (1 / a) * rxtd.real.reshape(nframe, nfft, 1)
        im = rxtd.real.reshape(nframe, nfft, 1) * (-1 * np.tan(vhypos) / a) + rxtd.imag.reshape(nframe, nfft, 1) * (
                1 / np.cos(vhypos))
        td = re + 1j * im
        fd = np.fft.fft(td, axis=1)
        fd = np.fft.fftshift(fd, axes=1)
        sbs = np.sum(np.abs(fd[:, (nfft >> 1) - sc, :] / fd[:, (nfft >> 1) + sc, :]), axis=0)
        m = sbs / np.min(sbs)
        v = vhypos[np.argmin(m)]

        # Plot the parameters
        print('Alpha: {}'.format(a))
        print('V: {}'.format(v))

        if it == 1:
            config['srv1-in2']['cal_iq_rx_a'] = str(a)
            config['srv1-in2']['cal_iq_rx_v'] = str(v)
        else:
            config['srv1-in1']['cal_iq_rx_a'] = str(a)
            config['srv1-in1']['cal_iq_rx_v'] = str(v)

        if isdebug:
            plt.plot(vhypos, 20 * np.log10(m))
            plt.grid()
            plt.xlabel('Sideband suppression [dB]')
            plt.xlabel('RX IQ quadrature phase error [rad]')
            plt.show()

    # Update calibration parameters
    with open('../../config/sivers.ini', 'w') as file:
        config.write(file)

    # Close the TPC connections
    del sdr1
    del sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
