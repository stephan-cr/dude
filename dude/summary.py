# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

""" """
import time
import os
import core
import utils
def preprocess_one(cfg, s):
    """ """
    assert False and "Not implemented"

    # get experiments 
    experiments = core.get_experiments(cfg)
    wd = os.getcwd()
    for experiment in experiments:
        for run in range(1, cfg.runs+1):
            if experiment_success(cfg, experiment,run):
                folder = core.get_folder(cfg, experiment, run)
                os.chdir(folder)
                fout = open(outputFile)
                fout.readline() #remove first line
                s['preprocess'](fout)
                fout.close()
                os.chdir(wd)

def summarize_one(cfg, s, filtered_experiments):
    experiments = []
    for exp in filtered_experiments:
        run, experiment = exp
        experiments.append(experiment)

    # group by X 
    options = {}
    for k in s['groupby']: # select the right options
        options[k] = cfg.options[k]
    groups = utils.groupBy(experiments, options)

    # create summary output directory if necessary
    utils.checkFolder(cfg.sum_output_dir)
    
    # save working directory
    wd = os.getcwd()

    print 
    print "starting summary", s['name']

    # for each group, call process of s
    for (group, elements) in groups:
        print "Group: ", group, " entries:", len(elements)
        options = {}
        for i in s['dimensions']: 
            options[i] = cfg.options[i]

        # get experiments that match ?????
        space = utils.groupBy(elements, options)

        oFile = cfg.sum_output_dir + '/' + core.get_name(s['name'],group)
        
        # prepare columns and sizes for print
        other_cols = ["entries", "files"]
        cols = s['dimensions'] + other_cols
        cols_sz = []
        for dimension in s['dimensions']:
            lengths = map(lambda x: len(str(x)), options[dimension])
            lengths.append(len(dimension))
            cols_sz.append(max(lengths))
        cols_sz += map(len,other_cols)

        # print column titles
        print '-'*(sum(cols_sz)+len(cols_sz))
        print utils.strColumns(cols, cols_sz)
        print '-'*(sum(cols_sz)+len(cols_sz))

        # open file for group
        f = open(oFile, 'w')

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
            print >>f, header

        for (point, samples) in space:
            outputs = []
            proc = 0 
            
            for sample in samples:
                proc = 0
                for run in range(1, cfg.runs+1):
                    if not (run, sample) in filtered_experiments:
                        continue
                    outputFolder = core.get_folder(cfg, sample, run)

                    # check if test ok
                    if core.experiment_success(cfg, sample, run):
                        os.chdir(outputFolder)
                        outf = open(core.outputFile)
                        # call process
                        s['process'](point, outf, f, wd + '/' + cfg.sum_output_dir)
                        outf.close()
                        os.chdir(wd)
        f.close()
        # next group

def summarize(cfg, filtered_experiments, sel = []):
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
            summarize_one(cfg, summary, filtered_experiments)
            sel.remove(summary['name'])

    for s in sel:
        print s, "not valid"

            
        


def check_cfg(cfg):
    assert hasattr(cfg, 'sum_output_dir')
    assert hasattr(cfg, 'summaries')
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
