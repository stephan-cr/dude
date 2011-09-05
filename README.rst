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
paths to your PATH and PYTHONPATH enviroment variables, for example,
by adding the following in your .bashrc, .profile or .zshrc::

    export PATH=$PATH:$HOME/local/bin
    export PYTHONPATH=$PYTHONPATH:$HOME/local/lib/python

To test if everything is correcly installed, just type::

    % dude

Documentation
-------------

**TODO** how to read the documentation

Contribute
----------

Contributions or feedback in any form are welcome. Issues, bugs and
feature requests can be reported at:
https://bitbucket.org/db7/dude/issues
