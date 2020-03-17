{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Tutorial 1: Object detection, setting a scale, image masking\n",
    "\n",
    "This example demonstrates core *phenopype* functionality by showing how multiple objects can be found and extracted from images by applying different **thresholding algorithms**. Furthermore it is shown how a scale is set, i.e. information from **size reference cards** is digitized, and how parts of images are masked to **exclude unwanted objects** from the object detection procedure.\n",
    "\n",
    "The images used for this tutorial contain isopods sitting inside a white tray underneath a camera stand, photopgraphed with a 50 mm lens on a Canon 750D. \n",
    "***\n",
    "* [Add images to project](#add)\n",
    "* [Setting a scale](#scale)\n",
    "* [Detecting objects](#objectfinder)\n",
    "* [Masking images](#mask)\n",
    "* [Detecting many objects](#object2)\n",
    "* [Detecting many objects in many files](#object3)\n",
    "* [Detecting objects on variable background](#object4)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import phenopype as pp\n",
    "\n",
    "## for this tutorial, you should be in the \"tutorial directory of phenopype-master\"\n",
    "#os.getcwd()\n",
    "#os.chdir(\"tutorials\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Add images to project<a name=\"add\"></a>\n",
    "\n",
    "In python, we can use `import as` to load packages and call them with shorter bindings. E.g. we can type `pp` instead of `phenopype` everytime we call a function. Next we specificy the folder containing the images, making a project object that contains all the image names and paths. The function `project_maker` will then collect all files that match your specifications (filetypes or names). \n",
    "\n",
    "For this first simple example, we only want to include the image named \"bug1.jpg\". We can do so using `include` (or, `exclude` to skip images whose filenames contain this string). Note that this can be any sub-string and does not have to be the whole filename, so in this case \"bug1\" will suffice."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "\n",
      "----------------------------------------------------------------\n",
      "Project settings\n",
      "================\n",
      "\n",
      "Project name: Demo project\n",
      "Image directory: images\n",
      "Search mode: dir\n",
      "Filetypes: []\n",
      "Include:['bug1']\n",
      "Exclude: []\n",
      "----------------------------------------------------------------\n",
      "Search returned following files: \n",
      "['bug1.jpg']\n"
     ]
    }
   ],
   "source": [
    "my_proj = pp.project_maker(image_dir = \"images\", include=[\"bug1\"], name =\"Demo project\") \n",
    " \n",
    "# HINT: image_dir can be relative or absolute \n",
    "# e.g. something like \"your_download_directory//phenopype-master//tutorials//images\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Let's have a quick look at the image using the collected absolute filepaths (accessible from the `my_proj` object) and the _phenopye_ function `show_img` (contains all the `opencv` GUI controls explained in ---. Close the image by hitting enter or closing the window:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "img_path = my_proj.filepaths[0] \n",
    "pp.show_img(img_path)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setting a scale <a name=\"scale\"></a>\n",
    "\n",
    "Our image contains an organism, as well as a reference card for colour and size. To make our measurements meaningful, we need to know the the pixel-to-mm-ratio. To do so we we load the image into the `scale_maker`, `zoom` into the scale area for better visibility, and mark the distance we specifiy - in this case 10 mm. \n",
    "\n",
    "**HINT:** The default mode for marking the scale is by dragging a box/rectangle around the object. However, you can also specify points to draw a polygon. \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Mark the outline of the scale by left clicking, remove points by right clicking, finish with enter.\n",
      "Finished, scale outline drawn. Now add the scale by clicking on two points with a known distance between them:\n",
      "Adding point 1 of 2 to scale\n",
      "Adding point 2 of 2 to scale\n",
      "\n",
      "\n",
      "------------------------------------------------\n",
      "Finished - your scale has 956 pixel per 10 mm.\n",
      "------------------------------------------------\n",
      "\n",
      "\n"
     ]
    }
   ],
   "source": [
    "scale = pp.scale_maker(image=img_path, value=10, unit=\"mm\", zoom=True, show=True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can access the scale by calling its variable `measured`, which always will give you the ratio of **pixels per 1 mm**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "95.3"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "scale.measured"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Detecting objects <a name=\"objectfinder\"></a>\n",
    "\n",
    "Finding objects inside an image is a core function of *phenopype*. Results depend on how \"good\" your pictures are with respect to foreground contrast of your objects, homogeneity of your background, and overall illumination and resolution. The pictures we have loaded above are pretty good for that purpose. However, don't give up just now if your images have less ideal contrast or a noisy background. *phenopype* comes with a flavor of different preprossing strategies and well established [thresholding algorithms in opencv](https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html), wrapped into a simple method: the `object_finder`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Help on class object_finder in module phenopype.base:\n",
      "\n",
      "class object_finder(builtins.object)\n",
      " |  object_finder(image)\n",
      " |  \n",
      " |  Initialize object finder class, loads image.\n",
      " |  \n",
      " |  Parameters\n",
      " |  ----------\n",
      " |  \n",
      " |  image: str or array\n",
      " |      absolute or relative path to OR numpy array of image containing the objects\n",
      " |  \n",
      " |  Methods defined here:\n",
      " |  \n",
      " |  __init__(self, image)\n",
      " |      Initialize self.  See help(type(self)) for accurate signature.\n",
      " |  \n",
      " |  find_objects(self, **kwargs)\n",
      " |      Method in object finder class: find objects in colour or grayscale images using thresholding\n",
      " |      \n",
      " |      Parameters\n",
      " |      ----------\n",
      " |      thresholding: list (default: [\"otsu\"])\n",
      " |          determines the type of thresholding: \n",
      " |              - \"binary\" needs an interger for the threshold value (default: 127), \n",
      " |              - \"adaptive\" needs odd integer for blocksize (default: 99) and constant to be subtracted (default 1) \n",
      " |              - for more info see https://docs.opencv.org/3.4.4/d7/d4d/tutorial_py_thresholding.html\n",
      " |      operations: list (default: [\"diameter\", \"area\"])\n",
      " |          determines the type of operations to be performed on the detected objects:\n",
      " |              - \"diameter\" of the bounding circle of our object\n",
      " |              - \"area\" within the contour of our object\n",
      " |              - \"grayscale\" mean and standard deviation of grayscale pixel values inside the object contours\n",
      " |              - \"bgr\" mean and standard deviation of blue, green and red pixel values inside the object contours\n",
      " |              - \"skeletonize\" attempts to transform object into a skeleton form using the technique of Zhang-Suen. WARNING: can be slow for large objects\n",
      " |      scale: num (1)\n",
      " |          pixel to mm-ratio \n",
      " |      mode: str (default: \"multiple\")\n",
      " |          detect all, or only [\"single\"] largest object or multiple \n",
      " |      mask: list\n",
      " |          phenoype mask-objects (lists of boolean mask, label, and include-argument) to include or exclude an area from the procedure\n",
      " |      show: bool (default: True)\n",
      " |          display the detection results\n",
      " |      blur1: int\n",
      " |          first pass blurring kernel size (before thresholding)\n",
      " |      blur2: list\n",
      " |          second pass blurring kernel size (after thresholding) and binary thresholding value (default 127)   \n",
      " |      min_diam: int\n",
      " |          minimum diameter (longest distance in contour) in pixels for objects to be included (default: 0)\n",
      " |      min_area: int\n",
      " |          minimum contour area in pixels for objects to be included (default: 0)\n",
      " |      corr_factor: int\n",
      " |          factor (in px) to add to (positive int) or subtract from (negative int) object (default: 0)\n",
      " |      resize: in (0.1-1)\n",
      " |          resize image to speed up detection process - usually not recommended\n",
      " |      gray_value_ref: int (0-255)\n",
      " |          reference gray scale value to adjust the given picture's histogram to\n",
      " |  \n",
      " |  ----------------------------------------------------------------------\n",
      " |  Data descriptors defined here:\n",
      " |  \n",
      " |  __dict__\n",
      " |      dictionary for instance variables (if defined)\n",
      " |  \n",
      " |  __weakref__\n",
      " |      list of weak references to the object (if defined)\n",
      "\n"
     ]
    }
   ],
   "source": [
    "help(pp.object_finder)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Just like `project_maker` or `scale_maker`, `object_finder` is a [class](https://docs.python.org/3.7/tutorial/classes.html), that means we have to initialize it first, and then run the actual method. After initializing it by giving it a path to our image (alternatively: an array), we can detect objects using `find_objects`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Warning - no scale specified\n",
      "     diameter  area\n",
      "idx                \n",
      "1           7    24\n",
      "2          19    67\n",
      "3          15     8\n",
      "4          17    16\n",
      "5          13    16\n",
      "..        ...   ...\n",
      "169        48   371\n",
      "170        24    46\n",
      "171        74   111\n",
      "172        12    19\n",
      "173         9    13\n",
      "\n",
      "[173 rows x 2 columns]\n",
      "\n",
      "\n",
      "----------------------------------------------------------------\n",
      "Found 1259 objects in bug1.jpg:\n",
      "  ==> 173 are valid objects\n",
      "    - 1086 are noise\n",
      "----------------------------------------------------------------\n"
     ]
    }
   ],
   "source": [
    "of = pp.object_finder(image=img_path)\n",
    "results = of.find_objects()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Masking images <a name=\"mask\"></a>\n",
    "\n",
    "Ok, this is not right, the algorithm is picking up our reference card. We need to only include our organism in our image by applying a mask to be included. This we can do with the class `mask_maker` that we need to initialize with a picture, and then apply the `draw_mask()` function. This method works cumulatively, meaning that we can include or exclude multiple areas **after** the first mask is drawn. \n",
    "\n",
    "**HINT:** We can use `\"rectangle\"` or `\"polygon\"` mode to draw our mask."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Mark the outline of your arena, i.e. what you want to include in the image analysis by left clicking, finish with enter.\n",
      "\n",
      "Mark the outline of your arena, i.e. what you want to include in the image analysis by left clicking, finish with enter.\n",
      "Adding point #1 with position(2127,866) to arena\n",
      "Adding point #2 with position(1821,2193) to arena\n",
      "Adding point #3 with position(1400,1253) to arena\n",
      "\n",
      "Mark the outline of your arena, i.e. what you want to include in the image analysis by left clicking, finish with enter.\n"
     ]
    }
   ],
   "source": [
    "mm = pp.mask_maker(img_path)\n",
    "mask1 = mm.draw_mask(label=\"1\", mode=\"rectangle\", show=True)\n",
    "mask2 = mm.draw_mask(label=\"2\", mode=\"polygon\", show=True, include=True)\n",
    "mask3 = mm.draw_mask(label=\"3\", mode=\"rectangle\", show=True, include=False)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The masks can the be passed on the the `object_finder`:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2, mask3]) # NOTE: your mask should be inside a list -> []"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The next problem is, that our organism is being recognized as many small objects. If we only have one organism in our image, we can switch to the `mode` \"single\". Also, we want to disregard legs and antenna. The removal of small structures can be accomplished by adding some gaussian noise to the image with the `blur1` variable (`blur1` = first pass blurring, `blur2` = second pass blurring). The provided number of the size of your blur kernel in pixels (bigger = more blurred). At this point we should also include the scale we measured earlier:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2, mask3], mode=\"single\", blur1=25, scale=scale.measured) "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "What we see in the console is just for evalution and does not show us much information. To see at what we actually measured, let's look at the `results` object, which contains some metadata, and the phenotypic information."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "\n",
    "\n",
    "Variable|Description\n",
    "-|-\n",
    "filename | name of the image file\n",
    "date_taken | timestamp of when your image was taken. (y-m-d h-m-s), or NA\n",
    "date_analyzed | timestamp of when your image was analyzed (i.e., current time). (y-m-d h-m-s)\n",
    "idx | if you have multiple objects in your image, this will correspond to the labels\n",
    "resize_factor | sometimes it is necessary to resize large images. this keeps track of it \n",
    "scale | the provided scale, number of pixels per 1 mm\n",
    "diameter | from the bounding circle of our object\n",
    "area | inside the contour of our object\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can measure aditional parameters that we pass on using the `operations` argument - e.g. \"bgr\", which returns the mean values for blue, green, and red pixels (for a full list of operations, see `help(pp.object_finder)`)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2, mask3], mode=\"single\", blur1=25, scale=scale.measured, operations = [\"grayscale\", \"bgr\"])\n",
    "results"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can keep running the `find_objects` method until we are happy with our results. Once that is the case, we save both the results data frame using `save_csv`; and the processed image, which we get by accessing `image_processed` in the `object_finder` object, and saving it with `save_img`. As name we use the filename that we get from the `my_proj` object.\n",
    "\n",
    "Note that by default, text files and images are overwritten if they already exists in the specified directory. Also, if a directory does not exists, it will be created."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "img_name = my_proj.filenames[0]\n",
    "\n",
    "pp.save_csv(df=results, name=img_name, save_dir=\"images_out\")\n",
    "pp.save_img(image=of.image_processed, name=img_name, save_dir=\"images_out\", resize=0.25)\n",
    "# NOTE: you can resize images with the \"resize\" argument to save space"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "You now should be able to handle the `object_finder` class. Below I will introduce more examples and processing steps that can improve results."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Detecting many objects <a name=\"object2\"></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "For this example we will load a different set of images."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "my_proj = pp.project_maker(image_dir = \"images\", include=[\"isopods\"]) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "img_path = my_proj.filepaths[0] # we only use the first image\n",
    "scale = pp.scale_maker(image=img_path, value=10, unit=\"mm\",  zoom=True, show=True) # measure scale"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "of = pp.object_finder(img_path)\n",
    "results = of.find_objects(scale=scale.measured) "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Looks terrible. We need to exclude areas, and pass the mask on to `find_objects`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "mask = pp.mask_maker(img_path)\n",
    "mask1 = mask.draw_mask(label=\"tray\", mode=\"rectangle\", include=True) # include the tray area\n",
    "mask2 = mask.draw_mask(label=\"scale\", mode=\"rectangle\", show=True, include=False) # exclude the scale inside the tray area"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2], scale=scale.measured)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Still not great, there is a lot of noise and some bugs are not identified properly. We can try some blurring and implementing a minimum diameter."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2], scale=scale.measured, min_diam=10, blur1=10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Blurring tends to \"eat away\" the object borders. We can counteract this by adding a \"correction factor\" that will add some more area to our objects. `corr_factor` is a list that takes three arguments: [shape, value, iterations]. See `help(object_finder)` for details. \n",
    "\n",
    "Since we add more \"flesh to the bone\", we can also increase the minimum diameter of our objects and also introduce `min_area` to get rid of those small particles. Note that the preview that gets put out after every `find_object` run can help you specify those parameters. E.g. if most objects have around 100 pixels and an area >1000 pixels, we want to set the threshold so that the majority stays in, but the smallest objects get excluded."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mask=[mask1, mask2], scale=scale.measured, min_diam=20,min_area=1100, blur1=10, corr_factor=[\"ellipse\",10,1])\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Ok, this looks good, let's save the results and the processed image for reference, the `idx` column corresponds to the labels inside the image. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "img_name = my_proj.filenames[0]\n",
    "\n",
    "pp.save_csv(df=results, name=img_name, save_dir=\"images_out\")\n",
    "pp.save_img(image=of.image_processed, name=img_name, save_dir=\"images_out\", resize=0.5)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Detecting many objects in many files <a name=\"object3\"></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Let's do this for all the files in our project. Because the tray on which the bugs sit isn't perfectly centered in each picture, we should mark the boundaries with the `polygon_maker`. However, because the scale is the same in each picture, we can use the `detect` method from the `scale_maker` class. `detect` uses the accelerated KAZE (AKAZE: \n",
    "https://www.youtube.com/watch?v=lI50PGr2TEU) algorithm for feature registration and matching. I will expand more on this in a future version of the tutorial."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# MAKE FILE LIST\n",
    "\n",
    "my_proj = pp.project_maker(image_dir = \"images\", include=[\"isopods\"]) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# MARK SCALE ONCE, GET PIXEL RATIO\n",
    "\n",
    "img_path = my_proj.filepaths[0] # we only use the first image\n",
    "scale = pp.scale_maker(image=img_path, value=10, unit=\"mm\",  zoom=True, show=True) # measure scale"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# MARK TRAY AREA ONLY, SCALE WILL BE AUTOMATICALLY DETECTED. CONTINUE WITH ENTER\n",
    "\n",
    "# loop through both the projects filepaths and filenames using \"zip\":\n",
    "for path, name in zip(my_proj.filepaths, my_proj.filenames):\n",
    "           \n",
    "    # mark the tray for each image. if your picture doesn't change dramatically, you can skip this\n",
    "    arena = pp.mask_maker(path)\n",
    "    mask1 = arena.draw_mask(label=\"tray\", mode=\"rectangle\", show=True)\n",
    "    \n",
    "    # this is a scale detector! if your scale is identical, the scale-finder will find it!\n",
    "    mask2, scale.current = scale.detect(path, min_matches=10, show=True)    \n",
    "\n",
    "    # we use the optimal settings we found above\n",
    "    of = pp.object_finder(path)\n",
    "    results = of.find_objects(mask=[mask1, mask2], scale=scale.measured, min_diam=20,min_area=1100, blur1=10, corr_factor=[\"ellipse\",10,1])\n",
    "        \n",
    "    # save after every iteration\n",
    "    pp.save_csv(results, name, \"tutorials\\\\images_out\")\n",
    "    pp.save_img(of.image_processed, name, \"tutorials\\\\images_out\", resize=0.5)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Detect objects on variable background <a name=\"object4\"></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "In this example, the background is not homogenous enough for the standard thresholding algorithm, so we need to use different settings."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "my_proj = pp.project_maker(\"images\", include=[\"bug2\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "of = pp.object_finder(image=my_proj.filepaths[0])\n",
    "results = of.find_objects(mode=\"single\", blur1=10) # does not work"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The algorithm fails because the image is full gradients that are invisible to us - we can make them visible if we change the algorithm, and binarize the image.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = of.find_objects(mode=\"single\", method=[\"adaptive\", 99,1], show=False) \n",
    "pp.show_img(of.thresh)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# and now with proper output\n",
    "results = of.find_objects(mode=\"single\", blur1=10, method=[\"adaptive\", 99,3]) # does work a lot better"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "pp.save_csv(results, my_proj.filenames[0], \"images_out\")\n",
    "pp.save_img(of.image_processed, my_proj.filenames[0], \"images_out\", resize=0.5)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
