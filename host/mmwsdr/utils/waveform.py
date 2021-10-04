import numpy as np


def wideband(sc_min=-100, sc_max=100, nfft=1024, mod='qam', seed=100):
    """

    :param sc_min: minimum subcarrier index
    :type sc_min: int
    :param sc_max: maximum subcarrier index
    :type sc_max: int
    :param nfft: num of FFT points
    :type nfft: int
    :param mod: frequency domain symbol modulation
    :type mod: str
    :param seed:
    :type seed: int
    :return:
    :rtype:
    """
    np.random.seed(seed)
    qam = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)  # QAM symbols

    # Create the wideband sequence in frequency-domain
    fd = np.zeros((nfft,), dtype='complex')
    if mod == 'qam':
        fd[((nfft >> 1) + sc_min):((nfft >> 1) + sc_max)] = np.random.choice(qam, len(range(sc_min, sc_max)))
    else:
        fd[((nfft >> 1) + sc_min):((nfft >> 1) + sc_max)] = 1
    fd = np.fft.fftshift(fd, axes=0)

    # Convert the waveform to time-domain
    td = np.fft.ifft(fd, axis=0)

    # Normalize the signal
    td /= np.max([np.abs(td.real), np.abs(td.imag)])


def onetone(sc=400, nfft=1024):
    """

    :param sc: subcarrier index
    :type sc: int
    :param nfft: num of FFT points
    :type nfft: int
    :return: waveform
    :rtype: np.array
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
