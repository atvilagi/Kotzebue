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

.. code-block:: Bash

	~$ sudo pacman -S docker

Test it with:

.. code-block:: Bash

	~$ sudo docker run hello-world

-----------------
Install on Ubuntu
-----------------

For Ubuntu, it's a little more involved:

.. code-block:: Bash

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

.. code-block:: Bash

	~$ sudo docker run hello-world

For help or more information, go to the `Docker Install Guide`_.

.. _Docker Install Guide: https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1

-----------------------------------------
Adding Your Main User to the Docker Group
-----------------------------------------

You can continue to use the docker commands with ``sudo`` but it's generally easier to add your user to ``docker`` group so you don't have to:

.. code-block:: Bash

	~$ gpasswd -a <i>user</i> docker

============================
Installing Docker on Windows
============================

Installing Windows is different than Linux, but only minorly. Go to the `Docker Toolbox`_ website and click on the ``DockerToolbox-#####.exe`` link to download the installer.

.. _Docker Toolbox: https://github.com/docker/toolbox/releases

Once the installer is downloaded, run it and install the `Docker Toolbox`_. Run the ``Docker Quickstart Terminal`` (it will take a few minutes to load on first load-up) and test that it works:

.. code-block:: Bash

	~$ docker run hello-world
