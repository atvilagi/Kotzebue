"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Building/Pushing/Pulling the ``acep/fuelmeter-tools-docker`` Container
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

PAGE STILL UNDER CONSTRUCTION
=============================

---------------------
Pulling the Container
---------------------

The easiest way to get the ``fuelmeter-tools-docker`` image is ``pull`` it from ``Docker Hub``. You need to create a ``Docker account``_.

.. _Docker account: https://hub.docker.com/signup/

Once you create an account, run:

.. code-block: Bash

	~$ docker login

to login. Then ``pull`` the ``acep/fuelmeter-tools-docker`` image with:

.. code-block:: Bash

	~$ docker pull acep/fuelmeter-tools-docker

----------------------
Building the Container
----------------------

You can build a ``docker container`` with the ``Dockerfile`` and other contents of the ``fuelmeter-tools/docker`` directory.

Move to the ``docker`` directory and run:

.. code-block:: Bash

	fuelmeter-tools/docker$ docker build -t acep/fuelmeter-tools-docker .


-------------------------------------------
Pushing the Container to the ``Docker Hub``
-------------------------------------------

If you make any changes to the ``fuelmeter-tools-docker`` container or its ``Dockerfile``, you can push the new image to the ``Docker Hub``.

Build the new image, like above, and then run:

.. code-block:: Bash

	~$ docker push acep/fuelmeter-tools-docker

The image is decently large, so it will take some time to complete the push.
