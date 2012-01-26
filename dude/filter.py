# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" """

import core
import os
import utils
import re

def filter_one(cfg, experiments, filter, invert, only_ran):
    """ """
    wd = os.getcwd()
    filtered_experiments = []
    for experiment in experiments:
        if only_ran and core.experiment_ran(cfg, experiment):
            folder = core.get_folder(cfg, experiment)
            os.chdir(folder)
            outf = open(core.outputFile)
            outf.readline()
            ret = filter(experiment, outf)
            if not invert and ret:
                filtered_experiments.append( experiment )
            if invert and not ret:
                filtered_experiments.append( experiment )
            outf.close()
            os.chdir(wd)
        elif not only_ran:
            folder = core.get_folder(cfg, experiment)
            os.chdir(folder)
            ret = filter(experiment, None)
            if not invert and ret:
                filtered_experiments.append( experiment )
            if invert and not ret:
                filtered_experiments.append( experiment )
            os.chdir(wd)
    return filtered_experiments


def filter_experiments(cfg, filters, invert, only_ran=True):
    """ """
    experiments = core.get_experiments(cfg)
    filtered_experiments = experiments

    for f in filters:
        filtered_experiments  = filter_one(cfg, filtered_experiments, f, invert, only_ran)
    return filtered_experiments


def generic_filter(experiment, outf, filters):
    for key, value in filters:
        assert type(key) == str
        assert type(value) == list

        if not utils.parse_value(experiment[key]) in value:
            return False
    return True


def filter_inline(cfg, filters, invert, only_ran=True):
    flts = []
    for f in filters.split(';'):
        fs = f.split('=')
        assert len(fs) == 2
        (key,value) = fs
        key = key.strip()
        if re.match("\[.*\]", value):
            value = utils.parse_str_list(value)
        else:
            value = [utils.parse_value(value)]
        flts.append((key,value))

        # add optpt to optspace if it does not exist
        if key not in cfg.optspace:
            cfg.optspace[key] = []

        for v in value:
            if v not in cfg.optspace[key]:
                cfg.optspace[key].append(v)

    return filter_experiments(cfg, [(lambda a, b: generic_filter(a,b,flts))], invert, only_ran)



def check(cfg):
    """ """
    # check if the filters really exist
    assert hasattr(cfg, 'filters')
    assert type(cfg.filters) == dict
    assert hasattr(cfg, 'optspace')
