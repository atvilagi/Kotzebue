"""""""""""""""""
Installing Docker
"""""""""""""""""

==========================
Installing Docker on Linux
==========================

To install Docker on Linux, use your distro's package manager and download the 'docker' package.

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

For help or more information, go to the 'Docker install help page https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1'_.
