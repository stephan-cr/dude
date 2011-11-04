# Copyright (c) 2011 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

class SummaryBase:
    """Base class for new summaries."""

    def __init__(self, name, groupby = [], header = None, quiet = False):
        self._name = name
        self._groupby = groupby
        self._header = header
        self._quiet = quiet

    def name(self):
        return self._name

    def header(self, dimensions):
        if self._header:
            if type(dimensions) == list:
                dimensions.sort()
                dimensions = ' '.join(dimensions)
            return dimensions + ' ' + self._header
        else:
            return None

    def groupby(self):
        return self._groupby
    
    def format(self, optpt, *args):
        #assert len(values.split(' ')) == len(self.header.split(' '))
        keys = optpt.keys()
        keys.sort()
        s = ''
        for k in keys:
            s += optpt[k] + ' '
        for arg in args:
            s += ' ' + str(arg)
        return s

    def quiet(self):
        return self._quiet
