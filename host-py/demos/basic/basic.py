
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
path = os.path.abspath('../..')
if not path in sys.path:
    sys.path.append(path)
import mmwsdr

"""
Main
"""

def main():
    # Parameters
    nfft = 1024
    nskip = 1024
    ntimes = 1
    is_debug = True

    # Create the two SDRs
    sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', unit_name='SN0243', is_debug=is_debug)
    sdr1 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.4', unit_name='SN0240', is_debug=is_debug)

    # Configure the RFSoC
    sdr0.fpga.configure('../../config/rfsoc.cfg')
    sdr1.fpga.configure('../../config/rfsoc.cfg')

    # Make sure that the nodes are not transmitting
    buf = np.zeros((nfft, 1))
    sdr0.send(buf)
    sdr1.send(buf)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
