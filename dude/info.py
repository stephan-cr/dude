# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""!!"""
import utils
import core

def show_info(cfg, options = {}, run = 0):
    if options == {}:
        print '----------------------------------'
        print 'Experiment', cfg.name
        print '----------------------------------'
        print 'Options :'
        for k in cfg.options.keys():
            print '%8s' % (k), '=', cfg.options[k]
        print 'Runs    :', str(cfg.runs)
        if len(cfg.constraints) == 0:
            print 'Samples : complete space'
        else:
            print 'Samples : constrained space'
        print "Timeout :", cfg.timeout
        #print "Version :", cfg.dude_version
        #else:
        #    print 'Samples :', str(self.samples)
        #    print 'Program :', str(self.progBaseName)
        print '----------------------------------'
        print 'Summaries:'
        for s in cfg.summaries:
            print '\t', s['name']
        print '----------------------------------'
        if hasattr(cfg, 'filters'):
            print 'Filters:'
            for f in cfg.filters:
                print '\t', f
        else:
            print 'Filters: None'
        print
    else:
        print
        print 'Experiment: '
        for k in options.keys():
            print '%8s' % (k), '=', options[k]
        print '%8s' %('CWD'), '=', core.get_folder(cfg, options, run)
        if hasattr(cfg, 'get_cmd'):
            print '%8s' %('CMD'), '=', cfg.get_cmd(options)


def print_run(actual_runs, status, experiment_elapsed_time):
    print "Run %d status %d time %.4fs" % (actual_runs, status,
                                           experiment_elapsed_time)

def print_exp(actual_runs, executed_runs, missing_runs, total_runs,
              total_time, elapsed_time):
    remaining_time = elapsed_time.mean()*(missing_runs-executed_runs)
    if missing_runs == 0:
        percent_exec = 100
    else:
        percent_exec = executed_runs/missing_runs*100

    # strings
    runs = "run %d of %d: remaining runs %d of %d (%d%%)" % (actual_runs, total_runs,
                                                             missing_runs - executed_runs, missing_runs,
                                                             percent_exec)
    elapsed = "elapsed: %s" % utils.sec2string(total_time)
    remaining = "remaining: %s" % utils.sec2string(remaining_time)

    print "====", runs, elapsed, remaining, "===="

def print_exp_simple(actual_runs, total_runs, missing_runs):
    #percent_exec = 100*actual_runs/total_runs

    runs = "run %d of %d: remaining runs %d" % (actual_runs,
                                                total_runs,
                                                missing_runs)
    print "====", runs, "===="
