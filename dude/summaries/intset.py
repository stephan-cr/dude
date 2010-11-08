# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import generic_summary
class Intset(generic_summary.LineSelect):
    def __init__(self, name, groupby):
        generic_summary.LineSelect(name = name, groupby = groupby,
                                   split = lambda line: line.split(':')[1].split('(')[1].split(' ')[0],
                                   regex = '^#txs', header = 'txs')
