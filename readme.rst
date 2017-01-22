.. -*- coding: utf-8 -*-

============================================
Neware battery data format conversion script
============================================

This is a script for converting `Neware`_ battery testing data into a more convenient format for plotting.

It requires `Python 2.7`_.

Usage::

    $ python extract-from-general-report.py --input input.txt --mass 1.5

or::

    $ python extract-from-general-report.py
    Enter filename: input.txt
    Enter mass of active material in mg, or just press enter to calculate mAh:1.5

This will produce a folder called ``input_data_extracted`` containing individual text files for each cycle,
as well as a cycle summary file and a `Grace`_ input file.

Note that the input file must be tab-delimited,
so keep this in mind if you export an Excel file and then convert it to a ``.csv`` file.

Currently only works with the "General Report" export type.

.. _Neware: http://www.newarebattery.com/index.php/service-and-software/software-and-download
.. _Python 2.7: https://www.python.org/downloads/
.. _Origin: http://originlab.com/
.. _Grace: http://plasma-gate.weizmann.ac.il/Grace/

-------
License
-------

This project is licensed under the terms of the `MIT license`_.

.. _MIT license: LICENSE.txt
