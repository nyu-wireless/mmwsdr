"""
:description: In this demo, we show a frequency-domain channel sounder at 60 GHz. We generate N_FFT symbols in
frequency-domain. We generate a wide-band sequence filling [sc_min, sc_max] sub-carries with random 4-QAM symbols. We
use IFFT to get the time-domain TX sequence. We transmit the data from SDR1 with cyclic repeat. We receive 100 frames
of N_FFT data from SDR2. The user can select to save or process the data. When we process the data

In this demo we control a single SDR node. We create an SDR object and an XY-Table object using the
`mmwsdr` library. The SDR object configures and controls a Xilinx RFSoC ZCU111 eval board and a Sivers IMA transceiver
board. A user can provide arguments to the script, such as the carrier frequency, the COSMOS node id and the transceiver
mode. The script by default starts a local connection with a carrier frequency at 60.48 GHz in receive mode.

We use two SDR devices connected
to the same computer. We generate $N_\mathrm{FFT}$ symbols in frequency domain. We fill the $[sc_\mathrm{min}, sc_\mathrm{max}]$
subcarriers with random 4-QAM symbols. We use IFFT to get the time-domain TX sequence. We
transmit the data from $\mathrm{SDR}_0$ with cyclic repeat. We receive 16 frames of $N_\mathrm{FFT}$ data from $\mathrm{SDR}_1$.
We perform correlation and plot the estimated channel impule response.


:organization: New York University
:author: Panagiotis Skrimponis

:copyright: 2021
"""
# Import Libraries
import os
import sys
import time
import socket
import argparse
import configparser
import subprocess

import numpy as np
import matplotlib

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
    file_id = 0  # file id
    nfft = 1024  # num of continuous samples per frames
    nskip = 2 * 1024  # num of samples to skip between frames
    nframe = 100  # num of frames
    issave = True  # save the received IQ samples
    isprocess = True  # process the received IQ samples
    isdebug = True  # print debug messages
    iscalibrated = True  # apply calibration parameters
    sc_min = -250  # min sub-carrier index
    sc_max = 250  # max sub-carrier index
    tx_pwr = 15000  # transmit power

    node = socket.gethostname().split('.')[0]  # Find the local hostname

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create the SDR objects
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=args.freq,
                                  isdebug=isdebug, islocal=(node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=args.freq,
                                  isdebug=isdebug, islocal=(node == 'srv1-in2'), iscalibrated=iscalibrated)

    # Create the XY table controllers. Load the default location.
    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))

    # Create a wide-band tx signal
    txtd = mmwsdr.utils.waveform.wideband(sc_min=sc_min, sc_max=sc_max, nfft=nfft)

    # Main loop
    while (1):
        # Send data
        sdr1.send(txtd*tx_pwr)

        # Receive data
        rxtd = sdr2.recv(nfft, nskip, nframe)

        # Process the received data
        if isprocess:
            # Estimate the channel
            rxfd = np.fft.fft(rxtd, axis=1)
            Hest = rxfd * np.conj(np.fft.fft(txtd))
            hest = np.fft.ifft(Hest, axis=1)

            t = np.arange(nfft) / sdr2.fpga.fs / 1e-9
            plt.plot(t, 20 * np.log10(np.abs(hest[0, :]) / np.max(np.abs(hest[0, :]))))

            plt.xlabel('Delay (ns)', fontsize=13)
            plt.ylabel('Magnitude (dB)', fontsize=13)
            plt.tight_layout()
            plt.grid()
            plt.show()

            Hest = np.fft.fftshift(Hest, axes=1)
            plt.imshow(np.abs(Hest.T), aspect='auto', interpolation='none')
            plt.xlabel('Frame index')
            plt.ylabel('Subcarrier index')
            plt.show()

        # Save the data
        if issave:
            np.savez_compressed('sounder_{}'.format(file_id), rxtd=rxtd)

        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n press enter to continue ")
        else:
            ans = input("Enter 'q' to exit or\n press enter to continue ")

        if ans == 'q':
            break

    # Delete the SDR object. Close the TCP connections.
    del sdr1, sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
