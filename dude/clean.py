# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" """
import core
import shutil
import os

def clean_experiments(cfg, experiments):
    for experiment in experiments:
        folder = core.get_folder(cfg, experiment)
        print "Cleaning", folder
        shutil.rmtree(folder)

def clean_experiment(folder):
    status_file = os.path.join(folder, 'dude.status')
    if os.path.exists(status_file):
        print "Cleaning", folder
        os.remove(status_file)
