=====================
ACEP Fuel Meter Tools
=====================

This is a collection of the data management and analysis tools developed to support
the ACEP fuelmeter project.

Licensing
=========

The repository, content within, and contributions are licensed under MIT license.

Monthly Reports
===============

To make a zip file containing the monthly reports for the PuMA meters, run the ``Makefile`` in the base directory of the repository, so:

.. code-block:: bash

	fuelmeter-tools$ make monthly_reports


Data Packaging Output Files
===========================

Some scripts in the ``python/scripts`` folder package all the data as a time series and an event series.

Other tools used
================

* [jupyter notebooks] - data examples 

Contributors
------------

Contributors to this project are:

* Bax Bond
* Dayne Broderson
* Doug Keller
