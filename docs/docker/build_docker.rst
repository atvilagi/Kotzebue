"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Building/Pushing/Pulling the ``uafacep/fuelmeter-tools-docker`` Container
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

---------------------
Pulling the Container
---------------------

The easiest way to get the ``uafacep/fuelmeter-tools-docker`` image is ``pull`` it from ``Docker Hub``. You need to create a `Docker account`_.

.. _Docker account: https://hub.docker.com/signup/

Once you create an account, run:

.. code-block: 

	~$ docker login

to login. Then ``pull`` the ``uafacep/fuelmeter-tools-docker`` image with:

.. code-block::

	~$ docker pull uafacep/fuelmeter-tools-docker

----------------------
Building the Container
----------------------

You can build a ``docker container`` with the ``Dockerfile`` and other contents of the ``fuelmeter-tools/docker`` directory.

Move to the ``docker`` directory and run:

.. code-block::

	fuelmeter-tools/docker$ docker build -t uafacep/fuelmeter-tools-docker .


-------------------------------------------
Pushing the Container to the ``Docker Hub``
-------------------------------------------

If you make any changes to the ``uafacep/fuelmeter-tools-docker`` container or its ``Dockerfile``, you can push the new image to the ``Docker Hub``.

Build the new image, like above, and then run:

.. code-block::

	~$ docker push uafacep/fuelmeter-tools-docker

The image is decently large, so it will take some time to complete the push.
