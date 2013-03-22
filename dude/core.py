# Copyright (c) 2010, 2011, 2012 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""
Core functionality consists of generating points in the options space
and generating names out of options.
"""
import os
import sys
import fcntl
import utils

### some constants ####
SEP = '__'
statusFile = 'dude.status'
outputFile = 'dude.output'
lockFile   = 'dude.lock'


def get_experiments(cfg):
    """Creates a list of experiments."""
    # TODO: sampling
    exps = utils.cartesian(cfg.optspace)
    if hasattr(cfg, 'constraints'):
        for c in cfg.constraints:
            exps_tmp = []
            for exp in exps:
                if c(exp):
                    exps_tmp.append(exp)
            exps = exps_tmp

    if hasattr(cfg, 'optpt_cmp'):
        if sys.version_info < (3, 2):
            exps.sort(cmp=cfg.optpt_cmp)
        else:
            # starting from Python3.2 the `cmp` parameter is removed
            # functools.cmp_to_key is introduced since Python2.7 and Python3.2
            import functools
            exps.sort(key=functools.cmp_to_key(cfg.optpt_cmp))

    return exps

def get_raw_folder(cfg):
    """Gets the raw folder of the experiments. Create it if necessary"""
    # get raw output folder
    folder = cfg.raw_output_dir
    utils.checkFolder(folder)
    return folder

def get_name(prefix, optpt):
    """
    Given a prefix and an optpt, creates the a string to identify the
    experiment.
    """
    s = prefix
    l = optpt.keys()
    l.sort()
    for k in l:
        s += SEP + k
        st = ''.join(str(optpt[k]).split(' '))
        s += ''.join(os.path.split(st))
    return s

def get_folder(cfg, experiment, check = True):
    """Returns the experiment folder. Creates it if necessary."""
    folder = get_raw_folder(cfg)
    if check:
        utils.checkFolder(folder)

    # add experiment subfolder
    folder = os.path.join(folder, get_name('exp', experiment))
    utils.checkFolder(folder)
    return folder

def exist_status_file(folder):
    """Checks if status file exist for a given experiment"""
    return os.path.exists(os.path.join(folder, statusFile))

def read_status_file(folder):
    """Reads value of status file for a given experiment"""
    f = open(os.path.join(folder, statusFile), 'r')
    val = int(f.readline())
    f.close()
    return val


def experiment_success(cfg, experiment):
    """Checks if experiment ran correctly"""
    outputFolder = get_folder(cfg, experiment)
    oFile   = os.path.join(outputFolder, outputFile)
    sFile   = os.path.join(outputFolder, statusFile)
    lFile   = os.path.join(outputFolder, lockFile)

    if not os.path.exists(oFile) or not os.path.exists(sFile) \
            or os.path.exists(lFile):
        # it didn't run yet (or it is running), return None
        return False
    f = open(sFile, 'r')
    try:
        val = int(f.readline())
    except ValueError: # there's no number to read
        return False
    finally:
        f.close()
    if val != 0:
        # it didn't run successfully, return None
        return False
    return True


def experiment_ran(cfg, experiment):
    """Checks if experiment ran"""
    outputFolder = get_folder(cfg, experiment)
    oFile   = os.path.join(outputFolder, outputFile)
    sFile   = os.path.join(outputFolder, statusFile)
    lFile   = os.path.join(outputFolder, lockFile)

    if os.path.exists(lFile) or not os.path.exists(oFile) \
            or not os.path.exists(sFile):
        return False
    else:
        return True


def get_failed(cfg, missing = False):
    """Get the list of output files of executions that failed """
    failed = []
    experiments = get_experiments(cfg)
    for exp in experiments:
        outputFolder = get_folder(cfg, exp)
        oFile   = os.path.join(outputFolder, outputFile)
        sFile   = os.path.join(outputFolder, statusFile)
        lFile   = os.path.join(outputFolder, lockFile)

        if os.path.exists(lFile) or not os.path.exists(sFile):
            if missing:
                failed.append(exp)
                continue
            else:
                # not run
                continue

        f = open(sFile, 'r')
        try:
            val = int(f.readline())
        except ValueError: # there's no number to read
            return False
        finally:
            f.close()
        if val != 0:
            if not missing:
                failed.append(oFile)
            else:
                failed.append(exp)
    return failed

# def success_count(cfg, experiments):
#     c = 0
#     for run in range(1, cfg.runs+1):
#         for e in experiments:
#             if experiment_success(cfg, e, run):
#                 c += 1
#     return c

def success_count(cfg, experiments):
    c = 0
    for experiment in experiments:
        if experiment_success(cfg, experiment):
            c += 1
    return c

def experiment_running(cfg, experiment):
    """ Return None if not running, otherwise return pid of process
    running experiment."""
    folder = get_folder(cfg, experiment)
    lFile  = os.path.join(folder, lockFile)

    if os.path.exists(lFile):
        try:
            f = open(lFile, "r")
            pid = int(f.readline())
        except TypeError:
            print "Error reading lock file %s" % lFile
            sys.exit(1)
        finally:
            f.close()
        return pid
    else:
        return None

def experiment_lock(cfg, folder):
    """Lock an experiment folder"""
    lFile  = os.path.join(folder, lockFile)

    if os.path.exists(lFile):
        return False
    else:
        f = open(lFile, 'w')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            f.write("%d\n" % os.getpid())
        except IOError:
            return False
        finally:
            f.close()

        return True

def experiment_unlock(cfg, folder):
    """Unlock an experiment folder"""
    lFile  = os.path.join(folder, lockFile)

    assert os.path.exists(lFile), "Lock file was removed by another process"
    os.remove(lFile)

def check_cfg(cfg):
    """
    Verifies if loaded configuration file has fields necessary for
    this module.
    """
    assert hasattr(cfg, 'dude_version')
    assert getattr(cfg, 'dude_version') >= 3

    if not hasattr(cfg, 'name'):
        setattr(cfg, 'name', os.getcwd())

    assert hasattr(cfg, 'optspace')
    assert type(cfg.optspace) == dict

    if hasattr(cfg, 'constraints'):
        assert type(cfg.constraints) == list
    else:
        cfg.constraints = []

    assert hasattr(cfg, 'raw_output_dir')

    if hasattr(cfg, 'runs'):
        print "WARNING: runs is DEPRECATED. IGNORED"

    # TODO remove
    if not hasattr(cfg, 'timeout'):
        cfg.timeout = None
