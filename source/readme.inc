|image1|

+-----------+-----------+-----------+-----------+-----------+-----------+
| Project   | Windows   | Linux     | OSX build | Coverage  | Style     |
| status    | build     | build     |           |           |           |
+===========+===========+===========+===========+===========+===========+
| |Project  | |Build    | |Build    | *none*    | |Coverage | |Code     |
| Status:   | status|   | Status|   |           | Status|   | style|    |
| Active|   |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

| **Author:** `Moritz Lürig <https://luerig.net>`__
| **License:** `LGPL <https://opensource.org/licenses/LGPL-3.0>`__

--------------

What is phenopype?
^^^^^^^^^^^^^^^^^^

phenopype is a high throughput phenotyping pipeline for Python to
support ecologists and evolutionary biologists in extracting high
dimensional phenotypic data from digital images. phenopype integrates
state-of-the-art computer vision functions (using
`opencv-python <https://github.com/opencv/opencv-python>`__ as the main
backbone), the possibility for GUI-based interactions and a project
management ecosystem to facilitate rapid data collection and
reproducibility.

Why phenopype
^^^^^^^^^^^^^

phenopype is aiming to augment, rather than replace the utility of
existing CV libraries for scientists measuring phenotypes. Put
differently, phenopype does not intend to be an exhaustive library of
granular image processing functions, like OpenCV, scikit-image or
ImageJ, but instead, it is a set of wrappers and convenient management
tools to allow biologists to *get their data fast* without having to
fiddle with too much code.

Main features
^^^^^^^^^^^^^

(For a complete list `check the API
reference <https://mluerig.github.io/phenopype/api.html>`__)

-  image analysis workflow:

   -  preprocessing (automatic reference detection, colour and size
      correction, morphology operations)
   -  segmentation (thresholding, watershed, contour-filtering,
      foreground-background subtraction)
   -  measurement (pixel intensities, landmarks, shape features, texture
      features)
   -  visualization and export
   -  video analysis module for object tracking

-  project management tools to organize images and data (automatic
   creation of project directory tree)
-  customizable analysis-templates that allow anyone to reproduce all
   collected data with only a few lines of code (suitable for
   repositories like Dryad or OSF).

|image2|

--------------

Getting started
^^^^^^^^^^^^^^^

1. Read the `Installation
   Instructions <https://mluerig.github.io/phenopype/installation.html>`__
2. Download and run the
   `Tutorials <https://mluerig.github.io/phenopype/tutorial_0.html>`__
3. Have a look at the
   `Examples <https://mluerig.github.io/phenopype/index.html#examples>`__

Important information
^^^^^^^^^^^^^^^^^^^^^

-  phenopype currently **does not work on macOS**, as there are several
   issues with OpenCV’s HighGUI module, as documented
   `here <https://github.com/mluerig/phenopype/issues/9>`__ and
   `here <https://github.com/mluerig/phenopype/issues/5>`__ - any help
   in making phenopype usable for macOS is most welcome !
-  phenopype is currently undergoing `review at
   pyOpenSci <https://github.com/pyOpenSci/software-review/issues/24>`__.
   In the process, phenopype was updated to version 2 which is **not
   compatible with previous versions** - read the instructions for
   `installing past
   versions <https://mluerig.github.io/phenopype/installation.html#installing-past-versions>`__

--------------

Documentation
^^^^^^^^^^^^^

The full Documentation can be found here:
**https://mluerig.github.io/phenopype/**

Contributions and feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^

Phenopype development is an ongoing process and contributions towards
making it a more broadly applicable and user-friendly tool are most
welcome. This can be in the form of feature requests (e.g. more
functions from the `OpenCV
library <https://docs.opencv.org/master/modules.html>`__) or by
reporting bugs via the `issue
tracker <https://github.com/mluerig/phenopype/issues>`__. You can also
`get in touch with me <https://luerig.net>`__ directly if you have any
suggestions for improvement.

How to cite phenopype
^^^^^^^^^^^^^^^^^^^^^

phenopype: a phenotyping pipeline for python (v2.0.0). 2021 Lürig, M.
https://github.com/mluerig/phenopype

::

   @misc{phenopype,
     title={{phenopype: a phenotyping pipeline for Python}},
     author={L{\"u}rig, Moritz},
     year={2021},
     url={https://github.com/mluerig/phenopype},
   }

.. |image1| image:: https://github.com/mluerig/phenopype/raw/master/source/phenopype_logo.png
.. |Project Status: Active| image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/4o27rpjbe8ij2kj3?svg=true
   :target: https://ci.appveyor.com/project/mluerig/phenopype
.. |Build Status| image:: https://travis-ci.org/mluerig/phenopype.svg?branch=master
   :target: https://travis-ci.org/mluerig/phenopype
.. |Coverage Status| image:: https://coveralls.io/repos/github/mluerig/phenopype/badge.svg?branch=master
   :target: https://coveralls.io/github/mluerig/phenopype?branch=master
.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |image2| image:: https://github.com/mluerig/phenopype/raw/master/source/phenopype_demo.gif
