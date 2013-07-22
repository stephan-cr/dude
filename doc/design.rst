Overall structure
=================

Optspaces and optpts
--------------------
Each experiment has a *configuration*, which is the set of all controllable variables of the experiment, e.g., buffer size of 1024 bytes and timeout of 50 seconds.
The configuration might be "materialized" in a configuration file, in a command line, etc.
For Dude, a configuration is called an option point, or *optpt* for short, for example::

  some_optpt = {
    'buffer_size' : 1024,
    'timeout'     : 50
  }

Each dimension of an optpt has a domain: ``[1024, 2048]``, ``[10, 50, 100]``, ``["high.dat", "low.dat"]``, etc.
The n-dimensional space of all option dimensions and their domains is called options space, or *optspace* for short.
For example::

  an_optspace = {
    'buffer_size' : [1024, 2048, 4096],
    'timeout'     : [10, 50, 100]
  }


.. _constraints:

Constraints
-----------
By default, Dude generates all the optpts of an optspace by calculating its cartesian product.
Parts of the optspace can be however removed by using *constraints*.
A constraint is a *function* that takes an optpt as parameter and returns ``True`` if the optpt is valid otherwise ``False``.
For example, assume that performing an experiment with ``buffer_size`` of 4kB only makes sense if the ``timeout`` is at least 50.
This constraint can be expressed as the following function::

  def my_constraint(optpt):
    if optpt['buffer_size'] == 4096:
      return optpt['timeout'] >= 50
    else:
      return True

Directory structure and runs
----------------------------

Dude executes the experiments in time and space isolation.
It starts experiments sequentially, hence, avoiding contention on resources such as network adapters, CPUs, etc.
.. To start multiple experiments concurrently, multiple instances of Dude can be started.
Additionally, Dude starts each experiment with a different *expfolder* as working directory.
An experiment can write and read from its working directory without interfering or being interfered by other experiments.
When first started, Dude creates a ``raw`` subfolder and for each experiment a subfolder in ``raw``, for example ``raw/exp__buffer_size1024__timeout50``.
The latter are called *expfolders*.
While an optpt represents the configuration of an experiment, the expfolder is the *results* of an experiment.

Once an experiment is finished, either correctly or by crashing, its results on the standard output and its return value are stored in the files ``dude.output`` and ``dude.status`` respectively, both placed in the experiment's expfolder.

.. important:: It is recommended that any other file the experiment generates to be stored in the process' working directory, which is always the expfolder. If that is not the case, Dude provides a method to be called after the experiment, which can be used to copy the desired results to the expfolder.


Run details
===========

.. _spawn_or_fork:

Spawn or fork
-------------

There are two types of experiments that Dude can start: command lines or forked process.
You can define only one of them in your Dudefile.
Command-line experiments are executed if the ``cmdl_exp(optpt)`` method is defined.
``cmdl_exp`` must return the command line to be executed as a string, for example::

  def cmdl_exp(optpt):
    return "echo buffer_size=%d" % optpt['buffer_size']

In this example, when ``dude run`` is issued on the terminal, the command line ``echo buffer_size=X`` will be called for every value of X defined in the ``buffer_size`` dimension of the optspace. 

Forked-process experiments are executed if the ``fork_exp(optpt)`` method is defined. There are two use cases for ``fork_exp``. First, for experiments that are very simple such that they can be expressed as a couple of python lines of code, for example::

  def fork_exp(optpt):
    r = is_prime(optpt['number'])
    if r: print r, "is prime"
    else: print r, "is not prime"

The second use case is for very complex which need several commands, possibly running in parallel. For example, let's assume we want to experiment with a client and a server program varying parameters of both programs::

  import subprocess
  def fork_exp(optpt):
    s = subprocess.Popen('my_server --buffer=%d' %\
                   optpt['server_buffer_size'], 
                   stdout = sys.stdout, stderr = sys.stderr)

    c = subprocess.Popen('my_client --buffer=%d --threads=%d --timeout=%d' %\
                   optpt['client_buffer_size'], 
		   optpt['client_threads'],
		   optpt['experiment_time'],
                   stdout = sys.stdout, stderr = sys.stderr)

    # Block until client is done.
    rc = c.wait() 
    # If the return code is different from 0, there was an error. 
    # We can either assert that, or return the error code as return value.
    assert rc == 0, "client failed"

    # Terminate server with SIGTERM. We assume it handles the signal and
    # exits with 0.
    s.terminate()
    rs = s.wait()

    # Return the retcode of the server. In this example if the server or the
    # client failed, the experiment must be repeated/fixed.
    return rs


When ``dude run`` is issued on the terminal, the Dude process is forked just before calling ``fork_exp`` for every optpt in the optspace.
If the ``fork_exp`` fails with an assertion, throwns an exception, or returns a value different from 0, the experiment is marked as failed.

.. warning:: subprocesses spawned inside ``fork_exp`` must have stdout and stderr set to ``sys.stdout`` and ``sys.stderr`` respectively. Otherwise, Dude cannot log their output (see :ref:`logging` for details). 


Timeouts and signals
--------------------

By default, an experiment can take an unbounded amount of time to terminate.
If the user wants to limit this time, a ``timeout`` variable can be set in the Dudefile (seconds as unit).
If the experiment times out, it is killed by Dude.
Similarly, if the user presses "ctrl-c", any running experiment is immediately killed.

.. _prepare_exp:

Prepare and finish
------------------

Dude provides hooks which are executed before and after every experiment.
You can use ``prepare_exp(optpt)`` to create configuration files for your experiment, and ``finish_exp(optpt, status)`` to perform cleanup actions.

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
    return "my_program -f config.txt"

  def finish_exp(optpt, status):
    if status == 0:
      cleanup_program_successful()
    else:
      cleanup_program_failed()

.. _logging:

Output logging
--------------

Dude redirects the output (stdout and stderr) of each experiment to a log file.
In particular, ``dude.prepare_exp``, ``dude.output``, and ``dude.finish_exp`` log files will be created, corresponding to the different phases of an experiment.
See :ref:`run-options` for information on how to display the output on the screen.

.. _optptcmp:

Execution order
---------------

Dude executes experiments in some "random" order decided by the ``cmp`` built-in Python method.
Sometimes it can be useful to define the order in which experiments are going to be executed.
Dude provides the optional function ``optpt_cmp(optpt1, optpt2)`` for that, which can be define in your Dudefile and should implement the ``cmp`` interface (See `cmp documentation <http://docs.python.org/2/library/functions.html#cmp>`_ for details).

The most common use of this feature is to tell Dude to iterate on the dimensions in some order.
For example, we would like test a server and a client application with the following options::

  optspace = {
    'server_buffer_size' : [1024, 2048, 4096],
    'client_buffer_size' : [1024, 2048, 4096]
  }

The server takes long to start, so it would be good to test first all client options before restarting the server with another option (see :ref:`spawn_or_fork` for an example on how to start multiple processes).
Our Dudefile could look like this::

  from dude.defaults import order_dim
  optpt_cmp = order_dim(['server_buffer_size', 'client_buffer_size'])

  last_server_buffer_size = None
  def fork_exp(optpt):
    if last_server_buffer_size != optpt['server_buffer_size']:
      stop_server()
      last_server_buffer_size = optpt['server_buffer_size']
      rc = start_server(optpt)
      assert rc == 0, "server failed on start"

    rc = start_client(optpt)
    # return client's return code
    return rc
   
``order_dim`` is a helper function defined in ``dude.defaults`` that order the dimensions in the list order given as argument.
In the example, first all ``client_buffer_size`` values would be executed before the ``server_buffer_size`` would change.


.. _summaries:

Summaries details
=================

Summaries are used to extract information from executions. 
Summaries are usually used to perform simple aggregations only; tools such as Gnuplot, matplotlib and R can be used for further aggregation, analysis and plotting.

Summaries are added to the ``summaries`` variables in a Dudefile, for example::

      import dude.summaries
      summaries = [ dude.summaries.LineSelect('my_summary') ]


Since version Dude 3.1 summaries inherit a single SummaryBase class. All the following parameters are available in any summary.


.. autoclass:: dude.summaries.SummaryBase
   :members:

Summaries can either process output from the stdout/stderr of a program execution or from files generated during the execution.

stdout/stderr summaries
-----------------------

LineSelect and MultiLineSelect 

.. autoclass:: dude.summaries.LineSelect
   :members:
   :inherited-members:

.. autoclass:: dude.summaries.MultiLineSelect
   :members:
   :inherited-members:

file summaries
--------------

.. autoclass:: dude.summaries.FilesLineSelect
   :members:
   :inherited-members:

.. autoclass:: dude.summaries.FilesMultiLineSelect
   :members:
   :inherited-members:

other summaries
---------------

.. autoclass:: dude.summaries.JsonSelect
   :members:
   :inherited-members:

Backends
--------

Over time some different backends turned out to be useful.
Dude supports file, json and sqlite backends.

Other stuff
===========

Filters
-------

Inline filters
~~~~~~~~~~~~~~

Complex filters
~~~~~~~~~~~~~~~

Running "once"
--------------


.. _remote_experiments:

Remote experiments
------------------


