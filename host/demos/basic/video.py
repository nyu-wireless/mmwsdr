"""
"""

# Import Libraries
import os
import sys
import argparse
import numpy as np
import matplotlib
import configparser
import threading

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
    isdebug = True

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default='srv1-in1', help="COSMOS-SB1 node name (i.e., srv1-in1)")
    args = parser.parse_args()

    # Create a configuration parser
    config = configparser.ConfigParser()
    config.read('../../config/sivers.ini')

    xytable0 = mmwsdr.utils.XYTable(config[args.node]['table_name'], isdebug=isdebug)
    xytable0.move(x=float(config[args.node]['x']), y=float(config[args.node]['y']),
                  angle=float(config[args.node]['angle']))

    t = threading.Thread(target=xytable0.video)
    t.start()

    # Create a move
    xytable0.move(x=500, y=500, angle=-45)

    t.join()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
