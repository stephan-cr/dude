# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" """
import core
import shutil
import os
import glob
import dimensions
import utils

def clean_experiments(cfg, experiments):
    for experiment in experiments:
        folder = core.get_folder(cfg, experiment)
        print "Cleaning", folder
        if os.path.exists(folder):
            shutil.rmtree(folder)

def clean_experiment(folder):
    status_file = os.path.join(folder, 'dude.status')
    if os.path.exists(status_file):
        print "Cleaning", folder
        os.remove(status_file)

def clean_invalid_experiments(cfg, experiments):
    valid_folders = []
    for experiment in experiments:
        folder = core.get_folder(cfg, experiment)
        valid_folders.append(folder)

    raw_folder = core.get_raw_folder(cfg)
    meta_file = raw_folder + '/' + dimensions.META_FILE

    folders = glob.glob(raw_folder + '/*')
    folders = [f for f in folders
               if f not in valid_folders
               and f != meta_file]

    if len(folders) == 0:
        print "no invalid expfolders"
        return

    print "Removing following folders: "
    for folder in folders:
        print "\t", folder
    r = 'y'
    print "sure? [y/N]"
    r = utils.getch()
    if r == 'y':
        for folder in folders:
            shutil.rmtree(folder)
