# Copyright (c) 2013 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" """
import core
import shutil
import os
import sys

def visit_cmd_experiment(folder, cmd):
    cwd = os.getcwd()
    os.chdir(folder)
    r = os.system(cmd)
    os.chdir(cwd)
    if r: sys.exit(-1)

def visit_cmd_experiments(cfg, experiments, cmd):
    for experiment in experiments:
        folder = core.get_folder(cfg, experiment)
        if os.path.exists(folder):
            print "Executing \"%s\" in %s" % (cmd, folder)
            visit_cmd_experiment(folder, cmd)
