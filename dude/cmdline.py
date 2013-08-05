# Copyright (c) 2011, 2012 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

"""
cmdline
~~~~~~~

Command line interface.
"""

from . import __version__

import os
import sys
import optparse
import imp
import utils
import summary_backends
import summary
import args
import core
import expgen
import execute
import dimensions
import filter as filt
import clean
import info
import visit

desc = """Commands:
       clean\t\t delete experiments
       create <FOLDER>\t create FOLDER and a Dudefile in it
       failed\t\t list all failed experiments
       info\t\t show experiment description info
       list\t\t list directories of executed experiments
       missing\t\t list all missing experiments
       run\t\t run all missing experiments
       sum [<NAME>]\t summarize results (NAME optional)
       status\t\t show experiments status and running experiment
       visit <CMD>\t execute bash CMD on each experiment folder
"""

parser = optparse.OptionParser(usage="%prog [OPTIONS] <COMMAND> <ARGS>",
                               version="%prog " + __version__,
                               description = desc,
                               formatter = utils.IndentedHelpFormatterWithNL())
parser.add_option("-f", "--file", dest = "expfile",
                  help="read FILE as a Dudefile", metavar = "FILE")
parser.add_option("-x", "--filter", "--select",
                  dest = "filter", metavar = "FILTERS",
                  help = "select experiments using filters written in Dudefile\ne.g. -x filter1,filter2")
parser.add_option("-y", "--filter-inline",
                  dest = "filter_inline", metavar = "FILTERS",
                  help = "select experiments using inline filters separated by semicolons"
                  "\ne.g. -y \"option1=value;option2=[value3,value4]\"")
parser.add_option("-p", "--filter-path",
                  dest = "filter_path", metavar = "PATH",
                  help = "select experiments starting with PATH"
                  "\ne.g. -p \"raw/exp__optionXvalY\"")
parser.add_option("-i",  "--invert-filters", default = False,
                  dest = "invert", action = "store_true",
                  help = "invert filter selection")
parser.add_option("-a", "--args",
                  dest = "margs", metavar = "ARGS",
                  help = "arguments to Dudefile separated by semicolons"
                  "\ne.g. -a \"option1=value;option2=[value3,value4]\"")
parser.add_option("-o", default = False,
                  dest = "show_output", action = "store_true",
                  help = "show experiment's output")

group2 = optparse.OptionGroup(parser, 'run specific options')
group2.add_option("--force", action = "store_true",
                  dest = "force", default = False,
                  help = "force execution")
group2.add_option("--skip-global", default = False,
                  dest = "skip_global", action = "store_true",
                  help = "skip global prepare")
group2.add_option("--global-only", default = False,
                  dest = "global_only", action = "store_true",
                  help = "run global prepare only")

group3 = optparse.OptionGroup(parser, 'sum specific options')
group3.add_option('-b', '--backend', dest = 'backend', default = 'file',
                  help = 'backend to use for summary',
                  choices = summary_backends.backend_names())
group3.add_option('--ignore-status', dest = 'ignore_status',
                  default = False, action = 'store_true',
                  help = 'include failed experiments')

group4 = optparse.OptionGroup(parser, 'list specific options')
group4.add_option("-d", "--dict", action = "store_true",
                  dest = "dict", default = False,
                  help = "show output in dict format")

group5 = optparse.OptionGroup(parser, 'clean specific options')
group5.add_option("--invalid", action = "store_true",
                  dest = "invalid", default = False,
                  help = "remove invalid folders only")

parser.add_option_group(group2)
parser.add_option_group(group3)
parser.add_option_group(group4)
parser.add_option_group(group5)

def main(cargs):
    # folder from where dude is called
    cfolder = os.getcwd()

    # parse command line
    (options, cargs) = parser.parse_args(cargs)

    # check if a command has been given
    if cargs == []:
        parser.print_help()
        sys.exit()

     # create requires no Dudefile, so we deal with it right here
    if cargs[0] == "create":
        if len(cargs) < 2:
            expgen.create()
        else:
            expgen.create(cargs[1])
        sys.exit(0)

    # all other commands require a Dudefile, so we first load it (in "cfg")
    cfg = None

    # use a given dudefile in options
    if options.expfile != None:
        try:
            cfg = imp.load_source('', options.expfile)
        except IOError:
            print >> sys.stderr, 'ERROR: Loading', options.expfile, 'failed'
            parser.print_help()
            sys.exit(1)
    else: # try default file names
        current = os.getcwd()
        max_folder = 10  # arbitrary number of parent directories
        i = 0
        while i < max_folder:
            for f in ['desc.py', 'dudefile', 'Dudefile', 'dudefile.py']:
                try:
                    if os.path.exists(f) and i > 0:
                        print "Opening Dudefile: ", os.path.abspath(f)
                    cfg = imp.load_source('', f)
                    break
                except IOError:
                    pass
            if cfg != None:
                break
            else:
                i += 1
                parent, last = os.path.split(current)
                os.chdir(parent)
                current = parent

        if cfg == None:
            print >> sys.stderr, 'ERROR: no dudefile found'
            parser.print_help()
            sys.exit(1)

    # add to actual folder as root in cfg
    cfg.root = os.getcwd()

    # check if cfg can be used for core functions
    core.check_cfg(cfg)

    # check if cfg can be used for summaries
    summary.check_cfg(cfg)

    # parse arguments to module
    if options.margs:
        margs = args.parse(options.margs)
        print "Passing arguments:", margs
        args.set_args(cfg, margs)

    if hasattr(cfg, 'dude_version') and cfg.dude_version >= 3:
        dimensions.update(cfg)

    experiments = []
    if options.filter != None:
        filters = []
        for f in options.filter.split(','):
            filters.append(cfg.filters[f])
        experiments = filt.filter_experiments(cfg, filters,
                                              options.invert, False)
    elif options.filter_inline:
        experiments = filt.filter_inline(cfg,
                                         options.filter_inline,
                                         options.invert, False)
    elif options.filter_path:
        current = os.getcwd()
        if current != cfolder:
            # this assumes Dudefile is in the root of the experiment folder
            os.chdir(cfolder)
            path = os.path.abspath(options.filter_path)
            os.chdir(current)
            path = os.path.relpath(path) # get raw_output_dir/exp_... format
        else:
            path = options.filter_path

        experiments = filt.filter_experiments(cfg,
                                              filt.filter_path(cfg, path),
                                              options.invert, False)
    else:
        experiments = core.get_experiments(cfg)

    cmd = cargs[0]
    if cmd == 'run':
        if options.force:
            clean.clean_experiments(cfg, experiments)
        execute.run(cfg, experiments, options)
    elif cmd == 'run-once':
        assert len(experiments) == 1
        optpt =  experiments[0]
        folder = "once"
        utils.checkFolder(folder) # create if necessary
        if options.force:
            clean.clean_experiment(folder)
        execute.execute_isolated(cfg, optpt, folder, options.show_output)
    elif cmd == 'sum':
        summary.summarize(cfg, experiments, cargs[1:],
                          options.backend, options.ignore_status)
    elif cmd == 'list':
        for experiment in experiments:
            if options.dict:
                print "experiment:", experiment
            else:
                print core.get_folder(cfg, experiment)
    elif cmd == 'failed':
        failed = core.get_failed(cfg, experiments, False)
        for ffile in failed:
            print ffile
    elif cmd == 'missing':
        failed = core.get_failed(cfg, experiments, True)
        for exp in failed:
            print exp
    elif cmd == 'clean':
        if options.invalid:
            clean.clean_invalid_experiments(cfg, experiments)
        else:
            # TODO if no filter applied, ask if that's really what the
            # user wants.
            r = 'y'
            if options.filter == None and \
                    options.filter_inline == None:
                print "sure to wanna delete everything? [y/N]"
                r = utils.getch() #raw_input("Skip, quit, or continue?
                              #[s/q/c]")

            if r == 'y':
                clean.clean_experiments(cfg, experiments)
    elif cmd == 'visit':
        if len(cargs) < 2:
            print "Specify a bash command after visit"
            sys.exit(1)
        elif len(cargs) > 2:
            print "Surround multi-term bash commands with \"\"."
            print "e.g., \"%s\"" % ' '.join(cargs[1:])
            sys.exit(1)
        visit.visit_cmd_experiments(cfg, experiments, cargs[1])
    elif cmd == 'info':
        info.show_info(cfg, experiments)
    elif cmd == 'status':
        info.print_status(cfg, experiments)
    else:
        print >> sys.stderr, "ERROR: wrong command. %s" % cargs[0]
        parser.print_help()
