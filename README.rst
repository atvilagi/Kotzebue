=====================
ACEP Fuel Meter Tools
=====================

This is a collection of the data management and analysis tools developed to support
the ACEP fuelmeter project.

Licensing
=========

The repository, content within, and contributions are licensed under MIT license.

Data Packaging Output Files
===========================

Some scripts in the ``python/scripts`` folder package all the data as a time series and an event series.

Unified netCDF File
-------------------

To make a unified netCDF file containing the raw date, time series, and event series, run the following command in the base directory of the repository:

.. code-block:: bash

	fuelmeter-tools$ make unified_netcdf

The unified netCDF file is critical to have as all downstream data deliverables depend on it, and therefore must be run before other commands are to be run.

Monthly Reports
===============

To make a zip file containing the monthly reports for the PuMA meters, run the ``Makefile`` in the base directory of the repository, so:

.. code-block:: bash

	fuelmeter-tools$ make monthly_reports

This runs the necessary 

Other tools used
================

* jupyter notebooks - data examples 

============
Contributors
============

Contributors to this project are:

* Bax Bond
* Dayne Broderson
* Doug Keller
