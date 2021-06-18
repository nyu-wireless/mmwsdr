# -*- coding: utf-8 -*-
"""
@description: This class creates an object to control
the XYTable/s of the COSMOS Testbed

@authors: Panagiotis Skrimponis
          Tommy Azzino

@organization: New York University

@copyright 2021
"""
import requests


class XYTable(object):
    """
    XY Table class
    """
    def __init__(self, table_name):
        self.table_name = table_name  # either xytable1 or xytable2 (enum)

    def __del__(self):

    def get_status(self):

    def move(self):

    def stop(self):


