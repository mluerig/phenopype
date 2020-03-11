
Projects and pypes
=======================

The pype routine is phenopype’s standard method to analyse medium and large image datasets, where a function stack is constructed with the human readable yaml syntax (serialization language). First, users create a project directory tree, where raw images, attributes and metadata, settings and results will be stored (Fig 2A). Then users should create a pype configuration file and store it within each folder of the phenopype directory tree along with the raw images (Fig. 2B). Phenopype comes with several configuration templates for different cases (e.g. landmarking, colour scoring, or shape measurement), which users can test and modify prior to distributing them among the directories. Finally, users can execute the pype method on a phenopype directory, which will trigger three actions: first it will open the contained yaml configuration with the default OS text editor, then it will parse the contained functions and execute them in the sequence, and open a Python-window showing the processed image. After one parsing iteration, users can evaluate the results and decide to modify the opened configuration file (e.g. either change function parameters or add new functions), and run the pype again, or to terminate the pype and save all results. By providing unique names, users can store different pype configurations and the associated results side by side without having to create new directories (Fig. 2C). The processed image, any extracted phenotypic information, as well as the modified config-file is stored inside the image directory. Together with the raw images, which may be either stored separately or within the directory tree, users can thereby provide the full image analysis pipeline to anyone who wishes to reproduce the obtained results. 


Phenopype project
-----------------
.. autoclass:: phenopype.main.project
   :members:
   :undoc-members:
   :show-inheritance:
   
   
Pype routine
------------
  
.. autoclass:: phenopype.main.pype
   :members:
   :undoc-members:
   :show-inheritance: