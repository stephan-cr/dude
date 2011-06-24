Design
======

Optspaces and optpts
--------------------
Each experiment has a *configuration*, which is the set of all controllable variables of the experiment, e.g., buffer size of 1024 bytes and timeout of 50 seconds.
The configuration might be "materialized" in a configuration file, in a command line, etc.
For Dude, a configuration called an option point, or *optpt* for short, for example::

  some_optpt = {
    'buffer_size' : 1024,
    'timeout'     : 50
  }  

Each dimension of an optpt has a domain: ``[1024,2048]``, ``[10, 50, 100]``, ``["high.dat", "low.dat"]``, etc.
The n-dimensional space of all option dimensions and their domains is called options space, or *optspace* for short.
For example:: 

  an_optspace = {
    'buffer_size' : [1024, 2048, 4096],
    'timeout'     : [10, 50, 100]
  }

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

Once the results generated on the stardard output are all stored in the expfolder in the file ``dude.output``.
The return value of the program is stored in a file called ``dude.status``.

To check which experiments failed one can use following program.


Timeouts and signals
--------------------

Prepare and finish
------------------

Summaries
---------


Other stuff
===========

Filters
-------

Running "once"
--------------

Visitors
--------

Spawn or fork
-------------
