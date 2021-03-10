|image1|

+-----------+-----------+-----------+-----------+-----------+-----------+
| Project   | Windows   | Linux     | OSX build | Coverage  | Style     |
| status    | build     | build     |           |           |           |
+===========+===========+===========+===========+===========+===========+
| |Project  | |Build    | |Build    | *none*    | |Coverage | |Code     |
| Status:   | status|   | Status|   |           | Status|   | style|    |
| Active.|  |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

| **Author:** `Moritz Lürig <https://luerig.net>`__
| **License:** `LGPL <https://opensource.org/licenses/LGPL-3.0>`__

--------------

What is phenopype?
^^^^^^^^^^^^^^^^^^

phenopype is a high throughput phenotyping pipeline for Python to
support ecologists and evolutionary biologists in extracting high
dimensional phenotypic data from digital images. phenopype integrates
computer vision functions (using
`opencv-python <https://github.com/opencv/opencv-python>`__ as the main
backbone) and project management tools to facilitate rapid data
collection and reproducibility.

Why phenopype
^^^^^^^^^^^^^

phenopype is aiming to augment, rather than replace the utility of
existing CV libraries for scientists measuring phenotypes. Put
differently, phenopype does not intend to be an exhaustive library of
granular image processing functions, like OpenCV or scikit-image, but
instead, it is a set of wrappers for these libraries, combined with
project management to allow biologists to *collect data fast*.

Main features
^^^^^^^^^^^^^

| (For a complete list `check the API
  reference <https://mluerig.github.io/phenopype/api.html>`__) - image
  analysis workflow: - preprocessing (automatic reference detection,
  colour and size correction, morphology operations) - segmentation
  (thresholding, watershed, contour-filtering, foreground-background
  subtraction) - measurement (pixel intensities, landmarks, shape
  features, texture features) - visualization and export
| - video analysis module for object tracking - project management tools
  to organize images and data (automatic creation of project directory
  tree) - customizable analysis-templates that allow anyone to reproduce
  all collected data with only a few lines of code (suitable for
  repositories like DRYAD or OSF).

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

**The full Documentation can be found under:
https://mluerig.github.io/phenopype/**

--------------

Contributing and feedback
^^^^^^^^^^^^^^^^^^^^^^^^^

Phenopype development is an ongoing process and contributions towards
making it a more broadly applicable and userfriendly tool are most
welcome. This can be in the form of feature requests (e.g. more
functions from the `OpenCV
library <https://docs.opencv.org/master/modules.html>`__) or by
reporting bugs via the `issue
tracker <https://github.com/mluerig/phenopype/issues>`__. You can also
`get in touch with me <https://luerig.net>`__ directly if you have any
suggestions for improvement.

How to cite phenopype
^^^^^^^^^^^^^^^^^^^^^

phenopype: a phenotyping pipeline for python (v2.0.0) 2021 Lürig, M.
https://github.com/mluerig/phenopype

.. |image1| image:: source/images/phenopype_logo.png
.. |Project Status: Active.| image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/4o27rpjbe8ij2kj3?svg=true
   :target: https://ci.appveyor.com/project/mluerig/phenopype
.. |Build Status| image:: https://travis-ci.org/mluerig/phenopype.svg?branch=master
   :target: https://travis-ci.org/mluerig/phenopype
.. |Coverage Status| image:: https://coveralls.io/repos/github/mluerig/phenopype/badge.svg?branch=master
   :target: https://coveralls.io/github/mluerig/phenopype?branch=master
.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |image2| image:: source/images/phenopype_demo.gif
