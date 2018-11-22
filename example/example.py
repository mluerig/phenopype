# -*- coding: utf-8 -*-
"""
Last Update: 2018/10/07
Version 0.4.5
@author: Moritz Lürig
"""

#%% load modules

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


#%% example 1 - multiple object in one image

in_dir = "E:\\Python1\\phenopype\\example\\example1\\ex1_images"

proj = pp.project()    
proj.project_maker("example1", in_dir=in_dir)

scale = pp.scale_maker()
scale.measure(proj.filepaths[0], length=10, unit="mm", crop=True, zoom=True, save=True)

# initialize object finder
of = pp.standard_object_finder()

# =============================================================================
# run with no finetuning
# =============================================================================
of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"]) 
# [exclude] mask from the scale outline we drew
# 

# =============================================================================
# with some finetuning
# =============================================================================
of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"], blur1=25, min_size=50, min_area=5000) 

# =============================================================================
# for comparison: three different methods:
# =============================================================================
# adaptive
of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"], blur1=39, min_size=50, min_area=5000, method = ("adaptive", 149, 1)) 
# binary
of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"], blur1=39, min_size=50, min_area=5000, method = ("binary", 150)) 
# otsu
of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"], blur1=39, min_size=50, min_area=5000, method = "otsu") 

# =============================================================================
# default method ("otsu") seems to work best: with some more finetuning we 
# get a good result
# =============================================================================

of.run(im_path=proj.filepaths[0], exclude = [scale.mask], scale=scale.measured, show=["image", "df"], blur1=19, min_size=40, min_area=5000, blur2=(80,70), corr_factor=(-40,1,"cross")) 


# save results
of.save(output=proj.out_dir, overwrite=True)


#%% BREAK ALL WINDOWS
cv2.destroyAllWindows()



#%% DEBUG

set(list(proj.df) + list(of.df))

cv2.namedWindow('phenopype' ,cv2.WINDOW_NORMAL)
cv2.imshow('phenopype',  of.morph)
cv2.waitKey(0)
cv2.destroyAllWindows()

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))

thin = cv2.erode(of.morph,kernel, iterations = 1)

cv2.namedWindow('phenopype' ,cv2.WINDOW_NORMAL)
cv2.imshow('phenopype',  thin)
cv2.waitKey(0)
cv2.destroyAllWindows()

df = proj.df
df1 = of.df
df2 = cs.df
df1.set_index('filename', drop=True, inplace=True)

df = pd.DataFrame(data=list(zip(proj.filepaths, proj.filenames)), columns = ["filepath", "filename"])
df.index = proj.filenames
df.insert(0, "project", proj.name)
df.drop_uplicates(subset="filename", inplace=True)
df.drop(columns=["filepath"], inplace=True)
