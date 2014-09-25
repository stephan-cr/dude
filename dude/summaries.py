"""
  Summaries
  ~~~~~~~~~

  A set of generic summaries.
"""
import os
import glob
import re

class SummaryBase:
    """
    Base class for summaries.

    :param name: prefix of output filename
    :param groupby: groupby dimensions
    :param header: columns string separated by spaces
    :param quiet: be quiet
    """
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
        s = ' '.join([str(optpt[k]) for k in keys] + [str(arg) for arg in args])
        return s

    def quiet(self):
        return self._quiet

### Text summaries ------------------------------------------------------------
class LineSelect(SummaryBase):
    """
    Filters and splits lines from stdout/stderr.

    :param files: a list of filenames or a string with wildcards
    :param regex: regex to select lines
    :param split: function to split selected lines, if None, `(lambda l: l)`.
    """
    def __init__(self, name, groupby = [], header = None,
                 regex = '.*', split = None, quiet = False):
        SummaryBase.__init__(self, name, groupby, header, quiet)
        self.regex  = regex
        self.split  = split if split != None else (lambda line: line)

    # def proc(self, optpt, stdout, summary, folder):
    def visit(self, optpt, stdout, group_out):
        re_prog = re.compile(self.regex)
        for l in stdout.readlines():
            if re_prog.match(l):
                print >>group_out, self.format(optpt, self.split(l[:-1]))

class FilesLineSelect(SummaryBase):
    """
    Filters and splits lines from files:

    :param files: a list of filenames or a string with wildcards
    :param regex: regex to select lines
    :param split: function to split selected lines, if None, `(lambda l: l)`.
    :param fname_split: function to split the file names
    :param fname_header: header for filename, default = "fname"
    """
    def __init__(self, name, files, groupby = [], header = None,
                 regex = '.*',
                 split = None,
                 fname_split = None,
                 fname_header = "fname",
#                 has_header=False,
                 quiet = False
                 ):
        SummaryBase.__init__(self, name, groupby,  ' '.join([fname_header, header]), quiet)
        self.regex       = regex
        self.split       = split if split else (lambda line: line)
        self.files       = files
        self.fname_split = fname_split if fname_split else (lambda fname: fname)
        #self.has_header = has_header
        #self.quiet = quiet

    def visit(self, optpt, stdout, group_out):
        if type(self.files) == str:
            files = glob.glob(self.files)
        else:
            assert type(self.files) == list
            files = [glob.glob(f) for f in self.files]
            files = [f for fg in files for f in fg] # flatten

        #if not self.quiet:
        print "FilesLineSelect using files ", files
        re_prog = re.compile(self.regex)

        for fn in files:
            f = open(fn)
            lines_offset = 0 #1 if self.has_header else 0
            fname_split = self.fname_split(fn)
            skip = lines_offset
            for l in f:
                if skip > 0:
                    skip -= 1
                else:
                    if re_prog.match(l):
                        print >>group_out, self.format(optpt, fname_split + ' ' + self.split(l[:-1]))
            f.close()

class MultiLineSelect(SummaryBase):
    """
    Filters and splits lines from stdout with multiple rules

    function to split selected lines, if None, `(lambda l: l)`.

    :param filters: list of (header, regex, split)
    :param fname_split: function to split the file names
    :param fname_header: header for filename, default = "file"
    """
    def __init__(self, name, groupby = [],
                 filters = [("", '.*', (lambda line: line))],
                 quiet = False
                 ):
        header = ' '.join([f[0] for f in filters])
        SummaryBase.__init__(self, name, groupby, header, quiet)
        self.filters   = filters

    def visit(self, optpt, stdout, group_out):
        v = []
        for l in stdout.readlines():
            if v == []:
                # reserve place for pairs
                v = [None] * len(self.filters)
            # check for this line if any of regex matches
            for i in range(0, len(self.filters)):
                (header, regex, split) = self.filters[i]
                if re.match(regex, l):
                    # check if position is empty
                    assert v[i] is None

                    # add value to position
                    v[i] = split(l[:-1])
                    assert v[i] is not None

            complete = not (None in v)
            if complete:
                print >>group_out, self.format(optpt, " ".join(v))
                v = []

class FilesMultiLineSelect(SummaryBase):
    """
    Filters and splits lines from selected files with multiple rules

    :param files: a list of filenames or a string with wildcards
    :param filters: (column, regex, split)
    :param fname_split: function to split the file names
    :param fname_header: header for filename, default = "fname"
    """
    def __init__(self, name, files, groupby = [],
                 filters = [("", '.*', (lambda line: line))],
                 fname_split = (lambda fname: fname),
                 fname_header = "fname",
                 quiet = False
                 ):
        header = [fname_header] + [f[0] for f in filters]
        header = ' '.join(header)
        SummaryBase.__init__(self, name, groupby, header, quiet)
        self.filters = filters
        self.files   = files
        self.fname_split = fname_split

    def visit(self, optpt, stdout, group_out):
        if type(self.files) == str:
            files = glob.glob(self.files)
        else:
            assert type(self.files) == list
            files = [glob.glob(f) for f in self.files]
            files = [f for fg in files for f in fg] # flatten

        if not self.quiet():
            print "FilesMultiLineSelect using files ", files

        for fn in files:
            f = open(fn)
            v = []
            fname_split = self.fname_split(fn)
            for l in f:
                if v == []:
                    # reserve place for pairs
                    v = [None] * len(self.filters)
                # check for this line if any of regex matches
                for i in range(0, len(self.filters)):
                    (header, regex, split) = self.filters[i]
                    if re.match(regex, l):
                        # check if position is empty
                        assert v[i] is None

                        # add value to position
                        v[i] = split(l[:-1])
                        assert v[i] is not None

                complete = not (None in v)
                if complete:
                    print >>group_out, self.format(optpt, ' '.join([fname_split] + v))
                    v = []
            f.close()

### Json summaries ------------------------------------------------------------
import json


class JsonSelect(SummaryBase):
    """Selects entries from a Json file."""
    def __init__(self, name, path, filename, header,
                 groupby = [], quiet = False):
        """
        :param name: prefix of output filename
        :param path: path(s) in Json structure
        :param filename: json file to open
        :param header: columns string separated by spaces
        """
        SummaryBase.__init__(self, name, groupby, header)
        if type(path) == list:
            self.paths = path
        else:
            self.paths = [path]
        assert len(header.split(' ')) == len(self.paths)
        self.filename = filename

    def visit(self, optpt, stdout, group_out):
        if os.path.exists(self.filename):
            if not self.quiet():
                print "JsonSelect:", optpt
            f = open(self.filename)
            jobj = json.load(f)

            objs = []
            for path in self.paths:
                jobj_tmp = jobj
                for x in path.split(os.path.sep):
                    jobj_tmp = jobj_tmp[x]
                objs.append(jobj_tmp)

            s = self.format(optpt, *objs)

            keys = optpt.keys()
            keys.sort()
            s = ''
            for k in keys:
                s += optpt[k] + ' '
            for arg in objs:
                if isinstance(arg, dict):
                    s += ' ' + json.dumps(arg)
                else:
                    s += ' ' + str(arg)

            group_out.write(s)
            f.close()
