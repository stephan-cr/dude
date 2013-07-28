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


Each dimension of the optspace has a domain: ``[1024, 2048]``, ``[10, 50, 100]``, ``["high.dat", "low.dat"]``, etc.
An optpt in this space is for example::

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

Alternatively, you can define ``fork_exp(optpt)`` *instead* of ``cmdl_exp(optpt)``. If ``fork_exp`` is defined, Dude will fork its execution and consider the forked process as the experiment. See :ref:`spawn_or_fork` section for more details on these alternatives, and see :ref:`remote_experiments` for information on how to start experiments remotely.

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


.. hint:: Dude allows the user to define :ref:`constraints` to limit the optpts to a subset of the optspace.

Calling the Dude
----------------

`dude` is a command line tool which accepts several commands to start, stop, delete, filter, and aggregate experiments.
It is usually started in a folder where there is a Dudefile (see ``examples/echo`` for an example).
The command ``info`` shows an overview of the Dudefile in the current folder:

.. code-block:: console

   examples/echo$ ls
   Dudefile
   examples/echo$ dude info
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   Experiment set: examples/echo
   --------------------------------------------------------------------------------
   Option space:
   	        buffer_size = [1024, 2048, 4096]
          	    timeout = [10, 50, 100]
   Experiments: complete space
   Summaries  : ['default']
   Timeout    : None
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





The typical workflow of a user consists of four steps, two of them performed by Dude:

1. Creation of a Dudefile;
2. Execution of experiments upon invocation of ``dude run``;
3. Aggregation of results upon invocation of ``dude sum``;
4. Use of resulting aggregations for further plotting and analysis.


Execution
^^^^^^^^^

To start executing experiments, Dude is invoked from the command line with a ``run`` argument in any folder where a Dudefile exists:

.. code-block:: console

  examples/echo$ dude run

  ...


Dude executes the experiments in time and space isolation.
Experiments are started sequentially by Dude, hence, avoiding contention on resources such as network adapters, CPUs, etc.
Additionally, an experiment can write and read from its working directory without interfering or being interfered by other experiments.
When first started, Dude creates a ``raw`` subfolder and for each experiment a subfolder in ``raw``, for example ``raw/exp__buffer_size1024__timeout50``.
The latter are called *expfolders*.
The working directory of the experiments are always their expfolders.

Once an experiment is finished, either correctly or by crashing, its results on the standard output and its return value are stored in the files ``dude.output`` and ``dude.status`` respectively, both placed in the experiment's expfolder.
For checking which experiments failed, one can simply type:

.. code-block:: console

  examples/echo$ dude failed
  raw/exp__buffer_size1024__timeout100/dude.output


In this example, the experiment with optpt ``{ 'buffer_size' : 1024, 'timeout' : 100 }`` returned with a value different than 0 (it failed).
When invoking ``dude run`` again, only failed (or not yet run) experiments are executed.
Dude provides several other commands to manage expfolders (see TBD).

.. hint:: See :ref:`optptcmp` to learn how to specify the execution order of the experiments.

Summaries
^^^^^^^^^

Dude can collect, filter, aggregate any information from experiments with :ref:`summaries`.
For that the user invokes

.. code-block:: console

  examples/echo$ dude sum


By default, Dude simply concatenates the output to the stdout of every experiment into the file ``output/default``.
After calling ``dude sum``, the user can access the resulting aggregation file with any program to further process, analyze or plot it, for example:

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


Dude provides several :ref:`summary <summaries>` classes which can be added directly to the Dudefile as follows::

      import dude.summaries
      summaries = [ dude.summaries.LineSelect('stdout') ]

Additionally, the user can extend any of the summaries and add it to the ``summaries`` variable in the Dudefile.


From optpts to configuration files
----------------------------------

Dude can generate configuration files before executing the command line returned by ``cmdl_exp``.
For that the user has to provide an :ref:`prepare_exp` method, which is invoked inside the experiment's folder.
Here is an example::

  dude_version = 3
  from dude.defaults import *

  optspace = {
      'buffer_size' : [1024, 2048, 4096],
      'timeout'     : [10, 50, 100]
  }

  def prepare_exp(optpt):
    f = open("config.txt","w")
    print >>f, "buffer_size=%d timeout=%d" %\
      (optpt['buffer_size'], optpt['timeout'])
    f.close()

  def cmdl_exp(optpt):
    return "cat config.txt"


Because Dude runs the experiments in separate expfolders, ``prepare_exp`` do not overwrite the configuration files of other experiments even if they are named in the same way for all experiments.
