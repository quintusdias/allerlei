import itertools

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
            lluv = list(gen)

            gen = itertools.takewhile(lambda x: not x.startswith('%TableEnd:'),
                                      fptr)
            rads1 = list(gen)

            gen = itertools.takewhile(lambda x: not x.startswith('%TableEnd:'),
                                      fptr)
            rcv2 = line(gen)
            footer = fptr.readlines()

        pass

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
