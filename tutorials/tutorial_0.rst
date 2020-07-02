How to run the tutorials and examples using Jupyter Notebook
============================================================

The tutorials are written as `Jupyter notebooks`, interactive web-apps to run, document, and visualize code: `https://jupyter.org/ <https://jupyter.org/>`_. If you installed Python using Anaconda, it is possible that :code:`jupyter` is already installed - check py typing :code:`jupyter --version` into the console. Otherwise you can install it with pip

.. code-block:: bash

	pip install jupyter notebook

After installing phenopype, `clone the phenopype repository from github <https://github.com/mluerig/phenopype/archive/master.zip>`_. After downloading, unpack the zip file, cd to the tutorial folder, open a terminal and run the notebooks:

.. code-block:: bash

	jupyter notebook

Alternatively, you can copy the code from the jupyter code cells over to Spyder and execute them there. In this case you need to adjust the file paths given in the code cells accordingly. 

.. tip:: 
	If you want to use the tutorials or examples as a blueprint for your own project, simply save them as python a script by clicking File > Download as > Python (.py).


Tutorials
---------

.. toctree::
	:maxdepth: 1

	tutorial_1_python_intro
	tutorial_2_phenopype_workflow
	tutorial_3_managing_projects_1
	tutorial_4_managing_projects_2
	tutorial_5_gui_interactions
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