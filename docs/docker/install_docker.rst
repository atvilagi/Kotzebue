"""""""""""""""""
Installing Docker
"""""""""""""""""

==========================
Installing Docker on Linux
==========================

To install Docker on Linux, use your distro's package manager and download the ``docker`` package.

---------------------
Install on Arch Linux
---------------------

For Arch Linux, it's pretty simple:

.. code-block::

	~$ sudo pacman -S docker

Test it with:

.. code-block:: 

	~$ sudo docker run hello-world

-----------------
Install on Ubuntu
-----------------

For Ubuntu, it's a little more involved:

.. code-block:: 

	~$ sudo apt-get update
	
	~$ sudo apt-get install \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg-agent \
		software-properties-common \

	~$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

	~$ sudo add-apt-repository \
		"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
		$(lsb_release -cs) \
		stable"

	~$ sudo apt-get update
	
	~$ sudo apt-get install docker-ce docker-ce-cli containerd.io

Test it with:

.. code-block:: 

	~$ sudo docker run hello-world

For help or more information, go to the `Docker Install Guide for Linux`_.

.. _Docker Install Guide for Linux: https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1

-----------------------------------------
Adding Your Main User to the Docker Group
-----------------------------------------

You can continue to use the docker commands with ``sudo`` but it's generally easier to add your user to the ``docker`` group so you don't have to:

.. code-block:: 

	~$ gpasswd -a <user> docker

where ``<user>`` is the placeholder for your username.

============================
Installing Docker on Windows
============================

Installing Docker on Windows is different than Linux, but probably easier. Go to the `Docker Toolbox`_ website and click on the ``DockerToolbox-#####.exe`` link to download the installer.

.. _Docker Toolbox: https://github.com/docker/toolbox/releases

Once the installer is downloaded, run it and install the `Docker Toolbox`_. Run the ``Docker Quickstart Terminal`` (it will take a few minutes to load on first load-up) and test that it works:

.. code-block:: 

	~$ docker run hello-world

There is a ``Docker Desktop for Windows`` but it requires the Professional or Enterprise version of Windows.
