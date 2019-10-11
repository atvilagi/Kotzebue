=====================
ACEP Fuel Meter Tools
=====================

This is a collection of the data management and analysis tools developed to support
the ACEP Fuel Meter project.

---------
Licensing
---------

The repository, content within, and contributions are licensed under **MIT license**.

------------
Contributors
------------

Contributors to this project are:

* Bax Bond
* Dayne Broderson
* Doug Keller

---------------
Getting Started
---------------

Get the Data
============

The fuel meter data is stored in the ``ftp-data`` directory. This directory is located on the ``elektron`` server, in the ``puma`` directory.

To get the data will you have to get a copy from the server. Ask the contributors of this repository to figure this out.

Once you have the data, place the ``ftp-data`` alongside this repository.

.. code-block:: Bash

	puma-overarching-directory/
		|-- ftp-data/
		|-- fuelmeter-tools/

Getting Setup
=============

To use this repo, clone it via ``git`` command line or through **Github Desktop**. The instructions to install ``git`` or **Github Desktop** are `here <docs/git/install_git.rst>`_.

Then, if you don't have it, install **Docker**, following the instructions in `Installing Docker <docs/docker/install_docker.rst>`_.

``pull`` or ``build`` the ``acep/fuelmeter-tools-docker`` container with:

.. code-block:: Bash

	~$ docker pull acep/fuelmeter-tools-docker

More detailed instructions are `here <docs/docker/run_docker.rst>`_.

Then run the ``acep/fuelmeter-tools-docker`` container and change to the fuelmeter-tools directory:

.. code-block:: Bash

	~$ docker run -i -t -v $(pwd)/..:/home acep/fuelmeter-tools-docker bash

	~# cd fuelmeter-tools

Now you're in the container, in the ``fuelmeter-tools`` repo directory. Now you can run the ``fuelmeter-tools`` specifc commands to manipulate data and build reports.

Running ``fuelmeter-tools`` Commands
====================================

From the ``fuelmeter-tools`` directory, you can run a few ``make`` commands to play with data/reports while in the ``acep/fuelmeter-tools-docker`` container.

.. code-block:: Bash

	fuelmeter-tools$ make unified_netcdf

Runs the scripts to build the ``puma_unified_data.nc`` file, which is needed to perform downstream commands, such as making reports.

.. code-blocks:: Bash

	fuelmeter-tools$ make monthly_reports

Runs the scripts to build the monthly reports for the stoves in the ``data/yaml/puma-monthly-report-inventory.yml`` file.
