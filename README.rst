"""""""""""""""""""""
ACEP Fuel Meter Tools
"""""""""""""""""""""

This is a collection of the data management and analysis tools developed to support
the ACEP Fuel Meter project.

=========
Licensing
=========

The repository, content within, and contributions are licensed under the **MIT license**.

============
Contributors
============

Contributors to this project are:

* Bax Bond
* Dayne Broderson
* Doug Keller
* Tawna Morgan

==========================
Elektron Server Quickstart
==========================

------------------------
Creating Monthly Reports
------------------------

On the ``elektron`` server, the ``fuelmeter-tools`` git repository and stove data (in the ``ftp-data`` directory) are in the ``data/puma`` directory.

.. code-block::

    data/
        puma/
            ftp-data/
            fuelmeter-tools/
            
SSH
===

``ssh`` into the server as ``data`` (this is dependent on your setup).

.. code-block::

    your-comp:~$ ssh elektron
    
or however you ``ssh`` into the elektron server as the ``data`` user.

Update ``ftp-data``
===================

Update the ``ftp-data`` directory by switching into it and running:

.. code-block::

    data:~/puma/ftp-data$ ./mirror.sh
    
Run Docker Container
====================

Switch to the ``fuelmeter-tools`` directory. Run the ``uafacep/fuelmeter-tools-docker`` docker image with:

.. code-block::

    data:~/puma/fuelmeter-tools$ docker run -i -t -v $(pwd)/../../..:/home uafacep/fuelmeter-tools-docker bash
    
Now you will be in the actively running docker container.

Running ``fuelmeter-tools`` Commands
====================================

To update the unified netcdf file, switch to the ``fuelmeter-tools`` directory, and then run:

.. code-block::

    [root@####### fuelmeter-tools]# make unified_netcdf

Once this command is done, the ``puma_unified_data.nc`` file will have been made. This file is needed for the subsequent commands.

To create the monthly reports, run:

.. code-block::

    [root@####### fuelmeter-tools]# make monthly_reports
    
This will build the monthly reports and put them in the ``fuelmeter-tools/output`` directory, in a directory and zip file.
