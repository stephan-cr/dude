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
import pty
import sys
import time
import utils
from threading import Timer

tc = time.time


catch_sigint = False
global_cfg = None


# there are two ways how to start an experiment. 
# Either with a spawn or with a fork
gproc = None
gpid  = None
fd    = None



def keyint_handler():
    """Stops the experiment and asks if it should stop the complete set of experiments or not"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    status = 1
    if gproc != None:
        proc.wait()
        print "return code was : ", proc.poll()
        if hasattr(global_cfg, 'on_kill'):
            global_cfg.on_kill(None)

    if gpid != None:
        print "waiting dude child"
        os.kill(gpid, signal.SIGINT)
        (npid, status) = os.waitpid(gpid, 0)
        print "return code was : ", status
        if hasattr(global_cfg, 'on_kill'):
            global_cfg.on_kill(None)

    print "Quitting... ", gpid
    exit(status)


def kill_on_timeout(cfg, proc):
    """Kills experiment processes on timeout"""
    print "Killing experiment"
    proc.send_signal(signal.SIGINT)
    if hasattr(cfg, 'on_timeout'):
        cfg.on_kill(proc)

def kill_pid(pid, callback):
    """Kill process and execute callback."""
    print "Killing experiment"
    
    try:
        os.kill(pid, signal.SIGTERM)
    except:
        pass
    if callback: callback()

def fork_experiment(cfg, optpt, timeout, fname, show_output = True):
    """Fork process and start a experiment. The global variable gpid
    will be set with the child process. """
    global gpid, fd

    # stdout of the process will redirected to file
    f = open(fname,'w')

    # create a pipe to communicate
    r, w = os.pipe()

    gpid = os.fork()
    if gpid:
        # is there a callback in the cfg?
        callback = None
        if hasattr(cfg, 'on_timeout'):
            callback = lambda optpt: cfg.on_timeout(optpt)

        signal.signal(signal.SIGINT, lambda num, frame: keyint_handler())

        # start killer
        killer = Timer(timeout, kill_pid, [gpid, callback])
        killer.start()

        os.close(w) # use os.close() to close a file descriptor
        #fr = os.fdopen(r) # turn r into a file object
        fr = open(fname, 'r')
        fd = fr.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        start_time = time.time()
        status = 1
        done = False
        while True:
            try:
                line = fr.readline()
                if line:
                    if show_output:
                        print line.rstrip()
                    else:
                        break
                    #print >>f, line.rstrip()
                else:
                    raise IOError('empty line!')
            except IOError, e:
                if done:
                    break
                
            if not done:
                (npid, status) = os.waitpid(gpid, os.WNOHANG)
                #print npid, status
                if (npid, status) != (0,0):
                    done = True

                elapsed = time.time() - start_time
                if elapsed > 5:
                    time.sleep(5)
                    elapsed = time.time() - start_time
                    info.print_elapsed(cfg, elapsed)

        killer.cancel()
        f.close()
        fr.close()
        #gpid = None
        return status
    else:
        # we are the child
        def bahm():
            print "bahm bahm baaahm"
            sys.exit(1)
        signal.signal(signal.SIGINT, lambda num, frame: bahm())
        gpid = None
        os.close(r)
        w = os.fdopen(w, 'w')
        sys.stdout = f
        sys.stderr = f
        print "dude: child start"
        timeout = 2 # seconds
        t = None
        def flushit(t):
            t = Timer(timeout, flushit, [t])
            t.start()
            f.flush()
        t = Timer(timeout, flushit, [t])
        try: 
            ret = cfg.exp(optpt)
        except Exception, e:
            print e
            sys.exit(1) 
        print "dude: child exit"
        f.flush()
        t.cancel()
        w.flush()
        w.close()
        sys.exit(ret)

def run_program(cfg, cmd, timeout, fname, show_output = True):
    """Run experiment in a subprocess"""

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
        info.print_elapsed(cfg, elapsed)

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


def execute_safe(cfg, optpt, run, show_output, folder = None):
    """Executes one experiment configuration for a run"""
    start = tc()

    cmd = None
    if hasattr(cfg, 'get_cmd'):
        cmd = cfg.get_cmd(optpt)
        
    e_start = e_end = 0

    # get dir name and create if necessary
    if folder == None:
        folder = core.get_folder(cfg, optpt, run)

    if run == 1:
        # show experiment info
        info.show_info(cfg, optpt, run, folder)

    # skip successful runs
    if core.exist_status_file(folder):
        val = core.read_status_file(folder)
        if val == 0:
            # it ran successfully, don't repeat exp
            print '<-> skipping ' + str(run)
            print "Run", run, "skipped"
            return (False, 0)

    # change working directory
    wd = os.getcwd()
    os.chdir(folder)

    # call prepare experiment
    if hasattr(cfg, 'prepare_exp'):
        cfg.prepare_exp(optpt)

    e_start = tc()
    # decide whether to call run_program or fork_experiment
    if cmd != None:
        s = run_program(cfg, cmd, cfg.timeout, core.outputFile, show_output)
    else:
        s = fork_experiment(cfg, optpt, cfg.timeout, core.outputFile, show_output)
    e_end = tc()

    if s != 0:
        print "error: ", str(s)


    f = open(core.statusFile,'w')
    f.write(str(s))
    f.close()

    # call prepare experiment
    if hasattr(cfg, 'finish_exp'):
        cfg.finish_exp(optpt)

    # go back to working dir
    os.chdir(wd)

    # return the time used
    end = tc()

    info.print_run(run, s, (e_end - e_start))
    return (True, (end-start))

def execute(cfg, optpt, run, show_output, folder = None):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        return execute_safe(cfg, optpt, run, show_output, folder)
    except KeyboardInterrupt, e:
        print e
        return (False, 0)

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
        try:
            cfg.prepare_global()
        except KeyboardInterrupt, e:
            print "Interrupted on prepare_global()"
            sys.exit(1)

    if options.global_only:
        return

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
    assert hasattr(cfg, 'get_cmd') or hasattr(cfg, 'exp')
    assert not (hasattr(cfg, 'get_cmd') and hasattr(cfg, 'exp'))
    assert hasattr(cfg, 'timeout')
