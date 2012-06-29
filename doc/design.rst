Design
======

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



Timeouts and signals
--------------------

By default, an experiment can take an unbounded amount of time to terminate.
If the user wants to limit this time, a ``timeout`` variable can be set in the Dudefile (seconds as unit).
If the experiment times out, it is killed by Dude.
Similarly, if the user presses "ctrl-c", any running experiment is immediately killed.


.. _summaries:

Summaries
---------

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
~~~~~~~~~~~~~~~~~~~~~~~

LineSelect and MultiLineSelect 

.. autoclass:: dude.summaries.LineSelect
   :members:
   :inherited-members:

.. autoclass:: dude.summaries.MultiLineSelect
   :members:
   :inherited-members:

file summaries
~~~~~~~~~~~~~~

.. autoclass:: dude.summaries.FilesLineSelect
   :members:
   :inherited-members:

.. autoclass:: dude.summaries.FilesMultiLineSelect
   :members:
   :inherited-members:

other summaries
~~~~~~~~~~~~~~~

.. autoclass:: dude.summaries.JsonSelect
   :members:
   :inherited-members:

Backends
~~~~~~~~

Over time some different backends turned out to be useful.
Dude supports file, json and sqlite backends.


.. _prepare_exp:

Prepare and finish
------------------

Prepare_exp

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

Spawn or fork
-------------

