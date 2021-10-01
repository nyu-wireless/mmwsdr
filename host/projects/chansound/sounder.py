"""

"""

# Import Libraries
import os
import sys
import argparse
import time

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

    :return:
    :rtype:
    """
    # Parameters
    naoa = 91
    nfft = 1024  # num of continuous samples per batch
    nskip = 2*1024  # num of samples to skip between batches
    nbatch = 100  # num of batches
    isdebug = True  # print debug messages
    iscalibrated = True  # print debug messages
    sc_min = -450  # min subcarrier index
    sc_max = 450  # max subcarrier index
    tx_pwr = 15000  # transmit power
    qam = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)

    # Find the angles of arrival
    aoa = np.linspace(-45, 45, naoa)

    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, default=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, default='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    parser.add_argument("--mode", type=str, default='rx', help="sdr mode (i.e., rx)")
    args = parser.parse_args()

    # Create an SDR object and the XY table
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=args.freq, unit_name='SN0240', isdebug=isdebug,
                                      iscalibrated=iscalibrated)
        xytable0 = mmwsdr.utils.XYTable('xytable1', isdebug=isdebug)

        # Move the SDR to the lower-right corner
        xytable0.move(x=0, y=0, angle=0)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=args.freq, unit_name='SN0243', isdebug=isdebug,
                                      iscalibrated=iscalibrated)
        xytable0 = mmwsdr.utils.XYTable('xytable2', isdebug=isdebug)

        # Move the SDR to the lower-left conrner
        xytable0.move(x=1300, y=0, angle=0)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    # Configure the RFSoC
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Use the same seed for Tx and Rx. This will ensure a common pseudo-random sequence for both sides.
    np.random.seed(100)

    # Create the tx signal (in frequency domain)
    txfd = np.zeros((nfft,), dtype='complex')
    txfd[((nfft >> 1) + sc_min):((nfft >> 1) + sc_max)] = np.random.choice(qam, len(range(sc_min, sc_max)))

    # Main loop
    while (1):
        if args.mode == 'tx':
            txfd = np.fft.fftshift(txfd, axes=0)
            txtd = np.fft.ifft(txfd, axis=0)
            txtd = txtd / np.max([np.abs(txtd.real), np.abs(txtd.imag)]) * tx_pwr
            sdr0.send(txtd)

        elif args.mode == 'rx':
            rx_pwr = np.zeros((naoa,))

            for iaoa in range(naoa):
                # Change the angle of arrival (AoA)
                xytable0.move(x=1300, y=0, angle=aoa[iaoa])
                time.sleep(2)

                # Receive data
                rxtd = sdr0.recv(nfft, nskip, nbatch)

                # Estimate the channel
                rxfd = np.fft.fft(rxtd, axis=1)
                Hest = rxfd * np.conj(txfd)
                hest = np.fft.ifft(Hest, axis=1)

                # Find the position of the first peak
                pos = np.argmax(np.abs(hest)**2, axis=1)
                rx_pwr[iaoa] = np.sum(np.abs(hest[:,pos]))

                # In debug mode plot the impulse response
                if isdebug:
                    t = np.arange(nfft) / sdr0.fs / 1e-9
                    plt.plot(t, 20 * np.log10(np.abs(hest[0, :]) / np.max(np.abs(hest[0, :]))))
                    plt.xlabel('Delay [ns]')
                    plt.ylabel('Magnitude [dB]')
                    plt.tight_layout()
                    plt.grid()
                    plt.show()

                    Hest = np.fft.fftshift(Hest, axis=1)
                    plt.imshow(np.abs(Hest.T), aspect='auto', interpolation='none')
                    plt.xlabel('Frame index')
                    plt.ylabel('Subcarrier index')
                    plt.show()

            # Normalize the received power
            rx_pwr /= np.max(rx_pwr)

            # Plot the results
            plt.plot(aoa, 20 * np.log10(rx_pwr))
            plt.xlabel('Angle of arrival [Deg]')
            plt.ylabel('Power [dB]')
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
