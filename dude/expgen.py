# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" generates create directory for an experiment and an empty Dudefile"""
import errno
import os
import string

def __create_folder(folder):
    try:
        os.makedirs(folder)
    except OSError as e:
        # if directory already exists: fine
        if e.errno != errno.EEXIST:
            raise


dfile = """\
# -*- mode: python -*-

dude_version = 3
from dude.defaults import *

name    = "${expname}"

optspace = {
  'param1' : [1,2,3]
}

prog = "echo"

def prepare_global():
    pass

def prepare_exp(optpt):
    pass

def cmdl_exp(optpt):
    return prog + " bla: " + str(optpt['param1'])

def finish_exp(optpt, status):
    pass

import dude.summaries
example_summary = dude.summaries.LineSelect (
    name   = 'example_summary',
    regex  = '.*',
    split  = (lambda l: l.split(':')[1]),
    header = "result"
    )

summaries = [example_summary]
"""


def __create_dfile(folder, expname):
    f = open(os.path.join(folder, 'Dudefile'), 'w')
    f.write(string.Template(dfile).substitute({'expname':expname}))
    f.close()


def create(expname=None):
    foldername = expname
    if expname is None or expname == '.':
        expname = os.path.basename(os.getcwd())
        foldername = '.'
    else:
        __create_folder(expname)
    __create_dfile(foldername, expname)
