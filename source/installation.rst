Installation instructions
=========================

.. important::

	These instructions are intended for Python beginners and assume that :code:`Anaconda` is being used to manage Python and :code:`pip` for the phenopype installation. There are, of course, other ways to install Python, and phenopype can be directly installed via :code:`pip install phenopype`. However, if you don't know what this means or are in doubt about what to do, you should just stick to the following instructions.

1. Installing Python
--------------------

Download and install `Anaconda3 <https://www.anaconda.com/distribution/>`_ (Python 3). Anaconda is a scientific python distribution which comes with the most common scientific Python packages already built in. Follow the OS-specific instructions below:

1.1 For Windows
~~~~~~~~~~~~~~~

Open the Anaconda installer file you downloaded. Depending on the installation location of your choice you may need admin rights (right click on the file and select `Run as Administrator`), but DON'T install Anaconda to `Program files`, as this may cause problems later. A good idea is typically the root directory of your hard drive (e.g. `C:\\Anaconda3`). Then test if the installation was successful by opening a terminal and typing:

.. code-block:: bash

	conda --version

If :code:`conda` is not recognized you need add the path to your Anaconda installation directory to your environmental variables (if you have not done so during the installation). To do so, go to `Control Panel\\System` and `Security\\System\\Advanced System Settings` and look for `Environment Variables`. Then click `new` and add the path to the Anaconda folder (i.e., the path you selected during installation - e.g. `C:\\Anaconda3`) and the subfolder `scripts` (e.g. `C:\\Anaconda3\\Scripts`.

An alternative to manipulating the environment variables is to use the anaconda prompt that can be launched from a shortcut in the `Start` menu (should get added during the installation), or through the `Anaconda Navigator <https://docs.anaconda.com/anaconda/user-guide/getting-started/>`_).


1.2 For Linux
~~~~~~~~~~~~~~~

Run the Anaconda installer script you downloaded, e.g. :code:`bash ~/Downloads/Anaconda3-2020.02-Linux-x86_64.sh`, and follow the instructions. When the installer prompts “Do you wish the installer to initialize Anaconda3 by running conda init?”, type `yes`. Then test if the installation was successful by opening a terminal and typing:

.. code-block:: bash

	conda --version

If :code:`conda` is not recognized you need to add the path to your Anaconda installation directory to your `.bashrc` file. To do so, type :code:`echo 'export PATH=/path/to/anaconda3/bin:$PATH' >> ~/.bashrc`.


1.3. Troubleshooting references
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- https://docs.anaconda.com/anaconda/install/
- https://docs.anaconda.com/anaconda/user-guide/troubleshooting/
- https://stackoverflow.com/questions/28612500/why-anaconda-does-not-recognize-conda-command
- https://stackoverflow.com/questions/44597662/conda-command-is-not-recognized-on-windows-10
- https://askubuntu.com/questions/908827/variable-path-issue-conda-command-not-found


2. Installing phenopype
-----------------------

(These instructions are valid across operating systems).


2.2 Initial installation
~~~~~~~~~~~~~~~~~~~~~~~~

Open a terminal. Then create a virtual environment with `conda`. Using such environments will give you full control over which Python packages are installed, and reduces the change of package related issues. Note that phenopype requires Python v3.7, which needs to be explicitly specified. For example, for an environment named "pp", type:


.. code-block:: bash

	conda create -n "pp" python=3.7


You can now activate your environment. **This needs to be done every time you are using phenopype**:

.. code-block:: bash

	conda activate pp


Now install phenopype to the environment using :code:`pip` (`pip` is the package installer for Python):

.. code-block:: bash

	pip install phenopype


.. tip::

	If you prefer an "Rstudio-like" environment, you can use Phenopype from a Python Integrated Development Environment (IDE), such as `Spyder <https://www.spyder-ide.org/>`_. `Spyder` needs to be installed with `conda` directly to the environment you created before. Using the example from above:


	.. code-block:: bash

		conda activate pp
		conda install spyder


	Once installed, you can run `Spyder` by typing :code:`spyder`


That's it - happy `phenopyping`! You can now use phenopype by after loading :code:`python` or :code:`spyder` from the terminal. You can also use phenopype from a `jupyter notebook` - for more details, give the `tutorials <tutorial_0.html>`_ a try. **Always remember to activate your environment.**


2.2 Installing updates
~~~~~~~~~~~~~~~~~~~~~~

For regular major and minor releases, use the :code:`-U` flag with :code:`pip`:

.. code-block:: bash

	pip install phenopype -U

2.3 Installing past versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Major releases are not backwards compatible, so if you have existing phenopype projects that were created with a previous version you need to download that specific version. You can tell `pip` to do so, for example, for version `1.0.0`:

.. code-block:: bash

		pip install "phenopype==1.0.0"

Or, for the latest phenopype version that is still 1.x.x:

.. code-block:: bash

		pip install "phenopype < 2"


3. Choosing a text editor
-------------------------

Phenopype's high throughout workflow currently requires a text editor to be installed that **does not lock the file** (`read about file locking here <https://superuser.com/a/855057/970488>`_).

.. warning::

	Your OS needs to know how to handle `.yaml` files. Make sure that the default app to open these files is set. Otherwise, phenopype will be unable to open YAML configuration files (this is a common error source).


For Windows, `Notepad` works. However, I highly recommend `Notepad++`, which supports syntax highlighting and has many other useful features: https://notepad-plus-plus.org/downloads/.

Another popular editor is `Atom <https://atom.io/>`_. `Atom` works across all platforms: https://flight-manual.atom.io/getting-started/sections/installing-atom/

Regardless which editor you chose, you need to make sure that your OS "knows" how to open ".yaml" files. Check the following: create a file named `test.yaml`. When you try to open it but nothing happens, you need to select a text editor as the default application for the `.yaml` file ending.
