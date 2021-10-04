"""

"""

# Import Libraries
import os
import sys
import time
import argparse
import matplotlib
import subprocess
import numpy as np
import configparser

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr


def pttrn(sdr_tx, sdr_rx, xytable, x, y):
    nfft = 1024  # num of continuous samples per frame
    nskip = 1024  # num of samples to skip between frames
    nframe = 50  # num of frames

    sc_min = -400  # subcarrier index
    sc_max = 400  # subcarrier index
    tx_pwr = 15000  # transmit power

    naod = 91
    ncode = 64

    aod = np.linspace(-45, 45, naod)

    f = np.linspace(-nfft / 2, nfft / 2 - 1, nfft)  # subcarrier index vector for plotting

    # Generate the tx sequence
    txtd = mmwsdr.utils.waveform.wideband(sc_min=sc_min, sc_max=sc_max, nfft=nfft)
    sdr_tx.send(txtd*tx_pwr)

    # Collect the data
    rxtd = np.zeros((naod, ncode, nframe, nfft))
    for iaod in range(naod):
        print('\n-')
        xytable.move(x=x, y=y, angle=aod[iaod])
        time.sleep(1) # Wait for 1 s
        for icode in range(ncode):
            sys.stdout.write('.')
            sdr_rx.beam_index = icode
            time.sleep(0.1)
            rxtd[iaod, icode] = sdr_rx.recv(nfft, nskip, nframe)

    # Process the data
    rxfd = np.fft.fft(rxtd, axis=3)
    Hest = rxfd * np.conj(np.fft.fft(txtd))
    hest = np.fft.ifft(Hest, axis=3)

    # keep only the maximum peak
    max_peak = np.max(np.abs(hest), axis=3)
    sum_peak = np.sum(max_peak, axis=2)
    pwr = np.max(sum_peak, axis=1)

    plt.plot(aod, 20*np.log10(pwr))
    plt.xlabel('Angle of departure [Deg]')
    plt.ylabel('Power [dB]')
    plt.tight_layout()
    plt.grid()
    plt.show()

def main():
    """

    :return:
    :rtype:
    """

    # Parameters
    iscalibrated = True  # apply rx and tx calibration factors
    isdebug = True  # print debug messages

    # Reload the FTDI drivers to ensure communication with the Sivers' array
    subprocess.call("../../scripts/sivers_ftdi.sh", shell=True)

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="Carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='srv1-in1', help="COSMOS-SB1 node name (i.e., srv1-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="SDR mode (i.e., rx)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    # Create the SDR
    sdr1 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in1', freq=args.freq,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in1'), iscalibrated=iscalibrated)

    sdr2 = mmwsdr.sdr.Sivers60GHz(config=config, node='srv1-in2', freq=args.freq,
                                  isdebug=isdebug, islocal=(args.node == 'srv1-in2'), iscalibrated=iscalibrated)

    if config['srv1-in1']['table_name'] != None:
        xytable1 = mmwsdr.utils.XYTable(config['srv1-in1']['table_name'], isdebug=isdebug)
        xytable1.move(x=float(config['srv1-in1']['x']), y=float(config['srv1-in1']['y']),
                      angle=float(config['srv1-in1']['angle']))

    if config['srv1-in2']['table_name'] != None:
        xytable2 = mmwsdr.utils.XYTable(config['srv1-in2']['table_name'], isdebug=isdebug)
        xytable2.move(x=float(config['srv1-in2']['x']), y=float(config['srv1-in2']['y']),
                      angle=float(config['srv1-in2']['angle']))


    for it in range(2):
        if it == 0:
            pttrn(sdr1, sdr2, xytable1, float(config['srv1-in1']['x']), float(config['srv1-in1']['y']))
        else:
            pttrn(sdr2, sdr1, xytable2, float(config['srv1-in2']['x']), float(config['srv1-in2']['y']))

    # Close the TPC connections
    del sdr1
    del sdr2


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
