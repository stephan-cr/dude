# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""Manages the execution of experiments"""
import commands
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


catch_sigint = False
running_process = None
global_cfg = None
def sig_handler(signum, frame, proc):
    """Stops the experiment and asks if it should stop the complete set of experiments or not"""
    if proc != None:
        proc.wait()
        print "return code was : ", proc.poll()
        if hasattr(global_cfg, 'on_kill'):
            global_cfg.on_kill(None)

    print "Skip or quit? [s/q]"
    r = utils.getch() #raw_input("Skip, quit, or continue? [s/q/c]")
    if r == 's':
        print "Skipping..."
        return
    else:
        print "Quitting..."
        sys.exit(1)
    return

def kill_on_timeout(cfg, proc):
    """Kills experiment processes on timeout"""
    print "Killing experiment"
    print dir(proc)
    proc.send_signal(signal.SIGINT)
    if hasattr(cfg, 'on_timeout'):
        cfg.on_kill(proc)

def run_program(cfg, cmd, timeout, fname, show_output = True):
    """Run experiment in a subprocess"""
    global running_process

    f = open(fname,'w')
    fr = open(fname,'r')

    # shell=False, bufsize=0
    p = subprocess.Popen(cmd, shell=True,
                         stderr=f,
                         stdout=f)   
    set_catcher(p)
    global_cfg = cfg
    t = Timer(timeout, kill_on_timeout, [cfg, p])
    t.start()

    retcode = None

    # make stdout of process non-blocking
    
    fd = fr.fileno() # p.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    start_time = time.time()
    while True:
        while True:
            try:
                line = fr.readline()
                if line != '':
                    if show_output:
                        print ">>> " + line.rstrip()
                else:
                    break
            except IOError, e:
                pass

        retcode = p.poll()
        if retcode != None:
            break

        time.sleep(5)
        elapsed = time.time() - start_time
        print elapsed, "seconds elapsed"

    while True:
        try:
            line = fr.readline()
            if line != '':
                if show_output:
                    print ">>> " + line.rstrip()
            else:
                break
        except IOError, e:
            break

    t.cancel()
    f.close()
    fr.close()
    return retcode

def init():
    # catch CTRL-C
    catch_sigint = True
    set_catcher(None)

def set_catcher(proc):
    # catch CTRL-C
    if catch_sigint:
        signal.signal(signal.SIGINT, lambda num, frame: sig_handler(num,frame,proc) )


def execute(cfg, experiment, run, show_output):
    """Executes one experiment configuration for a run"""
    start = tc()
    cmd = cfg.get_cmd(experiment)

    e_start = e_end = 0

    # get dir name and create if necessary
    folder = core.get_folder(cfg, experiment, run)

    if run == 1:
        # show experiment info
        info.show_info(cfg, experiment, run)
    
    # skip successful runs
    if core.exist_status_file(folder):
        val = core.read_status_file(folder)
        if val == 0: 
            # it ran successfully, dont repeat exp
            print '<-> skipping ' + str(run)
            print "Run", run, "skipped"
            return (False, 0)

    # change working directory
    wd = os.getcwd()
    os.chdir(folder)

    # call prepare experiment
    if hasattr(cfg, 'prepare_exp'):
        cfg.prepare_exp(experiment)

    e_start = tc()
    #(s, o) = commands.getstatusoutput(cmd)
    s = run_program(cfg, cmd, cfg.timeout, core.outputFile, show_output)
    e_end = tc()
			
    if s != 0:
        print "error: ", str(s)

        
    f = open(core.statusFile,'w')
    f.write(str(s))
    f.close()
    
    # call prepare experiment
    if hasattr(cfg, 'finish_exp'):
        cfg.finish_exp(experiment)

    # go back to working dir
    os.chdir(wd)

    # return the time used
    end = tc()

    info.print_run(run, s, (e_end - e_start))
    return (True, (end-start))

def run(cfg, experiments, options):
    """Generate the experiment space and calls execute() for each experiment"""
    # check configuration and folders
    #self.checkRequirements() 
    #self.checkFolders()

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
        cfg.prepare_global()

    # print initial info
    info.print_exp_simple(1, total_runs, missing_runs)

    # execution loop
    for i in range(0, len(experiments)):
        run,experiment = experiments[i]
        # One more run 
        actual_runs += 1
        # Execute the measurement
        exp_cpy = experiment.copy()
        (executed, etime) = execute(cfg, exp_cpy, run, options.show_output)
        
        if executed:
            executed_runs += 1

        # Add elapsed time to mean object
        elapsed_time.add(etime)

        # Calculate the total time
        t_actual = tc()
				
        # Print some time information
        info.print_exp(actual_runs, executed_runs, missing_runs, total_runs, t_actual - t_start, elapsed_time)

def check_cfg(cfg):
    assert hasattr(cfg, 'runs')
    assert hasattr(cfg, 'options')
    assert type(cfg.options) == dict
    # assert hasattr(cfg, 'constraints') optional
    assert type(cfg.constraints) == list
    assert hasattr(cfg, 'raw_output_dir')
    assert hasattr(cfg, 'prepare_exp')
    assert hasattr(cfg, 'get_cmd')
    assert hasattr(cfg, 'timeout')
