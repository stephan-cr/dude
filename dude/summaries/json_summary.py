# Copyright (c) 2011 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import os
import json
import glob
from base import *

class JsonSelect(SummaryBase):
    """ Document this!!! """
    def __init__(self, name, path, filename, header,
                 groupby = [], quiet = False):
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

            group_out.write(s)
            f.close()
