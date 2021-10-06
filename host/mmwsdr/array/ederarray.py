import os
import sys
import argparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse

path = os.path.abspath('/root/mmwsdr/lib/ederenv/Eder_A/')
if path not in sys.path:
    sys.path.append(path)
import eder


class EderArray(object):
    """

    """

    def __init__(self, init=True, unit_name='SN0240', board_type='MB1', eder_version='2'):
        """

        :param init:
        :type init: bool
        :param unit_name:
        :type unit_name: str
        :param board_type:
        :type board_type: str
        :param eder_version:
        :type eder_version: str
        """
        self.array = eder.Eder(init=init, unit_name=unit_name, board_type=board_type, eder_version=eder_version)
        self.array.check()

    @property
    def freq(self):
        """
        Get the carrier frequency of the SDR

        :return: The carrier frequency in Hz
        :rtype: float
        """
        ref_freq = 45e6
        divn = self.array.regs.rd('pll_divn')
        return (divn + 36) * 6 * ref_freq

    @freq.setter
    def freq(self, fc):
        """
        Set the SDR carrier frequency

        :param freq: Carrier frequency in Hz
        :type freq: float
        """
        self.array.pll.set(fc)

    @property
    def mode(self):
        """
        Get the Sivers' array mode

        :return: 'RX' in receive mode or TX' in transmit mode
        :rtype: str
        """
        return self.array.mode

    @mode.setter
    def mode(self, array_mode):
        """
        Set the Sivers' array mode

        :param array_mode: 'RX' for receive mode or TX' for transmit mode
        :type array_mode: str
        """
        if array_mode == 'TX':
            self.array.run_tx(freq=self.freq)
            self.array.tx.dco.run()
            self.array.tx.regs.wr('tx_bb_ctrl', 0x17)
            self.array.tx.regs.wr('tx_bf_gain', 0x0e)
            self.array.tx.regs.wr('tx_rf_gain', 0x0e)
            self.array.tx.regs.wr('tx_bb_gain', 0x03)
        elif array_mode == 'RX':
            self.array.run_rx(freq=self.freq)
            self.array.rx.dco.run()
            self.array.rx.regs.wr('rx_bf_rf_gain', 0xee)

    @property
    def beam_index(self):
        """
        Get the SDR beamforming (BF) vector

        :return: Index of the RX or TX BF vector (row of the RX BF AWV Table)
        :rtype: int
        """
        return self.__beam_index

    @beam_index.setter
    def beam_index(self, index):
        """
        Set the receive (RX) and transmit (TX) beamforming (BF) vectors.

        :param index: Index of the RX BF vector (row of the RX BF AWV Table)
        :type index: int
        """
        self.__beam_index = index
        self.array.tx.set_beam(index)
        self.array.rx.set_beam(index)


def CreateEderHandler(array):
    """

    :param array: Array object to control over HTTP
    :type array: EderArray
    :return:
    :rtype:
    """

    class EderServerHandler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            self.array = array
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_GET(self):
            # Create the response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Parse the URL
            url = urlparse.urlparse(self.path)  # Parse the URL
            request = url.path.split('/')[1]  # Find the request
            param = urlparse.parse_qs(url.query)  # Find the parameters

            # Serve the valid requests
            if request == 'setup':
                self.array.mode = param['mode'][0]
                self.wfile.write(self.array.mode)
            elif request == 'setfreq':
                self.array.freq = float(param['freq'][0])
                self.wfile.write(self.array.freq)
            elif request == 'setbeam':
                self.array.beam_index = int(param['index'][0])
                self.wfile.write(self.array.beam_index)
            elif request == 'beamsweep':
                start = int(param['start'][0])
                stop = int(param['stop'][0])
                step = int(param['step'][0])
                for idx in range(start, stop, step):
                    self.array.tx.bf.awv.set(idx)
            else:
                self.wfile.write('Error\n')
                return

            self.wfile.write('\n')
            return

    return EderServerHandler


def main():
    """
    Simple HTTP Interface to connect to the Eder Array
    :return:
    :rtype:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='port', default=8000, type=int,
                        help='HTTP server port to listen for Eder requests')
    parser.add_argument('-u', dest='unit_name', metavar='UNIT', default='SN0240',
                        help='The serial number of the MB1 unit.')
    args = parser.parse_args()

    # Create the Array Object
    array = EderArray(unit_name=args.unit_name)

    # Create and start the HTTP Server to listen on all interfaces
    httpd = HTTPServer(('0.0.0.0', args.port), CreateEderHandler(array))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Received termination signal from user. Shutting down...')

    # Close the connection
    httpd.shutdown()
    httpd.socket.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
