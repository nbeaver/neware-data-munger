.. -*- coding: utf-8 -*-

====================================================
Neware battery testing report data conversion script
====================================================

This is a script for converting `Neware`_ battery testing data into a more convenient format for plotting.

It requires `Python 2.7`_.

Usage::

    $ python extract-from-general-report.py --input input.txt --mass 1.5

or::

    $ python extract-from-general-report.py
    Enter filename: input.txt
    Enter mass of active material in mg, or just press enter to calculate mAh:1.5

Note that the input file must be tab-delimited,
so keep this in mind if you export an Excel file and then convert it to a ``.csv`` file.

Currently only works with the "General Report" export type.
    
----
TODO
----

- Use existing mass if datafile contains it (e.g. "This datafile uses an active material mass of 1.3 mg. Continue using this value?")
- Put the number of the cycle at the beginning of the filename to make it easier to sort.
- Generate an EZStat-style ``.csv`` file.

----
DONE
----

- Reference by spreadsheet column name, not column number (e.g. 'A', not 0, and 'Q', not 16).
- Add a prompt so that it can be run successfully without arguments.
- Output directory containing files for individual cycles.
- Add an optional "mass?" prompt.
- Infer ``.csv`` data columns based on headers.
- Generate a dedicated Grace output file.

.. _Neware: http://www.newarebattery.com/index.php/service-and-software/software-and-download
.. _Python 2.7: https://www.python.org/downloads/
