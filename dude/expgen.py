# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" generates create directory for an experiment and an empty Dudefile"""
import os
import string

def __create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)



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
sum = dude.summaries.LineSelect (
	name   = 'example_summary',
        regex  = '.*',
        split  = (lambda l: l.split(':')[1]),
        header = "result"
	)

summaries = [sum]
"""


def __create_dfile(folder, expname):
    f = open(folder + '/Dudefile', 'w')
    f.write(string.Template(dfile).substitute({'expname':expname}))
    f.close()


def create(expname):
    __create_folder(expname)
    __create_dfile(expname, expname)
