# Copyright (c) 2010, 2013 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""Manages the execution of experiments"""

import core
import traceback
import info
import os
import signal
import subprocess
import sys
import time
import utils
import errno
from threading import Timer

tc = time.time


class SpawnProcess:
    """Run experiment in a subprocess.  Because process runs with
    shell True, we need to use process groups to terminate the
    process.
    """
    def __init__(self, func, optpt, stdout, stderr):
        self.proc   = None
        self.status = None
        self.func   = func
        self.optpt  = optpt
        self.stdout = stdout
        self.stderr = stderr

    def kill(self):
        try:
            os.killpg(self.proc.pid, signal.SIGKILL)
        except OSError, e:
            print "Ignoring exception:", e
        self.status = self.proc.wait()

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
                                     stdout = self.stderr,
                                     preexec_fn = os.setsid
                                     )
        assert self.proc != None

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

        (npid, status) = os.waitpid(self.pid, os.WNOHANG)
        if (npid, status) == (0,0):
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
            # print status, npid, self.pid
            self.status = os.WEXITSTATUS(status)
            return True

    def start(self):
        self.pid = os.fork()
        if self.pid == 0:
            self.__child()
            # should exit in __execute_child
            assert False

    def __child(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

        ret = 1
        print "dude: child start", os.getpid()
        try:
            ret = self.func(self.optpt)
            print "dude: child exit", ret
        except KeyboardInterrupt, e:
            #print "Cought keyboard interrupt in child"
            os._exit(3) ## keyinterrupt or timeout
        except Exception, e:
            print "Exception in fork_cmd:"
            print '#'*60
            print "", e
            print '~'*60
            traceback.print_exc(file=sys.stdout)
            print '#'*60
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(2)
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
            sys.stdout.flush()
            sys.stderr.flush()
            if ret == None:
                ret = 0
            os._exit(ret)

def kill_proc(cfg, proc, terminate):
    """Stops the experiment and asks if it should stop the complete
    set of experiments or not"""
    proc.kill()

    if hasattr(cfg, 'finish_exp'):
        cfg.finish_exp(proc.optpt, proc.status)

    if terminate:
        # Unlock experiment (we are in the experiment directory since
        # we called chdir).
        core.experiment_unlock(cfg, ".")
        os._exit(1)
    else:
        # If it was a timeout, terminate is false. The unlock is
        # called in the finally of execute_one().
        pass

def execute_one(cfg, optpt, stdout, stderr):
    """Run experiment in a child process. Kill process on timeout or
    keyboard interruption."""

    timeout = cfg.timeout

    if hasattr(cfg, 'cmdl_exp'):
        proc = SpawnProcess(cfg.cmdl_exp, optpt, stdout, stderr)
    else:
        assert hasattr(cfg, 'fork_exp')
        proc = ForkProcess(cfg.fork_exp, optpt, stdout, stderr)

    killer = Timer(timeout, kill_proc, [cfg, proc, False]) if timeout else None

    # save old sigint handler
    old_handler = signal.getsignal(signal.SIGINT)

    try:
        try:
            # start process
            proc.start()

            # overwrite sigint handler. If a KeyboardInterrupt occurs
            # before that, we catch that bellow and kill the process
            # manually.
            signal.signal(signal.SIGINT,
                          lambda num, frame: kill_proc(cfg, proc, True))
        except KeyboardInterrupt, e:
            #print "Cought keyboard interrupt"
            kill_proc(cfg, proc, True) # True == terminate dude
            assert False, "Never reach this line"

        # start timer after starting process. That is important
        # otherwise a forked process gets the timer as well.
        if killer: killer.start()

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
            if elapsed >= 5:
                if timeout is None or elapsed < timeout:
                    info.print_elapsed(timeout, elapsed)
    finally:
        # restore sigint handleer
        signal.signal(signal.SIGINT, old_handler)

        if killer: killer.cancel()
        # print >>sys.stderr, "ciao", os.getpid()

    return retcode

def execute_isolated(cfg, optpt, folder, show_output = False):
    """Executes one experiment in a separate folder"""
    start = tc()

    # lock experiment
    if not core.experiment_lock(cfg, folder):
        return (False, 0, 0)

    # skip successful runs
    if core.exist_status_file(folder):
        val = core.read_status_file(folder)
        if val == 0:
            # it ran successfully, don't repeat exp

            # unlock experiment
            core.experiment_unlock(cfg, folder)

            return (False, val, 0)

    # change working directory
    wd = os.getcwd()
    os.chdir(folder)

    # call prepare experiment
    if hasattr(cfg, 'prepare_exp'):
        if show_output:
            f = utils.Tee("dude.prepare_exp", 'w')
        else:
            f = open("dude.prepare_exp", 'w')
        try:
            sys.stdout = sys.stderr = f
            if cfg.prepare_exp(optpt) == False:
                # unlock experiment
                core.experiment_unlock(cfg, ".")

                os.chdir(wd)
                return (False, -1 , 0)
        except:
            core.experiment_unlock(cfg, ".")
            raise  # raise previous exception
        finally:
            if f: f.close()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
    status = -1
    try:
        if show_output:
            fout = utils.Tee(core.outputFile, 'w')
        else:
            fout = open(core.outputFile, 'w')

        status = execute_one(cfg, optpt, fout, fout)
        if status != 0:
            print 'command returned error value: %d' % status

    finally:
        if fout: fout.close()

        # call prepare experiment
        if hasattr(cfg, 'finish_exp'):
            if show_output:
                f = utils.Tee("dude.finish_exp", 'w')
            else:
                f = open("dude.finish_exp", 'w')
            try:
                sys.stdout = sys.stderr = f
                s = cfg.finish_exp(optpt, status)
                # if finish_exp returns something, use that as status
                # value, otherwise use execute_one status.
                if s: status = s
            except:
                core.experiment_unlock(cfg, ".")
                raise  # raise previous exception
            finally:
                if f: f.close()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

        f = open(core.statusFile,'w')
        print >>f, status
        f.close()

        # unlock experiment
        core.experiment_unlock(cfg, ".")

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
    info.show_info(cfg, experiments)

    # initialize counters
    t_start = tc()

    total_runs = len(experiments)# * cfg.runs
    missing_runs = total_runs - core.success_count(cfg, experiments)
    actual_runs = 0
    executed_runs = 0
    elapsed_time = utils.Mean()

    if hasattr(cfg, 'prepare_global') and not options.skip_global:
        if options.show_output:
            f = utils.Tee("dude.prepare_global", 'w')
        else:
            f = open("dude.prepare_global", 'w')
        try:
            sys.stdout = sys.stderr = f
            cfg.prepare_global()
        except KeyboardInterrupt, e:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print "Interrupted on prepare_global()"
            sys.exit(1)
        finally:
            if f: f.close()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    if not options.global_only:
        # execution loop
        for experiment in experiments:
            # One more run
            actual_runs += 1

            # get dir name and create if necessary
            folder = core.get_folder(cfg, experiment, True)

            # show experiment info
            info.show_exp_info(cfg, experiment, folder,
                               executed_runs+1, missing_runs,
                               total_runs)

            # Execute the measurement
            exp_cpy = experiment.copy()
            (executed, status, etime) = execute_isolated(cfg,
                                                         exp_cpy,
                                                         folder,
                                                         options.show_output)

            if executed:
                info.print_run(actual_runs, status, etime)
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
        if options.show_output:
            f = utils.Tee("dude.finish_global", 'w')
        else:
            f = open("dude.finish_global", 'w')
        try:
            sys.stdout = sys.stderr = f
            cfg.finish_global()
        except KeyboardInterrupt, e:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print "Interrupted on prepare_global()"
            sys.exit(1)
        finally:
            if f: f.close()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

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
