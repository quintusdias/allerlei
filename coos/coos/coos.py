import itertools
import re

import numpy as np
import pandas as pd

class CodarRadials(object):
    """CODAR radials.
    """
    def __init__(self):
        pass

    def parse(self, ascii_file):
        """Parse ASCII radials file.

        Parameters
        ----------
        ascii_file : str
            Path to ASCII radials file.
        """
        with open(ascii_file, 'r', encoding='latin1') as fptr:
            # Iterate thru the file until hitting the end of the table section.
            gen = itertools.takewhile(lambda x: not x.startswith('%TableEnd:'),
                                      fptr)
            lst = list(gen)
            data, attrs = self.process_lluv(lst)
            import pdb; pdb.set_trace()

            gen = itertools.takewhile(lambda x: not x.startswith('%TableEnd:'),
                                      fptr)
            rads1 = list(gen)

            gen = itertools.takewhile(lambda x: not x.startswith('%TableEnd:'),
                                      fptr)
            rcv2 = line(gen)
            footer = fptr.readlines()

        pass

    def process_lluv(self, lst):
        """
        Process section of data file with lat, lon, u, and v components.
        """

        # The column names are in the first line starting with '%%'
        line = [x for x in lst if x.startswith('%%')][0]
        # Get rid of the newline.
        line = line.strip(chr(10))
        names = re.split('\s\s+', line)
        # Leading '%%' does not count as a column.
        names = names[1:]

        # The column units (some of them) are in the second line starting
        # with '%%'
        line = [x for x in lst if x.startswith('%%')][1]
        # Get rid of the newline.
        line = line.strip(chr(10))
        names = re.split('\s\s+', line)
        # Leading '%%' does not count as a column.
        units = names[1:]

        # The lines of actual data do NOT start with '%'
        data_lines = [x for x in lst if not x.startswith('%')]
        data = np.zeros((len(data_lines), 18), dtype=np.float64)
        for idx, line in enumerate(data_lines):
            line_data = np.fromstring(line, sep=' ')
            data[idx] = line_data


    def parse_header(self, fptr):
        """
        """
        while True:
            line = fptr.readline()

    def write_netcdf(self, netcdf_file):
        pass

    def plot(self):
        pass

    def __str__(self):
        pass
