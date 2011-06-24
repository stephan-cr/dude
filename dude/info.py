# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""!!"""
import utils
import core
import os

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


def show_info(cfg, optspace = {}, run = 0, folder = None):
    if optspace == {}:
        name = cfg.name if hasattr(cfg, 'name') else os.getcwd()
        print '----------------------------------'
        print 'Experiment', name
        print '----------------------------------'
        print 'Options :'
        for k in cfg.optspace.keys():
            print '%8s' % (k), '=', cfg.optspace[k]
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
        for k in optspace.keys():
            print '%8s' % (k), '=', optspace[k]
        if folder == None:
            folder = core.get_folder(cfg, optspace, run)
        print '%8s' %('CWD'), '=', folder
        if hasattr(cfg, 'get_cmd'):
            print '%8s' %('CMD'), '=', cfg.get_cmd(optspace)


def print_run(actual_runs, status, experiment_elapsed_time):
    print "Run %d status %d time %.4fs" % (actual_runs, status,
                                           experiment_elapsed_time)

def print_exp(actual_runs, executed_runs, missing_runs, total_runs,
              total_time, elapsed_time):
    remaining_time = elapsed_time.mean()*(missing_runs-executed_runs)
    if missing_runs == 0:
        percent_exec = 100.0
    else:
        percent_exec = float(executed_runs)/float(missing_runs)*100.0

    # strings
    runs = "run %d of %d: remaining runs %d of %d (%.1f%%)" % (actual_runs, total_runs,
                                                               missing_runs - executed_runs,
                                                               missing_runs,
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

def print_elapsed(timeout, elapsed, last_elapsed = None):
    b = PBar(20)
    p = elapsed * 1000 / timeout * 100
    p /= 1000

    if (p > 100) or (p < 0): 
        b.fill(100)
        print b, "\ttime out!!                  "
    else:
        b.fill(p)
        print b, "\telapsed: %d" % (int(elapsed)), "seconds", " " + chr(27) + '[A'

