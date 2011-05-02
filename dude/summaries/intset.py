# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import generic_summary

def split_line(line):
    return line.split(':')[1].split('(')[1].split(' ')[0]

class Intset(generic_summary.LineSelect):
    def __init__(self, name, groupby):
        generic_summary.LineSelect.__init__(self, name = name,
                                            groupby = groupby,
                                            split = split_line,
                                            regex = '^#txs', header = 'txs')
