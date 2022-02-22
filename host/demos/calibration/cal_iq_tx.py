"""
:description: In this demo, we show the transmitter IQ calibration.

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
import math
import configparser
import subprocess

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr


def cal(sdr_tx, sdr_rx):
    # Parameters
    nvhypo = 101  # num of v hypothesis
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024 * 5  # num of samples to skip between frames
    nframe = 100  # num of frames
    isdebug = True  # print debug messages
    tx_pwr = 12000  # transmit power
    sc = 422  # rx subcarrier index

    sdr_tx.freq = 60.48e9
    sdr_rx.freq = 60.48e9

    # Generate the tx sequence
    txtd = mmwsdr.utils.waveform.onetone(sc=sc, nfft=nfft) * tx_pwr

    pwr = np.zeros((2,))
    for it in range(2):
        if it == 0:
            sdr_tx.send(txtd.real)
        else:
            sdr_tx.send(txtd.imag)
        rxtd = sdr_rx.recv(nfft, nskip, nframe)
        rxtd = sdr_rx.apply_iq_cal(td=rxtd, a=sdr_rx.cal_iq_rx_a, v=sdr_rx.cal_iq_rx_v)

        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)

        fd = np.zeros_like(rxfd)
        fd[:, (nfft >> 1) + sc] = rxfd[:, (nfft >> 1) + sc]
        fd[:, (nfft >> 1) - sc] = rxfd[:, (nfft >> 1) - sc]
        fd = np.fft.fftshift(fd, axes=1)
        td = np.fft.ifft(fd, axis=1)
        pwr[it] = np.sum(np.sqrt(np.mean(np.abs(td) ** 2, axis=1)))

    a = pwr[0] / pwr[1]

    sdr_tx.freq = 61.29e9

    vhypos = np.linspace(-1, 1, nvhypo)
    sbs = np.zeros((nvhypo,))

    # Calculate the v
    for ivhypo in range(nvhypo):
        v = vhypos[ivhypo]
        re = (1 / a) * txtd.real
        im = ((-1) * re * math.tan(v)) + (txtd.imag / math.cos(v))
        sdr_tx.send(re + 1j * im)

        rxtd = sdr_rx.recv(nfft, nskip, nframe)
        rxtd = sdr_rx.apply_iq_cal(td=rxtd, a=sdr_rx.cal_iq_rx_a, v=sdr_rx.cal_iq_rx_v)
        rxfd = np.fft.fft(rxtd, axis=1)
        rxfd = np.fft.fftshift(rxfd, axes=1)
        sbs[ivhypo] = np.sum(np.abs(rxfd[:, (nfft >> 1) + sc]), axis=0)

    m = sbs / np.min(sbs)

    v = vhypos[np.argmin(m)]

    if isdebug:
        plt.plot(vhypos, 20 * np.log10(m))
        plt.grid()
        plt.xlabel('Sideband suppression [dB]')
        plt.xlabel('TX IQ quadradure phase error [rad]')
        plt.show()

    return a,v


def main():
    """
    Main function
    """

    # Parameters
    nsdr = 2  # num of SDR nodes to calibrate
    isdebug = True  # print debug messages
    iscalibrated = False  # apply rx and tx calibration factors

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default='srv1-in1', help="COSMOS-SB1 node name (i.e., srv1-in1)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create the SDR
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=61.29e9,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=60.48e9,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in2'), iscalibrated=iscalibrated)

    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))

    for isdr in range(nsdr):
        if isdr == 0:
            a, v = cal(sdr1, sdr2)
            config['srv1-in1']['cal_iq_rx_a'] = str(a)
            config['srv1-in1']['cal_iq_rx_v'] = str(v)

        else:
            a, v = cal(sdr2, sdr1)
            config['srv1-in2']['cal_iq_rx_a'] = str(a)
            config['srv1-in2']['cal_iq_rx_v'] = str(v)

        # Plot the parameters
        print('Alpha: {}'.format(a))
        print('V: {}'.format(v))

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
