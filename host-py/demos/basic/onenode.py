
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
    #
    # 10.113.6.3 SN0240
    # 10.113.6.4 SN0243
    sdr0 = mmwsdr.sdr.Sivers60GHz(ip='10.113.6.3', unit_name='SN0240', is_debug=is_debug)

    # Configure the RFSoC
    sdr0.fpga.configure('../../config/rfsoc.cfg')

    # Make sure that the nodes are not transmitting
    txtd = np.zeros((nfft, 1))
    sdr0.send(txtd)

    # Receive some data
    rxtd = sdr0.recv(nfft,nskip,ntimes)
    plt.plot(rxtd.real)
    plt.plot(rxtd.imag)
    plt.show()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
