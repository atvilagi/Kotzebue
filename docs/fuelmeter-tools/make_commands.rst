Data Packaging Output Files
===========================

Some scripts in the ``python/scripts`` folder package all the data as a time series and an event series.

Unified netCDF File
-------------------

To make a unified netCDF file containing the raw date, time series, and event series, run the following command in the base directory of the repository:

.. code-block:: bash

	fuelmeter-tools$ make unified_netcdf

For this command to work properly, the ``ftp-data`` (with all the puma text files in the structure they were deposited in by the PuMA devices), must be in the same directory as this repository:

.. code-block::

	puma-overarching-directory/
		|-- ftp-data/
		|-- fuelmeter-tools/
			|-- data/
				|-- netcdf/
					|-- puma_unified_data.nc

The unified netCDF file is critical to have as all downstream data deliverables depend on it, and therefore must be run before other commands are to be run (to have updated downstream data). The unified netCDF file (puma_unified_data.nc) is found in the ``data/netcdf/`` directory.

Monthly Reports
===============

To make a zip file containing the monthly reports for the PuMA meters, run the ``Makefile`` in the base directory of the repository, so:

.. code-block:: bash

	fuelmeter-tools$ make monthly_reports

This runs the necessary scripts to produce the reports and places them in the ``output`` directory:

.. code-block::

	fuelmeter-tools/
		|-- output/
			|-- puma_**_****_monthly_reports_**_**_****.zip

Where ``puma_**_****_monthly_reports_**_**_****.zip`` is the created zip file.

Other tools used
================

* jupyter notebooks - data examples 
