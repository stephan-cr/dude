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

def is_new(summary):
    return isinstance(summary, summaries.SummaryBase)

def summarize_one(cfg, s, experiments, backend,
                  ignore_status = False):
    # group by X
    optspace = {}

    if is_new(s):
        groupby    = s.groupby()
        name       = s.name()
        dimensions = cfg.optspace.keys()
    else:
        groupby    = s['groupby']
        name       = s['name']
        dimensions = s['dimensions']

    for k in groupby: # select the right optspace
        optspace[k] = cfg.optspace[k]
    groups = utils.groupBy(experiments, optspace)

    # create summary output directory if necessary
    utils.checkFolder(cfg.sum_output_dir)

    # save working directory
    wd = os.getcwd()

    print
    print "Summary:", name

    # for each group, call process of s
    for (group, elements) in groups:
        print "Group: ", group, " entries:", len(elements)
        optspace = {}

        for i in dimensions:
            optspace[i] = cfg.optspace[i]

        # get experiments that match

        if len(groupby) == 0: # hack to speed up normal path
            space = []
            for e in elements:
                x = {}
                for k in e: x[k] = str(e[k])
                space.append((x, [e]))
        else:
            space = utils.groupBy(elements, optspace)

        oFile = os.path.join(cfg.sum_output_dir, core.get_name(name, group))

        # prepare columns and sizes for print
        other_cols = ["entries", "files"]
        cols = dimensions + other_cols
        cols_sz = []
        for dimension in dimensions:
            lengths = map(lambda x: len(str(x)), optspace[dimension])
            lengths.append(len(dimension))
            cols_sz.append(max(lengths))
        cols_sz += map(len, other_cols)

        # print column titles
        print '-'*(sum(cols_sz)+len(cols_sz))
        print utils.strColumns(cols, cols_sz)
        print '-'*(sum(cols_sz)+len(cols_sz))

        # open file for group
        f = summary_backends.backend_constructor(backend)(oFile, dimensions)

        # write header
        if is_new(s):
            # get one point and look the dimensions
            (point, samples) = space[0]
            header = s.header(point.keys())
            if header:
                f.write_header(header)
        elif 'header' in s:
            # get one point and look the dimensions
            (point, samples) = space[0]
            dims = point.keys()
            dims.sort()
            header = ' '.join(dims) + ' '

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
                    if is_new(s):
                        s.visit(point, outf, f)
                    else:
                        s['process'](point, outf, f, os.path.join(wd, cfg.sum_output_dir))
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
            if is_new(s):
                sel.append(s.name())
            else:
                sel.append(s['name'])

    # check output folder
    utils.checkFolder(cfg.sum_output_dir)

    for summary in cfg.summaries:
        #if 'preprocess' in summary:
        #    preprocess_one(cfg, summary)
        if is_new(summary):
            if summary.name() in sel:
                summarize_one(cfg, summary, experiments, backend,
                              ignore_status)
                sel.remove(summary.name())
        else:
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
        elif hasattr(s, 'as_dict'):
            summ.append(s.as_dict(cfg))
        else:
            summ.append(s)
    cfg.summaries = summ
    for s in cfg.summaries:
        assert type(s) == dict or is_new(s) # by inheritance ok
        if type(s) == dict:
            assert 'name' in s
            assert 'dimensions' in s
            assert 'groupby' in s
            # optional assert 'preprocess' in s
            assert 'process' in s
            assert 'header' in s
