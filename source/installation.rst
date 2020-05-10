Installation
=============



1. Install Python
-----------------

To get started, download and install `Anaconda <https://www.anaconda.com/distribution/>`_ 
with Python 3. Anaconda is a scientific python distribution which comes with the most common 
scientific Python packages already built in.

You can test if the installation was successfull by opening a terminal and typing this command:

.. code-block:: bash

	conda --version

If :code:`conda` is not recognized, use the anaconda prompt (e.g. through the `Anaconda Navigator 
<https://docs.anaconda.com/anaconda/user-guide/getting-started/>`_ OR add the path to your Anaconda 
installation directory (e.g. :code:`C:\Anaconda3\Library\bin`) to your environmental variables. Further
help can be found here:

- https://docs.anaconda.com/anaconda/user-guide/troubleshooting/
- https://askubuntu.com/questions/908827/variable-path-issue-conda-command-not-found
- https://stackoverflow.com/questions/44597662/conda-command-is-not-recognized-on-windows-10
- https://towardsdatascience.com/how-to-successfully-install-anaconda-on-a-mac-and-actually-get-it-to-work-53ce18025f97

If you prefer an "Rstudio-like" environment, you can use Phenopype from a Python Integrated Development Environment (IDE). My favorite IDE is Spyder (https://www.spyder-ide.org/), but any other IDE will work too (a slightly outdated overview can be found `here <https://wiki.python.org/moin/IntegratedDevelopmentEnvironments>`_). Phenopype can of course also be run from the command line using :code:`python`.

2. Install phenopype
--------------------

You can install phenopype using :code:`pip`, and run it with :code:`spyder`:

.. code-block:: bash

	pip install phenopype

However, to have fuller control over your python packages and to not mess up existing Python installation, I recommend to create a virtual environment using :code:`conda`:

.. code-block:: bash

	conda create -n "pp" python=3.7
	conda install spyder

.. important::

	Make sure to install Spyder to the new environment you have just created, otherwise `Spyder` will be loaded from conda base environment where Phenopype may not be installed. 


Now activate the virtual environment and install Phenopype using `pip`:

.. code-block:: bash

	conda activate pp
	pip install phenopype

You can now use Phenopype by typing :code:`spyder` or :code:`python` into the command line. If you are unsure to proceed, consult the `tutorials <tutorial_0.html>`_.


2.1 Update Phenopype
""""""""""""""""""""

For regular major and minor releases do:

.. code-block:: bash

	pip install phenopype -U

2.2 Install hotfixes
""""""""""""""""""""

To install bugfixes for a current installation, pull the `fix` branch using :code:`pip` with :code:`git`:

.. code-block:: bash

	pip install git+https://github.com/mluerig/phenopype@fix -U

2.3 Install developmental version
"""""""""""""""""""""""""""""""""

To update to the latest unreleased version of Phenopype, which can be found on `github <https://github.com/mluerig/phenopype/tree/development>`_, pull the `development` branch using :code:`pip` with :code:`git`:

.. code-block:: bash

	pip install git+https://github.com/mluerig/phenopype@development

.. important::

	Any modifications to the python environments or `Spyder`, should only be done using :code:`conda`, but modifications to `phenopype`, 
	its dependencies or other python packages should only be done using :code:`pip`. Mixing the two installers may break your python enviroment.



3. Choose a text editor
-----------------------

The high throughout method in Phenopype currently requires a text editor to be installed that **does not lock the file** - `read about file locking here <https://superuser.com/a/855057/970488>`_. 

For Windows, notepad works. However, I recommend `Notepad++`, which supports syntax highlighting and has many other useful features: https://notepad-plus-plus.org/downloads/

For Linux `Vim` or `Nano` (are already installed on most Linux distributions), and for MacOS, `Nano` or `brackets` could work http://brackets.io/.

Moreover, it is important that your OS knows how to handle `.yaml` files. Make sure that the default app to open these files is set as one of the edtiors that you selected.

[More information about this will follow soon]