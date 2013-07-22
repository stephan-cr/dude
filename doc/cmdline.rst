Dude command-line 
==================

.. program:: dude

Information and basic commands
------------------------------

.. cmdoption:: info

   Show informations about the experiments.

.. cmdoption:: list

   List all expfolders.

.. cmdoption:: run

   Run experiments (only those that haven't been run or that have failed).

.. cmdoption:: sum

   Summarize experiments that successfully ran.


.. cmdoption:: failed

   Show all experiments that failed (returned code different than 0).

.. cmdoption:: missing 

   Show all experiments that haven't been executed or have failed.
      
.. cmdoption:: -f <FILE>, --file <FILE>

   Read FILE as a Dudefile. Default ``FILE=Dudefile``.


Filtering experiments
---------------------

.. cmdoption:: -y, --filter-inline

  Select experiments using inline filters separated by semicolons::
  
    dude run/list/sum -y "option1=value;option2=[value3,value4]"

.. cmdoption:: -p, --filter-path

  Select experiments starting with PATH::
  
    dude run/list/sum -p raw/exp__optionXvalY

.. cmdoption:: -i, --invert-filters

   Invert filter selection. Example::

     dude run/list/sum -i -y "option1=value;option2=[value3,value4]"


.. _run-options:

Run specific options
--------------------

.. cmdoption:: -o

   Show experiment's output.

.. cmdoption:: --force
 
   Force execution. For example::

     dude run --force -y "option1=value;option2=[value3,value4]"


.. cmdoption:: --skip-global

   Skip global prepare.

.. cmdoption:: --global-only

   Run global prepare only.


Sum specific options
--------------------

.. cmdoption:: --ignore-status

   Include failed experiments in the summaries.

.. cmdoption:: -b, --backend
   
   Default backend is file.

   Backend to use for summary: sqlite3, json, and file.


List specific options
---------------------

.. cmdoption:: -d, --dict

   Show output in dict format.
    
Advanced commands and options
-----------------------------

.. cmdoption:: run-once

   Creates a folder called "once" and runs one experiment inside. The
   selection with -y or -x or -p is necessary such that only one
   experiments is selected.

.. todo: fix run-once description.

Advanced filtering can be achieved with the following command-line options.

.. cmdoption:: -x <filter>, --filter <filter>, --select <filter>

   Select experiments using filters written in Dudefile.
   One can use multiple filters, for example::
   
     dude run/list/sum -x filter1,filter2

   The filter has to be implemented inside the Dudefile. (More details TBD)

.. cmdoption:: -a, --args

   Give arguments to Dudefile separated by semicolons::

     dude run/list/sum -a "option1=value;option2=[value3,value4]"
