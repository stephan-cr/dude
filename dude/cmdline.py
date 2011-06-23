"""
    cmdline
    ~~~~~~~

    Command line interface.

    :copyright: Copyright (c) 2011 Diogo Becker
    :license: MIT, see LICENSE for details.

"""
from dude import __version__

import os
import sys
import optparse
import imp
import utils
import summaries
import summary_backends
import summary
import args
import core
import expgen
import execute
import dimensions
import filter as filt
import clean

desc = """Commands:
       clean\t delete experiments
       failed\t list all failed experiments
       info\t show experiment description info
       list\t list directories of executed experiments
       missing\t list all missing experiments
       run\t run all experiments
       sum\t summarize results using given summaries
"""

parser = optparse.OptionParser(usage="%prog [options] command",
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
parser.add_option("-i",  "--invert-filters", default = False,
                  dest = "invert", action = "store_true",
                  help = "invert filter selection")
parser.add_option("-a", "--args",
                  dest = "margs", metavar = "ARGS",
                  help = "arguments to Dudefile separated by semicolons"
                  "\ne.g. -a \"option1=value;option2=[value3,value4]\"")
parser.add_option("--dry", default = False,
                  dest = "dry", action = "store_true",
                  help = "dry run (sets global dry variable to True)")
group2 = optparse.OptionGroup(parser, 'run specific options')
group2.add_option("-n","--no-output", action = "store_false",
                  dest = "show_output", default = True,
                  help = "omit the output of experiment")
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

group4 = optparse.OptionGroup(parser, 'list specific options')
group4.add_option("-d", "--dict", action = "store_true",
                  dest = "dict", default = False,
                  help = "show output in dict format")

parser.add_option_group(group2)
parser.add_option_group(group3)
parser.add_option_group(group4)

def main(cargs):
     # parse command line
     (options, cargs) = parser.parse_args(cargs)

     # check if a command has been given
     if cargs == []:
          parser.print_help()
          sys.exit()

     # create requires no Dudefile, so we deal with it right here
     if cargs[0] == "create":
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
          for f in ['desc.py', 'dudefile', 'Dudefile', 'dudefile.py']:
               try:
                    cfg = imp.load_source('', f)
                    break
               except IOError:
                    pass
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

     # set dry run variable
     if options.dry:
          cfgdry = True
     else:
          cfgdry = False

     # parse arguments to module
     if options.margs:
          margs = args.parse(options.margs)
          print "arguments to Dudefile:", margs
          args.set_args(cfg, margs)

     if hasattr(cfg, 'dude_version') and cfg.dude_version >= 3:
          dimensions.update(cfg)

     # TODO: the selection of experiments and how that interact with the commands should be redone.
     # the last parameter to filter_experiments include or exclude the not yet run experiments

     experiments = []
     if options.filter != None:
          filters = []
          for f in options.filter.split(','):
               filters.append(cfg.filters[f])
          experiments = filt.filter_experiments(cfg, filters, options.invert, True)
     elif options.filter_inline:
          experiments = filt.filter_inline(cfg, options.filter_inline, options.invert, False)
     else:
          experiments = core.get_run_experiments(cfg)

     cmd = cargs[0]
     if cmd == 'run':
          execute.init()
          if options.force:
               clean.clean_experiments(cfg, experiments)
          execute.run(cfg, experiments, options)
     elif cmd == 'run-once':
          assert len(experiments) == 1
          optpt =  experiments[0][1]
          execute.init()
          folder = "once"
          utils.checkFolder(folder) # create if necessary
          if options.force:
               clean.clean_experiment(folder)
          execute.execute(cfg, optpt, 1, options.show_output, folder)
     elif cmd == 'sum':
          summary.summarize(cfg, experiments, cargs[1:], options.backend)
     elif cmd == 'list':
          for run, experiment in experiments:
               if options.dict:
                    print "run:",run, "experiment:", experiment
               else:
                    print core.get_folder(cfg, experiment, run)
     elif cmd == 'failed':
          failed = core.get_failed(cfg, False)
          for ffile in failed:
               print ffile
     elif cmd == 'missing':
          failed = core.get_failed(cfg, True)
          for exp in failed:
               print exp
     elif cmd == 'force-fail':
          print "ERROR: Command not implemented!"
          sys.exit(1)
     elif cmd == 'clean':
          # TODO if no filter applied, ask if that's really what the user wants.
          r = 'y'
          if options.filter == None and options.filter_inline == None:
               print "sure to wanna delete everything? [y/N]"
               r = utils.getch() #raw_input("Skip, quit, or continue? [s/q/c]")

          if r == 'y':
               clean.clean_experiments(cfg, experiments)
     elif cmd == 'info':
          info.show_info(cfg)
     else:
          print >> sys.stderr, "ERROR: wrong command. %s" % cargs[0]
          parser.print_help()