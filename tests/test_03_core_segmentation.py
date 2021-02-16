#%% modules

import copy
import numpy as np

import phenopype as pp

from .settings import flag_overwrite

#%% tests

def test_blur(project_container):
    pp.segmentation.blur(project_container, kernel_size=7)
    assert not (project_container.image_copy==project_container.image).all()

def test_threshold(project_container):
    pp.segmentation.threshold(project_container, method="adaptive", 
                              blocksize=149, constant=10, channel="red")
    unique, counts = np.unique(project_container.image, return_counts=True)
    assert len(unique) == 2

def test_morphology(project_container):
    pp.segmentation.morphology(project_container, operation="close", 
                                shape="ellipse", kernel_size=3, iterations=2)
    assert not np.any(np.not_equal(project_container.image_bin, project_container.image))
        
def test_watershed(project_container):
    image = copy.deepcopy(project_container.image_copy)
    thresh = copy.deepcopy(project_container.image)
    water = pp.segmentation.watershed(image, thresh)
    assert not (thresh==water).all()

def test_draw(project_container):
    test_params = {"flag_test_mode": True,
                   "line_width": 2,
                   "line_colour": (0,0,0),
                   "point_list": [[(1417, 327), (1410, 346)]]}
    pp.segmentation.draw(project_container, overwrite=flag_overwrite, test_params=test_params)
    assert project_container.df_drawings.iloc[0]["coords"] == "[(1417, 327), (1410, 346)]"
    
def test_find_contours(project_container):
    pp.segmentation.find_contours(project_container, min_area=250)
    assert len(project_container.df_contours)>0
    
