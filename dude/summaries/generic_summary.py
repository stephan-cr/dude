# Copyright (c) 2010, 2011 Diogo Becker, Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

""" Summaries """
import os
import re
import glob

class LineSelect:
    def __init__(self, name, groupby = [], header = None,
                 regex = '.*', split = (lambda line: line) ):
        self.name = name
        self.groupby = groupby
        self.header = header
        self.regex  = regex
        self.split  = split

    def proc(self, optpt, stdout, summary, folder):
        keys = optpt.keys()
        keys.sort()
        s = ''
        for k in keys:
            s += optpt[k] + ' '

        re_prog = re.compile(self.regex)
        for l in stdout.readlines():
            if re_prog.match(l):
                print >>summary, s + self.split(l[:-1])
    # s =''
    # for d in dimensions:
    #     s += str(dimensions[d]) + ' '
    # for l in stdout.readlines():
    #     if len(l) > 1:
    #         print >>summary, s + l.split(':>')[1][:-1]

    def as_dict(self, cfg):
        s = {
            'name' : self.name,
            'dimensions' : cfg.optspace.keys(),
            'groupby' : self.groupby,
            'process' : lambda a,b,c,d: LineSelect.proc(self, a, b, c, d)
            }
        if self.header == None:
            s['header'] = lambda h: ""
        elif self.header.__class__ == "".__class__:
            s['header'] = lambda h: h + self.header
        else:
            s['header'] = self.header
        return s



class FilesLineSelect:
    """ Document this!!! """
    def __init__(self, name, files, groupby = [], header = None,
                 regex = '.*', split = (lambda line: line),
                 fname_split = (lambda fname: fname),
                 fname_header = None,
                 has_header=False,
                 quiet = False
                 ):
        self.name = name
        self.groupby = groupby
        self.header = header
        self.regex  = regex
        self.split  = split
        self.files  = files
        self.fname_split = fname_split
        self.fname_header = fname_header
        self.has_header = has_header
        self.quiet = quiet


    def proc(self, optpt, stdout, summary, folder):
        keys = optpt.keys()
        keys.sort()
        s = ''
        for k in keys:
            s += optpt[k] + ' '

        if self.files.__class__ == "".__class__:
            files = glob.glob(self.files)
        else:
            assert self.files.__class__ == [].__class__

        if not self.quiet:
            print "FilesLineSelect using files ", files
        re_prog = re.compile(self.regex)

        for fn in files:
            f = open(fn)
            lines_offset = 1 if self.has_header else 0
            fname_split = self.fname_split(fn)
            skip = lines_offset
            for l in f:
                if skip > 0:
                    skip -= 1
                else:
                    if re_prog.match(l):
                        print >>summary, s + fname_split + ' ' + self.split(l[:-1])
            f.close()

    def as_dict(self, cfg):
        s = {
            'name' : self.name,
            'dimensions' : cfg.optspace.keys(),
            'groupby' : self.groupby,
            'process' : lambda a,b,c,d: FilesLineSelect.proc(self, a, b, c, d)
            }
        if self.header == None:
            s['header'] = lambda h: ""
        elif self.header.__class__ == "".__class__:
            if self.fname_header == None:
                s['header'] = lambda h: h  + ' file ' + self.header
            else:
                s['header'] = lambda h: h  + self.fname_header + ' ' + self.header
        else:
            assert False # not implemented. this does not work because of 'file' column
            s['header'] = self.header
        return s


    def summarize(self, fd, folder = '.'):
        wd = os.getcwd()
        os.chdir(folder)
        self.proc({}, None, fd, None)
        os.chdir(wd)


class MultiLineSelect:
    def __init__(self, name, groupby = [],
                 filters = [("", '.*', (lambda line: line))] ):
        self.name    = name
        self.groupby = groupby
        self.filters   = filters

    def proc(self, optpt, stdout, summary, folder):
        keys = optpt.keys()
        keys.sort()
        s = ''
        for k in keys:
            s += optpt[k] + ' '

        v = []
        for l in stdout.readlines():
            if v == []:
                # reserve place for pairs
                for i in range(0, len(self.filters)):
                    v.append(None)
            # check for this line if any of regex matches
            for i in range(0, len(self.filters)):
                (header, regex, split) = self.filters[i]
                if re.match(regex, l):
                    # check if position is empty
                    assert v[i] == None

                    # add value to position
                    v[i] = split(l[:-1])
                    assert v[i] != None

            complete = True
            for p in v:
                if p == None:
                    complete = False
                    break
            if complete:
                print >>summary, s + " ".join(v)
                v = []

    def as_dict(self, cfg):
        s = {
            'name' : self.name,
            'dimensions' : cfg.optspace.keys(),
            'groupby' : self.groupby,
            'process' : lambda a,b,c,d: MultiLineSelect.proc(self, a, b, c, d)
            }
        header = []
        for (h,r,x) in self.filters:
            header.append(h)
        header = " ".join(header)
        s['header'] = lambda h: h + header
        return s

class FilesMultiLineSelect:
    """ Document this!!! """
    def __init__(self, name, files, groupby = [],
                 filters = [("", '.*', (lambda line: line))],
                 fname_split = (lambda fname: fname),
                 fname_header = None
                 ):
        self.name    = name
        self.groupby = groupby
        self.filters = filters
        self.files   = files
        self.fname_split = fname_split
        self.fname_header = fname_header

    def proc(self, optpt, stdout, summary, folder):
        keys = optpt.keys()
        keys.sort()
        s = ''
        for k in keys:
            s += optpt[k] + ' '


        if self.files.__class__ == "".__class__:
            files = glob.glob(self.files)
        else:
            assert self.files.__class__ == [].__class__

        print "FilesMultiLineSelect using files ", files
        for fn in files:
            f = open(fn)
            v = []
            for l in f:
                if v == []:
                    # reserve place for pairs
                    for i in range(0, len(self.filters)):
                        v.append(None)
                # check for this line if any of regex matches
                for i in range(0, len(self.filters)):
                    (header, regex, split) = self.filters[i]
                    if re.match(regex, l):
                        # check if position is empty
                        assert v[i] == None

                        # add value to position
                        v[i] = split(l[:-1])
                        assert v[i] != None

                complete = True
                for p in v:
                    if p == None:
                        complete = False
                        break
                if complete:
                    print >>summary, s + ' ' + self.fname_split(fn) + ' ' + " ".join(v)
                    v = []
            f.close()

    def as_dict(self, cfg):
        s = {
            'name' : self.name,
            'dimensions' : cfg.optspace.keys(),
            'groupby' : self.groupby,
            'process' : lambda a,b,c,d: FilesMultiLineSelect.proc(self, a, b, c, d)
            }
        header = []
        for (h,r,x) in self.filters:
            header.append(h)
        header = " ".join(header)
        if self.fname_header == None:
            s['header'] = lambda h: h  + ' file ' + header
        else:
            s['header'] = lambda h: h  + self.fname_header + ' ' + header
        return s
