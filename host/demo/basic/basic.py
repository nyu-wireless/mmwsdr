import numpy as np
import mmwsdr
import matplotlib.pyplot as plt

"""
Main
"""
def main():
    # Parameters
    nfft = 1024
    nskip = 1024
    ntimes = 1

    # Create the two SDRs
    sdr0 = mmwsdr.sdr.Sivers60GHz(ip=10.115.1.2, debug=True)
    sdr1 = mmwsdr.sdr.Sivers60GHz(ip=10.115.1.2, debug=True)

    # Configure the RFSoC
    sdr0.configure()
    sdr1.configure()

    # Make sure that the nodes are not transmitting
    buf = np.zeros(nfft,1)
    sdr0.send(buf)
    sdr1.send(buf)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass