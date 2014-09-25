# Copyright (c) 2010, 2011 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""
Dude output for experiments
"""
import utils
import os
import core
import sys

HEAD = '~'*80
HEAD2 = '~'*80
LINE = '-'*80

class PBar:
    """
    A simple progress bar.

    Based on example at http://snippets.dzone.com/posts/show/5432
    """
    def __init__(self, length = 80):
        self.len = length
        self.chars = (' ', '+')
        self.wrap = ('[', ']')
        self.filledc = 0

    def fill(self, i):
        assert not (i > 100) or (i < 0)
        self._setP(i)

    def _setP(self, p):
        self.filledc = int(round(float(self.len*p)/100))

    def __str__(self):
        out = []
        out.append(self.wrap[0])
        out.append(self.filledc*self.chars[1])
        out.append((self.len-self.filledc)*self.chars[0])
        out.append(self.wrap[1])
        return "".join(out)


def show_info(cfg, experiments):
    name = cfg.name if hasattr(cfg, 'name') else os.getcwd()
    print HEAD2
    print 'Experiment set:', name
    print LINE
    print 'Option space:'
    for k in cfg.optspace.keys():
        print '%20s' % (k), '=', cfg.optspace[k]
    if len(cfg.constraints) == 0:
        print 'Experiments: complete space'
    else:
        print 'Experiments: constrained space'
    print 'Summaries  :', [(summ['name'] if type(summ) == dict else summ.name()) for summ in cfg.summaries]
    if hasattr(cfg, 'filters'):
        print 'Filters    :', [fil for fil in cfg.filters]
    print "Timeout    :", cfg.timeout
    print HEAD2
    print
    print
    print


def show_exp_info(cfg, experiment, folder,
                  executed_runs, missing_runs, total_runs):
    print HEAD
    print 'Experiment: %d of %d (total: %d)'  % (executed_runs,
                                                 missing_runs,
                                                 total_runs)
    print 'Folder :', folder
    print 'Options:'
    for k in experiment.keys():
        print '%20s' % (k), '=', experiment[k]
    if hasattr(cfg, 'get_cmd'):
        print '%8s' %('CMD'), '=', cfg.get_cmd(experiment)
    print LINE

def print_run(actual_runs, status, experiment_elapsed_time):
    print LINE
    print 'Status   : %d'    % status
    # print 'Time  : %.4fs' % experiment_elapsed_time

def print_exp(actual_runs, executed_runs, missing_runs, total_runs,
              total_time, elapsed_time):
    #print LINE
    remaining_time = elapsed_time.mean()*(missing_runs-executed_runs)
    if missing_runs == 0:
        percent_exec = 100.0
    else:
        percent_exec = float(executed_runs)/float(missing_runs)*100.0

    # strings
    s  = "Completed: %.1f%%" % (percent_exec)
    #s += "\tElapsed  : %s" % utils.sec2string(total_time)
    s += "\nRemaining: %s (estimated)" % utils.sec2string(remaining_time)
    print s

def print_exp_simple(actual_runs, total_runs, missing_runs):
    #percent_exec = 100*actual_runs/total_runs

    runs = "run %d of %d: remaining runs %d" % (actual_runs,
                                                total_runs,
                                                missing_runs)
    print "====", runs, "===="

def print_elapsed(timeout, elapsed, last_elapsed = None):
    if timeout == None:
        # mock the limit just to show some progress
        timeout = 60
        if elapsed > timeout:
            timeout = elapsed * 1.5
    b = PBar(20)
    p = elapsed * 1000 / timeout * 100
    p /= 1000

    if (p > 100) or (p < 0):
        b.fill(100)
        print b, "\ttime out!!                  "
    else:
        b.fill(p)
        print b, "\telapsed: %d" % (int(elapsed)), "seconds", " " + chr(27) + '[A'
    sys.stdout.flush()

def print_status(cfg, experiments):
    name = cfg.name if hasattr(cfg, 'name') else os.getcwd()
    print HEAD2
    print 'Experiment set:', name
    print LINE
    total_runs = len(experiments)
    #missing_runs = total_runs - core.success_count(cfg, experiments)
    success  = core.success_count(cfg, experiments)
    failed   = len(core.get_failed(cfg, experiments, False))
    missing  = len(core.get_failed(cfg, experiments, True))
    print 'Statistics:'
    print '  Total    : %d' % (total_runs)
    print '  Finished : %d' % (success + failed)
    print '  Pending  : %d' % (missing - failed)
    print '  Failed   : %d' % (failed)
    print 'Running:'
    for e in experiments:
        v = core.experiment_running(cfg, e)
        if v:
            print '%10d : %s' % (v, core.get_folder(cfg, e))
    print HEAD2
    print
