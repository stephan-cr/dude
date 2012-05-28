====
Dude
====

The Dude is a framework to describe a set of configurations, to
execute them in experiments and to process the results into
summaries. Dude uses a description file in
Python_ to prepare, execute and summarize
experiments.

.. _Python: http://www.python.org/

Installation
------------

For those who are getting it for the first time::

    % hg clone https://bitbucket.org/db7/dude

In both cases, don't forget to install it afterwards. The installation
in /usr/local can be done with::

    % sudo python setup.py install

To install in your $HOME (not su), you can use the --home option,
e.g.::

    % python setup.py install --home=$HOME/local

This will copy the executable scripts in $HOME/local/bin and the
python libraries in $HOME/local/lib/python. You have to add these
paths to your PATH and PYTHONPATH environment variables, for example,
by adding the following in your .bashrc, .profile or .zshrc::

    export PATH=$PATH:$HOME/local/bin
    export PYTHONPATH=$PYTHONPATH:$HOME/local/lib/python

To test if everything is correctly installed, just type::

    % dude

Workflow
--------

To get an idea of the workflow using Dude, the following lines will
give you a rough outline.

To work with Dude you first have to create a *Dudefile* where you
describe a set of experiments and how to summarize the data produced
by these experiments (the "examples" subdirectory may help you). Dude
has a command to create a Dudefile template for you::

    % dude create <directory where you want to run your experiments>

After you made your changes, you can run the experiments::

    % dude run

You can run this command again when you discover that one experiment
crashed. Dude will only run experiments which were not already
executed or failed experiments. You can see all missing experiments by
issuing::

    % dude missing

and all failed experiments::

    % dude failed

If Dude is finished, you usually collect and process all data /
observations produced by your experiments. This is done by summarizing
your experiments::

    % dude sum

You can use any tool you want to further process the final summaries.

Documentation
-------------

More details can be found in the `full documentation`_.

.. _full documentation: http://dude.readthedocs.org.

Contribute
----------

Contributions or feedback in any form are welcome. Issues, bugs and
feature requests can be reported at:
https://bitbucket.org/db7/dude/issues
