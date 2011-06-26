# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""Manages the execution of experiments"""

import core
import fcntl
import info
import os
import signal
import subprocess
import sys
import time
import utils
from threading import Timer

tc = time.time


class SpawnProcess:
    """Run experiment in a subprocess"""
    def __init__(self, func, optpt, stdout, stderr):
        self.proc   = None
        self.status = None
        self.func   = func
        self.optpt  = optpt
        self.stdout = stdout
        self.stderr = stderr
        
    def kill(self):
        self.proc.kill()
        self.status = self.proc.wait()
        self.proc = None
        
    def poll(self):
        if self.status: 
            return True

        assert self.proc != None
        retcode = self.proc.poll()
        if retcode != None:
            self.status = retcode
            return True
        else:
            return False

    def start(self):
        self.proc = subprocess.Popen(self.func(self.optpt),
                                     shell = True,
                                     stderr = self.stdout,
                                     stdout = self.stderr)

class ForkProcess:
    """Fork process and start a experiment."""
    def __init__(self, func, optpt, stdout, stderr):
        self.pid    = None
        self.status = None
        self.func   = func
        self.optpt  = optpt
        self.stdout = stdout
        self.stderr = stderr
        
    def kill(self):
        assert self.pid != os.getpid()

        os.kill(self.pid, signal.SIGINT)
        (npid, status) = os.waitpid(self.pid, 0)
        self.pid = None
        # print "return code was : ", status
        self.status = status

    def poll(self):
        if self.status:
            return True

        assert self.pid != None
        (npid, status) = os.waitpid(self.pid, os.WNOHANG)
        if (npid, status) == (0,0):
            return False
        else:
            print status, npid, self.pid
            self.status = status
            return True

    def start(self):
        self.pid = os.fork()
        if self.pid == 0:
            self.__child()
            # should exit in __execute_child
            assert False 

    def __child(self):
        # def bahm():
        #     print "bahm bahm baaahm"
        #     sys.exit(1)
        # signal.signal(signal.SIGINT, lambda num, frame: bahm())
        sys.stdout = self.stdout
        sys.stderr = self.stderr
    
        print "dude: child start"
        try:
            ret = self.func(self.optpt)
        except KeyboardInterrupt, e:
            sys.exit(-1)
        except Exception, e:
            sys.exit(1)
        if ret == None:
            ret = 0
        sys.exit(ret)

def kill_proc(cfg, proc):
    """Stops the experiment and asks if it should stop the complete set of experiments or not"""
    proc.kill()
    if hasattr(cfg, 'on_kill'):
        cfg.on_kill(None)

def execute_one(cfg, optpt, stdout, stderr):
    """Run experiment in a child process. Kill process on timeout or keyboard interruption."""

    timeout = cfg.timeout

    if hasattr(cfg, 'cmdl_exp'):
        proc = SpawnProcess(cfg.cmdl_exp, optpt, stdout, stderr)
    else:
        assert hasattr(cfg, 'fork_exp')
        proc = ForkProcess(cfg.fork_exp, optpt, stdout, stderr)

    killer = Timer(timeout, kill_proc, [cfg, proc])
        
    try:
        # start process
        proc.start()
        
        # start timer after starting process. That is important
        # otherwise a forked process gets the timer as well.
        killer.start()

        start_time = time.time()
        elapsed = 0
        while True:
    
            if proc.poll():
                retcode = proc.status
                info.print_elapsed(timeout, elapsed)
                print
                break

            time.sleep(0.01 if elapsed < 5 else 5.0)
            elapsed = time.time() - start_time
            if elapsed >= 5 and elapsed < timeout:
                info.print_elapsed(timeout, elapsed)

    except KeyboardInterrupt, e:
        print
        kill_proc(cfg, proc)
        raise e
    finally:
        killer.cancel()

    return retcode

def execute_isolated(cfg, optpt, folder, show_output = False):
    """Executes one experiment in a separate folder"""
    start = tc()

    e_start = e_end = 0
    
    # skip successful runs
    if core.exist_status_file(folder):
        val = core.read_status_file(folder)
        if val == 0:
            # it ran successfully, don't repeat exp
            return (False, val, 0)

    # change working directory
    wd = os.getcwd()
    os.chdir(folder)

    # call prepare experiment
    if hasattr(cfg, 'prepare_exp'):
        cfg.prepare_exp(optpt)

    e_start = tc()
    status = -1
    try:
        fout = open(core.outputFile, 'w')
        status = execute_one(cfg, optpt, fout, fout)
    
        if status != 0:
            print 'command returned error value: %d' % s

    finally:
        e_end = tc()
        if fout: fout.close()

        f = open(core.statusFile,'w')
        f.write(str(status))
        f.close()

        print "status = ", status

        # call prepare experiment
        if hasattr(cfg, 'finish_exp'):
            cfg.finish_exp(optpt, status)

        # go back to working dir
        os.chdir(wd)

    # return the time used
    end = tc()

    return (True, status, (end-start))

def run(cfg, experiments, options):
    """
    Generate the experiment space and calls execute() for each
    experiment.
    """

    # print information
    info.show_info(cfg)

    # initialize counters
    t_start = tc()

    total_runs = len(experiments)# * cfg.runs
    missing_runs = total_runs - core.success_count(cfg, experiments)
    actual_runs = 0
    executed_runs = 0
    elapsed_time = utils.Mean()

    if hasattr(cfg, 'prepare_global') and not options.skip_global:
        try:
            cfg.prepare_global()
        except KeyboardInterrupt, e:
            print "Interrupted on prepare_global()"
            sys.exit(1)

    if not options.global_only:
        # print initial info
        info.print_exp_simple(1, total_runs, missing_runs)

        # execution loop
        for experiment in experiments:
            # One more run
            actual_runs += 1

            # get dir name and create if necessary
            folder = core.get_folder(cfg, experiment)

            # show experiment info
            info.show_info(cfg, experiment, 0, folder)

            # Execute the measurement
            exp_cpy = experiment.copy()
            (executed, status, etime) = execute_isolated(cfg, exp_cpy,
                                                 folder,
                                                 options.show_output)

            if executed:
                info.print_run(0, status, etime)
                executed_runs += 1
            else:
                print '<-> skipping'
            
            # Add elapsed time to mean object
            elapsed_time.add(etime)
                
            # Calculate the total time
            t_actual = tc()

            # Print some time information
            info.print_exp(actual_runs, executed_runs, 
                           missing_runs, total_runs, 
                           t_actual - t_start, elapsed_time)
    # end not global_only

    if hasattr(cfg, 'finish_global') and not options.skip_global:
        try :
            cfg.finish_global()
        except KeyboardInterrupt, e :
            print "Interrupted on finish_global()"
            sys.exit(1)

def check_cfg(cfg):
    assert hasattr(cfg, 'options')
    assert type(cfg.options) == dict
    # assert hasattr(cfg, 'constraints') optional
    assert type(cfg.constraints) == list
    assert hasattr(cfg, 'raw_output_dir')
    assert hasattr(cfg, 'prepare_exp')
    assert hasattr(cfg, 'cmdl_exp') or hasattr(cfg, 'exp')
    assert not (hasattr(cfg, 'cmdl_exp') and hasattr(cfg, 'exp'))
    assert hasattr(cfg, 'timeout')
