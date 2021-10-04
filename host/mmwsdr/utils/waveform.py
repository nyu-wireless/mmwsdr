import numpy as np


def onetone(sc=400, nfft=1024):
    """

    :param sc: subcarrier index
    :type sc: int
    :param nfft: num of FFT points
    :type nfft: int
    :return:
    :rtype:
    """
    # Create a tone in frequency-domain
    fd = np.zeros((nfft,), dtype='complex')
    fd[(nfft >> 1) + sc] = 1
    fd = np.fft.fftshift(fd, axes=0)

    # Convert the waveform to time-domain
    td = np.fft.ifft(fd, axis=0)

    # Normalize the signal
    td /= np.max([np.abs(td.real), np.abs(td.imag)])
    return td
