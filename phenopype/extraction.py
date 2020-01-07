#%% modules
import cv2
import copy
import numpy as np
import numpy.ma as ma

from phenopype.settings import colours
from phenopype.utils_lowlevel import _auto_line_thickness, _load_image

#%% methods

# obj_input = p1.PC

def colour_values(obj_input, **kwargs):
    
    ## kwargs
    channels = kwargs.get("channels", ["gray"])
    
    ## load image and contours
    image, flag_input = _load_image(obj_input, load="raw")
    if flag_input == "pype_container":
        contour_dict = obj_input.contours
        contour_df = obj_input.df_result

    ## create forgeround mask
    image_bin = np.zeros(image.shape[:2], np.uint8)
    for label, contour in contour_dict.items():
        if contour["order"]=="parent":
            image_bin = cv2.fillPoly(image_bin, [contour["coords"]], 255)
        elif contour["order"]=="child":
            image_bin = cv2.fillPoly(image_bin, [contour["coords"]], 0)

    foreground_mask = np.invert(np.array(image_bin, dtype=np.bool))

    ## method
    if "gray" in channels:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        new_cols = {"gray_mean":"NA",
                    "gray_sd":"NA"}
        contour_df = contour_df.assign(**new_cols)
        for label, contour in contour_dict.items():
            rx,ry,rw,rh = cv2.boundingRect(contour["coords"])
            grayscale =  ma.array(data=image_gray[ry:ry+rh,rx:rx+rw], mask = foreground_mask[ry:ry+rh,rx:rx+rw])
            contour_df.loc[contour_df["label"]==label,["gray_mean","gray_sd"]] = np.ma.mean(grayscale), np.ma.std(grayscale)

    if "rgb" in channels:
        contour_df = contour_df.assign(**{"red_mean":"NA",
                           "red_sd":"NA",
                           "green_mean":"NA",
                           "green_sd":"NA",
                           "blue_mean":"NA",
                           "blue_sd":"NA"})
        for label, contour in contour_dict.items():
            rx,ry,rw,rh = cv2.boundingRect(contour["coords"])
            blue =  ma.array(data=image[ry:ry+rh,rx:rx+rw,0], mask = foreground_mask[ry:ry+rh,rx:rx+rw])
            green =  ma.array(data=image[ry:ry+rh,rx:rx+rw,1], mask = foreground_mask[ry:ry+rh,rx:rx+rw])
            red =  ma.array(data=image[ry:ry+rh,rx:rx+rw,2], mask = foreground_mask[ry:ry+rh,rx:rx+rw])
            contour_df.loc[contour_df["label"]==label,["red_mean","red_sd"]]  = np.ma.mean(red), np.ma.std(red)
            contour_df.loc[contour_df["label"]==label,["green_mean","green_sd"]]  = np.ma.mean(green), np.ma.std(green)
            contour_df.loc[contour_df["label"]==label,["blue_mean","blue_sd"]]  = np.ma.mean(blue), np.ma.std(blue)

    obj_input.df_result = contour_df


