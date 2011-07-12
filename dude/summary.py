# Copyright (c) 2010, 2011 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""
Methods to collect results from experiments (in expfolders),
processing them, and writting the summaries out.
"""

import os

import core
import summary_backends
import summaries
import utils

def summarize_one(cfg, s, experiments, backend,
                  ignore_status = False):
    # group by X
    optspace = {}
    for k in s['groupby']: # select the right optspace
        optspace[k] = cfg.optspace[k]
    groups = utils.groupBy(experiments, optspace)

    # create summary output directory if necessary
    utils.checkFolder(cfg.sum_output_dir)

    # save working directory
    wd = os.getcwd()

    print
    print "starting summary", s['name']

    # for each group, call process of s
    for (group, elements) in groups:
        print "Group: ", group, " entries:", len(elements)
        optspace = {}
        for i in s['dimensions']:
            optspace[i] = cfg.optspace[i]

        # get experiments that match ?????
        space = utils.groupBy(elements, optspace)

        oFile = cfg.sum_output_dir + '/' + core.get_name(s['name'], group)

        # prepare columns and sizes for print
        other_cols = ["entries", "files"]
        cols = s['dimensions'] + other_cols
        cols_sz = []
        for dimension in s['dimensions']:
            lengths = map(lambda x: len(str(x)), optspace[dimension])
            lengths.append(len(dimension))
            cols_sz.append(max(lengths))
        cols_sz += map(len, other_cols)

        # print column titles
        print '-'*(sum(cols_sz)+len(cols_sz))
        print utils.strColumns(cols, cols_sz)
        print '-'*(sum(cols_sz)+len(cols_sz))

        # open file for group
        f = summary_backends.backend_constructor(backend)(oFile)

        # write header
        if s.has_key('header'):
            header = ""
            # get one point and look the dimensions
            (point, samples) = space[0]
            dimensions = point.keys()
            dimensions.sort()
            for d in dimensions:
                header += d + ' '

            header = s['header'](header)
            f.write_header(header)

        for (point, samples) in space:
            for sample in samples:
                if sample not in experiments:
                    continue
                outputFolder = core.get_folder(cfg, sample)

                # check if test ok
                if core.experiment_success(cfg, sample) or\
                        (ignore_status and\
                             core.experiment_ran(cfg, sample)):
                    os.chdir(outputFolder)
                    outf = open(core.outputFile)
                    # call process
                    s['process'](point, outf, f, wd + '/' + cfg.sum_output_dir)
                    outf.close()
                    os.chdir(wd)
        f.close()
        # next group

def summarize(cfg, experiments, sel = [], backend = 'file',
              ignore_status = False):
    """  """
    # TODO check if exists
    if sel == []:
        for s in cfg.summaries:
            sel.append(s['name'])

    # check output folder
    utils.checkFolder(cfg.sum_output_dir)

    for summary in cfg.summaries:
        #if summary.has_key('preprocess'):
        #    preprocess_one(cfg, summary)
        if summary['name'] in sel:
            summarize_one(cfg, summary, experiments, backend,
                          ignore_status)
            sel.remove(summary['name'])

    for s in sel:
        print s, "not valid"

def check_cfg(cfg):
    assert hasattr(cfg, 'dude_version')
    assert getattr(cfg, 'dude_version') >= 3

    assert hasattr(cfg, 'optspace')
    assert hasattr(cfg, 'sum_output_dir')

    if not hasattr(cfg, 'summaries'):
        cfg.summaries = [summaries.LineSelect('default')]
    else:
        assert type(cfg.summaries) == list

    summ = []
    for s in cfg.summaries:
        if type(s) == dict:
            summ.append(s)
        else:
            summ.append(s.as_dict(cfg))
    cfg.summaries = summ
    for s in cfg.summaries:
        assert type(s) == dict
        assert s.has_key('name')
        assert s.has_key('dimensions')
        assert s.has_key('groupby')
        # optional assert s.has_key('preprocess')
        assert s.has_key('process')
        assert s.has_key('header')
