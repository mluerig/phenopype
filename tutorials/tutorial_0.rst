How to run tutorials and examples using Jupyter Notebook
========================================================

The tutorials are written as a `jupyter notebook`, which is a browser based Python kernel to run, document, and visualize code: `https://jupyter.org/ <https://jupyter.org/>`_. If you installed Python using Anaconda, it is possible that :code:`jupyter` is already installed - check py typing :code:`jupyter --version` into the console. Otherwise you can install it with pip

.. code-block:: bash

	pip install jupyter notebook
	

.. important::

	Make sure `jupyter notebook` is installed in your specific environment (check with `pip freeze`). Otherwise, running `jupyter notebook` it will be loaded from conda base environment where Phenopype may not be installed (this is a common source of error). 


After installing phenopype, `clone the phenopype repository from github <https://github.com/mluerig/phenopype/archive/master.zip>`_. After downloading, unpack the zip file, cd to the tutorial folder, open a terminal and run the notebooks:

.. code-block:: bash

	jupyter notebook

Alternatively, you can copy the code from the jupyter code cells over to Spyder and execute them there. In this case you need to adjust the file paths given in the code cells accordingly. 

.. tip:: 
	If you want to use the tutorials or examples as a blueprint for your own project, simply save them as a Python script by clicking File > Download as > Python (.py).


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