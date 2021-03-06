"""""""""""""""""""""""""""""""""""""""""""""""""""""
Running a ``fuelmeter-tools-docker`` Docker Container 
"""""""""""""""""""""""""""""""""""""""""""""""""""""

First, navigate to the ``uafacep/fuelmeter-tools`` directory. Then run the ``acep/fuelmeter-tools-docker`` container with docker:

.. code-block::

	fuelmeter-tools$ docker run -i -t -v $(pwd)/..:/home uafacep/fuelmeter-tools-docker bash

This puts you in a Bash shell in the container with a volume attached to the directory just above your ``fuelmeter-tools`` directory. This is so the container can read and write files on your local (host) machine when you run the commands to manipulate or build data/reports.

From this point on, you're set to run the ``make`` commands described `here <../fuelmeter-tools/make_commands.rst>`_.
