Overview
========

The Dude is a framework to generate configurations, execute experiments, and process results into summaries.
An *experiment* is the run of a program given input files, arguments, etc, and resulting in some output on the standard output, in a file, or even in a database.
Dude uses as feed a *Dudefile*, which describes a complete set of experiments.
Based on this file, Dude creates command lines for each experiment and, if necessary, configuration files of any complexity.

Optspaces and optpts
--------------------
A set of experiments is described by an option space, *optspace* for short, and each experiment by an option point in this space, or simply *optpt*. An example of an *optspace* for some arbitrary program is the following::

  an_optspace = {
    'buffer_size' : [1024, 2048, 4096],
    'timeout'     : [10, 50, 100]
  }


Each dimension of the optspace has a domain: ``[1024,2048]``, ``[10, 50, 100]``, ``["high.dat", "low.dat"]``, etc.
An optpt in this space (i.e., an experiment) is for example::

  some_optpt = {
    'buffer_size' : 1024,
    'timeout'     : 50
  }  


From optpts to command lines
----------------------------

The most basic usage of Dude is the creation of command lines based on optpts.
For that, the user provides in the Dudefile a simple method called ``cmdl_exp`` which transforms an optpt into a string. 
For example, our program is ``echo`` and simply print on the screen the buffer size::

    def cmdl_exp(optpt):
    	return "echo buffer_size=%d" % optpt['buffer_size']

When Dude is invoked, it generates all optpts of an optspace by calculating its cartesian product. 
It then creates for each experiment a folder, and spawns the command line inside this folder.
A minimal Dudefile follows::

  from dude.defaults import *
  dude_version = 3

  optspace = {
      'buffer_size' : [1024, 2048, 4096],
      'timeout'     : [10, 50, 100]
  }

  def cmdl_exp(optpt):
    return "echo buffer_size=%d timeout=%d" %\
      (optpt['buffer_size'], optpt['timeout'])


Calling the Dude
----------------

To start executing experiments, Dude has to be called from the command line in any folder where a Dudefile exists with a ``run`` argument:

.. code-block:: console

  examples/echo$ dude run 

The experiments are started sequentially in different folders.
When first started, Dude creates a ``raw`` subfolder and for each experiment a subfolder in it, for example ``raw/exp__buffer_size1024__timeout50``.
Therefore, the experiments can write in the their root folders without conflicting with each other.
The subfolders where experiments are executed are called *expfolders*.
Once an experiment is finished, either correctly or by crashing, its results generated on the stardard output and its return value are stored in the files ``dude.output`` and ``dude.status`` respectively, both placed in the experiment's expfolder.



.. To check which experiments failed one can use following program.




..   examples/updown$ cat muddi.cfg 
..   upload   = [('sedell08', ['muddi.cfg'], '/tmp')]
..   cmds     = [('sedell08', 'mv /tmp/muddi.cfg /tmp/muddi2.cfg && echo "#some comment" >> /tmp/muddi2.cfg')]
..   download = [('sedell08', ['/tmp/muddi2.cfg'], '.')]
..   logdir   = None

..   examples/updown$ muddi -f muddi.cfg upload
..   # muddi: ('timeout = 300 seconds',)
..   # muddi: (['scp', 'muddi.cfg', 'sedell08:/tmp'], 'STARTED')
..   # muddi: ('first phase =', [0], ' | second phase =', [])

..   examples/updown$ muddi -f muddi.cfg execute
..   # muddi: ('timeout = 300 seconds',)
..   # muddi: (['ssh', 'sedell08', 'mv /tmp/muddi.cfg /tmp/muddi2.cfg && echo "#some comment" >> /tmp/muddi2.cfg'], 'STARTED')
..   # muddi: ('first phase =', [0], ' | second phase =', [])

..   examples/updown$ muddi -f muddi.cfg download
..   # muddi: ('timeout = 300 seconds',)
..   # muddi: (['scp', 'sedell08:/tmp/muddi2.cfg', '.'], 'STARTED')
..   # muddi: ('first phase =', [0], ' | second phase =', [])

..   examples/updown$ cat muddi2.cfg 
..   upload   = [('sedell08', ['muddi.cfg'], '/tmp')]
..   cmds     = [('sedell08', 'mv /tmp/muddi2.cfg && echo "#some comment" >> /tmp/muddi2.cfg')]
..   download = [('sedell08', ['/tmp/muddi2.cfg'], '.')]
..   logdir   = None
..   #some comment


.. The folder structure of Dude ...

Summaries
---------

Dude can collect, filter, aggregate any information from the experiments.
For that the user simply invokes Dude as follows:

.. code-block:: console

  examples/echo$ dude sum


By default, Dude simply concatenates the output to the stdout of every experiment into the file ``output/default``.
After calling ``dude run``, the user can access this file with any program to further process or plot this data, for example:
 
.. code-block:: console

  examples/echo$ cat output/default 

  1024 10 buffer_size=1024 timeout=10
  1024 50 buffer_size=1024 timeout=50
  1024 100 buffer_size=1024 timeout=100
  2048 10 buffer_size=2048 timeout=10
  2048 50 buffer_size=2048 timeout=50
  2048 100 buffer_size=2048 timeout=100
  4096 10 buffer_size=4096 timeout=10
  4096 50 buffer_size=4096 timeout=50
  4096 100 buffer_size=4096 timeout=100


Other ``summary`` objects can be added directly to the Dudefile::
      
      import dude.summaries
      summaries = [ dude.summaries.LineSelect('stdout') ]  


From optpts to configuration files
----------------------------------

Dude can generate configuration files before executing the command line returned by ``cmdl_exp``.
For that the user has to provide an ``prepare_exp`` method, which is invoked inside the experiment's folder.
Here is an example::

  dude_version = 3
  from dude.defaults import *

  optspace = {
      'buffer_size' : [1024, 2048, 4096],
      'timeout'     : [10, 50, 100]
  }

  def init_exp(optpt):
    f = open("config.txt","w")
    print >>f, "buffer_size=%d timeout=%d" %\
      (optpt['buffer_size'], optpt['timeout'])
    f.close()

  def cmdl_exp(optpt):
    return "cat config.txt"


Because Dude runs the experiments in separate expfolders, ``prepare_exp'' do not overwrite the configuration files of other experiments even if they are named in the same way for all experiments.


