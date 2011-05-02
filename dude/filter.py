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
    for (run, experiment) in experiments:
        if only_ran and core.experiment_ran(cfg, experiment, run):
            folder = core.get_folder(cfg, experiment, run)
            os.chdir(folder)
            outf = open(core.outputFile)
            outf.readline()
            ret = filter(experiment, run, outf)
            if not invert and ret:
                filtered_experiments.append( (run, experiment) )
            if invert and not ret:
                filtered_experiments.append( (run, experiment) )
            outf.close()
            os.chdir(wd)
        elif not only_ran:
            folder = core.get_folder(cfg, experiment, run)
            os.chdir(folder)
            ret = filter(experiment, run, None)
            if not invert and ret:
                filtered_experiments.append( (run, experiment) )
            if invert and not ret:
                filtered_experiments.append( (run, experiment) )
            os.chdir(wd)
    return filtered_experiments


def filter_experiments(cfg, filters, invert, only_ran=True):
    """ """
    experiments = core.get_experiments(cfg)
    filtered_experiments = []
    for run in range(1, cfg.runs+1):
        for experiment in experiments:
            filtered_experiments.append( (run, experiment) )

    for f in filters:
        filtered_experiments  = filter_one(cfg, filtered_experiments, f, invert, only_ran)
    return filtered_experiments


def generic_filter(experiment, run, outf, filters):
    for key, value in filters:
        assert type(key) == str
        assert type(value) == list

        if key == 'run':
            if not run in value:
                return False
        else:
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
        if not cfg.optspace.has_key(key):
            cfg.optspace[key] = []

        for v in value:
            if v not in cfg.optspace[key]:
                cfg.optspace[key].append(v)

    return filter_experiments(cfg, [(lambda a,b,c: generic_filter(a,b,c,flts))], invert, only_ran)



def check(cfg):
    """ """
    # check if the filters really exist
    assert has_attr(cfg, 'filters')
    assert type(cfg.filters) == dict
    assert has_attr(cfg, 'optspace')
