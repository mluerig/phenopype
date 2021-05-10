How to run tutorials and examples using Jupyter Notebook
========================================================

The tutorials are written as `jupyter notebooks` - browser based Python kernels to run, document, and visualize code (`https://jupyter.org/ <https://jupyter.org/>`_). Below is a step by step guide to get started with the tutorials and examples. If you installed Python using Anaconda, it is possible that `jupyter` is already installed (:code:`jupyter --version` in the terminal should return a version number) - in this case you can skip step 3.

#. Install phenopype: follow the `installation instructions <installation.html>`_.
#. Download and unpack the `phenopype repository from github <https://github.com/mluerig/phenopype/archive/master.zip>`_
#. Install jupyter notebook to your environment*: :code:`pip install jupyter notebook`
#. Open a terminal and go to the tutorial folder in the unpacked phenopype repository (e.g. `../downloads/phenopype-master/tutorials`)
#. Start the notebooks with :code:`jupyter notebook` and click on one of the tutorial files.
#. Run the code cell by cell


.. warning::

	\* Make sure you install `jupyter` to your specific environment (i.e. activate first using :code:`conda activate "my-env"`. If `jupyter` is not installed, running :code:`jupyter notebook` will fall back on the conda base environment where phenopype may not be installed (this is a common error source).


Tutorials
---------

.. toctree::
	:maxdepth: 1

	tutorial_1_python_intro
	tutorial_2_phenopype_images
	tutorial_3_phenopype_workflows
	tutorial_4_managing_projects
	tutorial_5_references
	tutorial_6_video_analysis


.. tip::
	If you want to use the tutorials or examples as a blueprint for your own project, simply save them as a Python script by clicking File > Download as > Python (.py).


Examples
--------

.. toctree::
	:maxdepth: 1

	example_1_detect_objects_isopods
	example_2_landmarks_stickleback
	example_3_phytoplankton
	example_4_video_analysis_stickleback
	example_5_shape_stickleback
	example_6_counting_snails
	example_7_worm_length
	example_8_cichlid_teeth
