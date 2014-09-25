# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""
Utility functions to handle lists and dictionaries.
"""
import errno
import os
import sys

def cartesian(sets):
    return __cartesian(sets, 0, {})

# result = __cartesian(sets, 0, {})
def __cartesian(sets, i, element):
    keys = sets.keys()
    if i == len(keys):
        return [element.copy()]
    else:
        product = []
        for value in sets[keys[i]]:
            element[keys[i]] = value
            product += __cartesian(sets, i+1, element)
    return product


# Check Folder
def checkFolder(folder):
    try:
        os.makedirs(folder)
    except OSError as e:
        # if directory already exists: fine
        if e.errno != errno.EEXIST: # file exists
            raise


# groupBy()
# groups the measurements by options
def groupBy(measurements, options):
    subsets = []
    __groupByRecursiveFor(options, 0, {}, measurements, subsets)
    return subsets

def __groupByRecursiveFor(d, i, options, set, subsets):
    keys = d.keys()
    if i == len(keys):
        subsets.append((options.copy(), getSubset(set, options)))
    else:
        for value in map(str,d[keys[i]]):
            options[keys[i]] = value
            __groupByRecursiveFor(d, i+1, options, set, subsets)

def getSubset(set, options):
    subset = []
    for e in set:
        if matchLeft(e, options):
            subset.append(e)
    return subset

def matchLeft(left, right):
    for k in right.keys():
        if str(left[k]) != str(right[k]):
            return False
    return True

def select(options, selection):
    s = {}
    for k in selection:
        assert k in options
        s[k] = options[k]
    return s

def unselect(options, unselection):
    s = {}
    assert type(unselection) == list
    for k in options.keys():
        if k not in unselection:
            s[k] = options[k]
    return s

def pick(options, selection):
    s = []
    for k in selection:
        assert k in options
        s.append(options[k])
    return tuple(s)

def chop(l, r):
    """
    Removes from list `l` all items in the intersection between lists `l` and `r`.
    """
    assert type(l) == list
    assert type(r) == list
    q = l[:] # [:] copies a list
    for e in r:
        q.remove(e)
    return q



# Mean class
class Mean:
    def __init__(self, alfa = 0.2):
        self.sum = 0
        self.alfa = alfa
        self.last = 0
        self.total = 0

    def add(self, num):
        self.last = num
        self.total += num
        self.sum = self.alfa*self.sum + (1-self.alfa)*num

    def mean(self):
        return self.sum

    def getLast(self):
        return self.last

    def getTotal(self):
        return self.total

def strColumns(columns, cols_size):
    s = ''
    for i in range(0,len(columns)):
        c  = columns[i]
        sz = cols_size[i]
        blanks = sz - len(c)
        s += ' '*blanks + c + ' '
    return s


# Time convert
def sec2string(sec):
    s = sec % 60
    m = (sec/60)%60
    h = sec/60/60
    return "%dh%dm%ds" %(h,m,s)


import tty, termios
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSANOW, old)
    return ch


import optparse
import textwrap

"""code from http://groups.google.com/group/comp.lang.python/browse_frm/thread/6df6e6b541a15bc2/09f28e26af0699b1?pli=1"""
class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):

    def format_description(self, description):
        if not description: return ""
        desc_width = self.width - self.current_indent
        indent = " "*self.current_indent
        # the above is still the same
        bits = description.split('\n')
        formatted_bits = [
            textwrap.fill(bit,
                          desc_width,
                          initial_indent=indent,
                          subsequent_indent=indent)
            for bit in bits]
        result = "\n".join(formatted_bits) + "\n"
        return result

    def format_option(self, option):
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #   eg. ("turn on expert mode", "read data from FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x    turn on expert mode
        #
        # But if the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in if it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #       read data from FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else: # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            # Everything is the same up through here
            help_lines = []
            for para in help_text.split("\n"):
                help_lines.extend(textwrap.wrap(para, self.help_width))
                # Everything is the same after here
            result.append("%*s%s\n" % (
                    indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)

def parse_value(v):
    v = str(v).strip()
    if v == 'True': return True
    if v == 'False': return False
    try:
        return int(v)
    except:
        return v

def parse_str_list(l):
    ls = l.split('[')
    assert len(ls) == 2
    ls = ls[1].split(']')
    assert len(ls) == 2
    ls = ls[0].split(',')
    r = []
    # remove empty entries
    for l in ls:
        if not l == '':
            r.append(parse_value(l))
    return r


class Tee(object):
    def __init__(self, name, mode):
        """BUG: fileno is necessary when for Popen in execute.py. We use stdout.fileno."""
        self.file   = open(name, mode)
        self.stdout = sys.stdout
        #sys.stdout  = self
        self.fileno = self.stdout.fileno

    def __del__(self):
        sys.stdout  = self.stdout
        #if self.file: self.file.close()

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def close(self):
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
