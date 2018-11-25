# -*- coding: utf-8 -*-
"""
Last Update: 2018/10/07
Version 0.4.5
@author: Moritz Lürig
"""

#%% 1) load modules

import os
import cv2
import phenopype as pp



#%% DEV_startup

import os
import cv2
os.chdir("E:\\python1\\phenopype")

import phenopype as pp
import importlib 
importlib.reload(pp)
pp.__file__


#%% 2) start project

# this is where your images are 
ex1 = "E:\\Python1\\phenopype\\examples\\example1\\images"

# initate a project
proj = pp.project()    
proj.project_maker(project_name="example1", image_dir=ex1, save_dir= ex1 + "\\out")

#%% 3) add a scale 
# # this sets the "pixel to mm ratio", that will get written to the output-files for reference. For this, any image that has THE SAME pixel ratio as all following images can be used. If it has the scale, "draw" and measure it, here we use this first image from our image folder (we can access this from our project):

img = proj.filepaths[0]

scale = pp.scale_maker()
scale.draw(image_path=img, length=10, unit="mm", mode="box")

# For this example, the "box" mode is not very useful, as it also covers up a lot of "non-scale" area. We should draw a polygon around the scale. We should also zoom into the scale image so we can work more accurately:
scale = pp.scale_maker()
scale.draw(image_path=img, length=10, unit="mm", mode="polygon", zoom=True)

#%% 4) select "arena"

# to avoid false positives and noise, we should exclude the eges of our image. Again, we select an area by drawing into the image. We will use the same image as before.

arena = pp.polygon_maker()
arena.draw(img, show=True, mode="box")

# similarly the scale-drawer, arena also accepts "polygon"

#%% 5) find and measure objects 

# =============================================================================
# without any finetuning
# =============================================================================
# initialize object finder
of = pp.standard_object_finder()

# [exclude] mask from the scale outline we drew, as well as the red (masked) area from the arena we drew
# [scale] indicates the scale we drew into the image
of.run(im_path=img, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"]) 

# =============================================================================
# with some finetuning
# =============================================================================
# for better results, we need to filter out some of the noise. by specifying minimum size (diameter/area) 
of.run(im_path=img, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"], blur1=12, min_diam=25, min_area=500) 

# =============================================================================
# for comparison: three different methods:
# =============================================================================
# better, but not good. we need to try different thresolding methods
# adaptive
of.run(im_path=img, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"],blur1=12, min_diam=25, min_area=500, method = ("adaptive", 149, 1)) 
# binary
of.run(im_path=img, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"], blur1=12, min_diam=25, min_area=500, method = ("binary", 150)) 
# otsu
of.run(im_path=img, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"], blur1=12, min_diam=25, min_area=500, method = "otsu") 

# default method ("otsu") seems to work best: with some more finetuning we should get a good result

# =============================================================================
# with optimum finetuning
# =============================================================================
of.run(im_path=proj.filepaths[0], exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"], blur1=9, min_diam=50, min_area=800, blur2=(19,35), corr_factor=(-5,1,"cross")) 



#%% 6) save results

# we save both image for QC and the data frame, to the folder we specified in the beginning
of.save(image=of.drawn, df=of.df, save_to=proj.save_dir, overwrite=True)


#%% 7) as loop, for all images (coming from step 3)

for p, n in zip(proj.filepaths, proj.filenames):
    
    # if your scale is identical, the scale-finder will find it!
    #scale.current, scale.mask = scale.find(p)    
    
    # if your picture doesn't change dramatically, you can skip this
    arena = pp.polygon_maker()
    arena.draw(img, show=False, mode="box")

    # we use the optimal settings we found above
    of = pp.standard_object_finder()
    of.run(im_path=p, exclude = [scale.mask, arena.mask], scale=scale.measured, show=["image", "df"], blur1=9, min_diam=50, min_area=800, blur2=(19,35), corr_factor=(-5,1,"cross")) 
    
    # save after every iteration
    of.save(image=of.drawn, df=of.df, save_to=proj.save_dir, overwrite=True)
    


