"""

"""

# Import Libraries
import os
import sys
import argparse
import numpy as np

path = os.path.abspath('../../')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr

# Parameters
sc = 400  # subcarrier index
nfft = 1024  # num of continuous samples
tx_pwr = 10000  # transmit power
isdebug = True  # print debug messages


def main():
    """

    :return:
    :rtype:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, nargs='?', const=60.48e9, help="receiver carrier frequency in Hz (i.e., 60.48e9)")
    parser.add_argument("--node", type=str, nargs='?', const='sdr2-in1', help="cosmos-sb1 node name (i.e., sdr2-in1)")
    args = parser.parse_args()

    # Create an SDR object
    if args.node == 'sdr2-in1':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', freq=args.freq, unit_name='SN0240', isdebug=isdebug)
    elif args.node == 'sdr2-in2':
        sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', freq=args.freq, unit_name='SN0243', isdebug=isdebug)
    else:
        raise ValueError("COSMOS node can be either 'sdr2-in1' or 'sdr2-in2'")

    sdr0.fpga.configure('../../config/rfsoc.cfg')

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

    while (1):
        if sys.version_info[0] == 2:
            ans = raw_input("Enter 'q' to exit or\n Enter beam index: ")
        else:
            ans = input("Enter 'q' to exit or\n Enter beam index: ")

        if ans == 'q':
            break
        elif ans.isdigit():
            sdr0.beam_index = int(ans)

    # Close the TPC connections
    del sdr0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
