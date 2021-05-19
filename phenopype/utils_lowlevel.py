#%% modules

import cv2, copy, os, sys, warnings
import numpy as np
import pandas as pd

import time
from datetime import datetime
from math import cos
from stat import S_IWRITE
from ruamel.yaml import YAML
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from phenopype.settings import colours, confirm_options, pype_config_templates
from phenopype.settings import flag_verbose, opencv_window_flags

## capture yaml output - temp
from contextlib import redirect_stdout
import io

#%% settings




#%% classes

# @_image_viewer_settings
class _image_viewer:
    def __init__(self, 
                 image, 
                 tool=None,
                 window_aspect='normal', 
                 window_control='internal', 
                 window_max_dimension=1000, 
                 zoom_magnification=0.5, 
                 zoom_mode='continuous', 
                 zoom_steps=20,
                 **kwargs):
        
        """
        Low level interactive image function.
        
        Future versions of phenopype will feature a more clean and userfriendly
        code structure.
        
        Parameters
        ----------

        """
        
        ## kwargs
        self.flag_text_label = kwargs.get("flag_text_label", False)
        self.canvas_blend_factor = kwargs.get("blend", 0.5)
        
        ## set class arguments
        self.flag_tool = tool
        self.flag_zoom_mode = zoom_mode       
        self.zoom_magnification = zoom_magnification
        self.zoom_n_steps = zoom_steps
        self.wait_time = 100        
        self.window_name = "phenopype"
                
        ## needs cleaning
        self.flag_draw = kwargs.get("draw", False)
        self.flag_test_mode = kwargs.get("test_mode", False)
        
        # =============================================================================
        # initialize variables
        # =============================================================================

        ## image
        self.image = copy.deepcopy(image)
        self.image_width, self.image_height = self.image.shape[1], self.image.shape[0]
        
        ## binary image (for blending)
        if "image_bin" in kwargs:
            image_bin = kwargs.get("image_bin")
            if len(image_bin.shape) == 2:
                self.image_bin = cv2.cvtColor(copy.deepcopy(image_bin), cv2.COLOR_GRAY2BGR)
            if not self.image.shape == self.image_bin.shape:
                print("binary image has different dimensions than input image")
                return
        
        ## get canvas dimensions
        if self.image_height > window_max_dimension or self.image_width > window_max_dimension:
            if self.image_width >= self.image_height:
                self.canvas_width, self.canvas_height = window_max_dimension, int(
                    (window_max_dimension / self.image_width) * self.image_height)
            elif self.image_height > self.image_width:
                self.canvas_width, self.canvas_height = int(
                    (window_max_dimension / self.image_height) * self.image_width), window_max_dimension
            
        ## canvas resize factor
        self.canvas_fx, self.canvas_fy = (
            self.image_width / self.canvas_width,
            self.image_height / self.canvas_height,
        )
        self.global_fx, self.global_fy = self.canvas_fx, self.canvas_fy

        ## zoom config
        self.zoom_x1, self.zoom_y1, self.zoom_x2, self.zoom_y2 = (
            0,
            0,
            self.image_width,
            self.image_height,
        )
        self.flag_zoom, self.zoom_idx = -1, 1
        self.zoom_step_x, self.zoom_step_y = (
            int(self.image_width / self.zoom_n_steps),
            int(self.image_height / self.zoom_n_steps),
        )
        if self.flag_zoom_mode == "fixed":
            mag = int(self.zoom_magnification * self.zoom_n_steps)
            self.zoom_step_x, self.zoom_step_y = (
                mag * self.zoom_step_x,
                mag * self.zoom_step_y,
            )

        ## configure tools
        if self.flag_tool:
            self.points, self.polygons, self.rect_start = [], [], None
            self.line_width = kwargs.get("line_width", _auto_line_width(image))
            self.line_colour = colours[kwargs.get("line_colour", "green")]
            if self.flag_tool in ["landmarks", "landmark"]:
                self.point_size = kwargs.get("point_size", _auto_point_size(image))
                self.point_colour = colours[kwargs.get("point_colour", "red")]
                self.text_size = kwargs.get("label_size", _auto_text_size(image))
                self.text_width = kwargs.get("label_size", _auto_text_width(image))
                self.label_colour = colours[kwargs.get("label_colour", "black")]

        # =============================================================================
        # open canvas
        # =============================================================================
        
        ## initialize canvas
        self._canvas_renew()
        self._canvas_mount()
        
        ## show canvas
        self.done = False
        self.finished = False
        cv2.namedWindow(self.window_name, opencv_window_flags[window_aspect])
        cv2.startWindowThread()  ## needed for Mac OS ??
        cv2.setMouseCallback(self.window_name, self._on_mouse_plain)
        cv2.resizeWindow(self.window_name, self.canvas_width, self.canvas_height)
        cv2.imshow(self.window_name, self.canvas)

        # =============================================================================
        # window control
        # =============================================================================
        
        if window_control == "internal":
            if self.flag_test_mode == True:
                self.done = True
                self.finished = True
                cv2.waitKey(self.wait_time)
                cv2.destroyAllWindows()
            elif self.flag_test_mode == False:
                if cv2.waitKey() == 13:
                    self.done = True
                    cv2.destroyAllWindows()
                elif cv2.waitKey() == 10:
                    self.done = True
                    self.finished = True
                    cv2.destroyAllWindows()
                elif cv2.waitKey() == 27:
                    cv2.destroyAllWindows()
                    sys.exit("\n\nTERMINATE (by user)")
            if self.flag_tool in ["polygon", "poly"]:
                if len(self.points) > 2:
                    self.points.append(self.points[0])
                    self.polygons.append(self.points)
            elif self.flag_tool in ["polyline","polylines","lines"]:
                if len(self.points) > 0:
                    self.polygons.append(self.points)
            # elif self.flag_tool in ["rectangle", "rect","template"]:
            #     if len(self.rect_list) > 0:
            #         for rect in self.rect_list:
            #             xmin, ymin, xmax, ymax = rect
            #             self.polygons.append(
            #                 [
            #                     (xmin, ymin),
            #                     (xmax, ymin),
            #                     (xmax, ymax),
            #                     (xmin, ymax),
            #                     (xmin, ymin),
            #                 ]
            #             )
            elif self.flag_tool in ["landmarks", "landmark"]:
                self.polygons.append(self.points)
        else:
            if self.flag_test_mode == True:
                self.done = True
                cv2.waitKey(self.wait_time)
                cv2.destroyAllWindows()

    def _on_mouse_plain(self, event, x, y, flags, params):
        if event == cv2.EVENT_MOUSEWHEEL and flags > 0:
            if self.zoom_idx < self.zoom_n_steps:
                self.flag_zoom = 1
                self.zoom_idx += 1
                if self.flag_zoom_mode == "continuous" or (
                    self.flag_zoom_mode == "fixed" and self.zoom_idx == 2
                ):
                    self._zoom_fun(x, y)
                self.x, self.y = x, y
                cv2.imshow(self.window_name, self.canvas)
        if event == cv2.EVENT_MOUSEWHEEL and flags < 0:
            if self.zoom_idx > 1:
                self.flag_zoom = -1
                self.zoom_idx -= 1
                if self.flag_zoom_mode == "continuous" or (
                    self.flag_zoom_mode == "fixed" and self.zoom_idx == 1
                ):
                    self._zoom_fun(x, y)
                self.x, self.y = x, y
                cv2.imshow(self.window_name, self.canvas)

        if self.flag_tool and not self.flag_draw:
            if self.flag_tool == "landmark" or self.flag_tool == "landmarks":
                self._on_mouse_point(event, x, y)
            elif self.flag_tool == "rectangle" or self.flag_tool == "rect":
                self._on_mouse_rectangle(event, x, y, flags)
            elif self.flag_tool == "polygon" or self.flag_tool == "poly":
                self._on_mouse_polygon(event, x, y, flags)
            elif self.flag_tool == "polyline" or self.flag_tool == "polylines":
                self._on_mouse_polygon(event, x, y, flags, polyline=True)
            elif self.flag_tool == "reference":
                self._on_mouse_polygon(event, x, y, flags, reference=True)
            elif self.flag_tool == "template":
                self._on_mouse_rectangle(event, x, y, flags, template=True)
        elif self.flag_tool and self.flag_draw:
            if self.flag_tool == "rectangle" or self.flag_tool == "rect":
                self._on_mouse_rectangle(event, x, y, flags, draw=True)
            elif self.flag_tool == "polygon" or self.flag_tool == "poly":
                self._on_mouse_polygon(event, x, y, flags, draw=True)
            elif self.flag_tool == "line" or self.flag_tool == "lines":
                self._on_mouse_polygon(event, x, y, flags, draw=True)
            elif self.flag_tool == "polyline" or self.flag_tool == "polylines":
                self._on_mouse_polygon(event, x, y, flags, polyline=True)
                
    def _on_mouse_point(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
        
            ## convert cursor coords from zoomed canvas to original coordinate space
            self._get_coords_original(x,y)
            
            ## append points to point list
            self.points.append(self.coords_original)
            
            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(tool="point", coord_list=self.points)
            self._canvas_mount()
            
        if event == cv2.EVENT_RBUTTONDOWN:
            
            ## remove points from list, if any are left
            if len(self.points) > 0:
                self.points = self.points[:-1]
                
            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(tool="point", coord_list=self.points)
            self._canvas_mount()
                

    def _on_mouse_polygon(self, event, x, y, flags, **kwargs):

        ## kwargs
        polyline = kwargs.get("polyline", False)
        reference = kwargs.get("reference", False)
        flag_draw = kwargs.get("draw", False)

        if event == cv2.EVENT_MOUSEMOVE:
            if (reference or flag_draw) and self.flag_tool == "line" and len(self.points) == 2:
                return
            
            ## draw line between current cursor coords and last polygon node
            if len(self.points) > 0:
                self.coords_prev = (
                    int((self.points[-1][0] - self.zoom_x1) / self.global_fx),
                    int((self.points[-1][1] - self.zoom_y1) // self.global_fy),
                )
                self.canvas = copy.deepcopy(self.canvas_copy)
                cv2.line(
                    self.canvas,
                    self.coords_prev,
                    (x, y),
                    self.line_colour,
                    self.line_width,
                )
                
            ## if in reference mode, don't connect
            elif (reference or flag_draw) and self.flag_tool == "line" and len(self.points) > 2:
                pass
            
            ## pump updates
            cv2.imshow(self.window_name, self.canvas)
            
            
        if event == cv2.EVENT_LBUTTONDOWN:  ## and (flags & cv2.EVENT_FLAG_CTRLKEY)
        
            ## skip if in reference mode
            if reference and len(self.points) == 2:
                print("already two points selected")
                return
            
            ## convert cursor coords from zoomed canvas to original coordinate space
            self._get_coords_original(x,y)
            
            ## append points to point list
            self.points.append(self.coords_original)
            
            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(
                tool="line", coord_list=self.polygons + [self.points])
            self._canvas_mount()
            
            ## if in reference mode, append to ref coords
            if reference and len(self.points) == 2:
                print("Reference set")
                self.reference_coords = self.points
            if flag_draw and self.flag_tool == "line" and len(self.points) == 2:
                self.polygons.append(self.points)
                self.points = []
                
        if event == cv2.EVENT_RBUTTONDOWN:
            
            ## remove points and update canvas
            if len(self.points) > 0:
                self.points = self.points[:-1]
            else:
                self.polygons = self.polygons[:-1]
                
            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(
                tool="line", coord_list=self.polygons + [self.points])
            self._canvas_mount()

        if flags == cv2.EVENT_FLAG_CTRLKEY and len(self.points) > 2:
            
            ## close polygon
            if not polyline:
                self.points.append(self.points[0])
                
            ## add current points to polygon and empyt point list
            self.polygons.append(self.points)
            self.points = []

            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(
                tool="line", coord_list=self.polygons + [self.points])
            self._canvas_mount()



    def _on_mouse_rectangle(self, event, x, y, flags, **kwargs):
        
        ## kwargs
        template = kwargs.get("template", False)
        
        if event == cv2.EVENT_LBUTTONDOWN:  
            
            ## end after one set of points if creating a template
            if template == True and len(self.polygons) == 1:
                return
            
            ## start drawing temporary rectangle 
            self.rect_start = x, y
            self.canvas_copy = copy.deepcopy(self.canvas)
            
        if event == cv2.EVENT_LBUTTONUP:
            
            ## end after one set of points if creating a template
            if template == True and len(self.polygons) == 1:
                print("Template selected")
                return
            
            ## end drawing temporary rectangle
            self.rect_start = None

            ## convert rectangle to polygon coords
            self.rect = [
                int(self.zoom_x1 + (self.global_fx * self.rect_minpos[0])),
                int(self.zoom_y1 + (self.global_fy * self.rect_minpos[1])),
                int(self.zoom_x1 + (self.global_fx * self.rect_maxpos[0])),
                int(self.zoom_y1 + (self.global_fy * self.rect_maxpos[1])),
                ]
            self.polygons.append(
                [
                    (self.rect[0], self.rect[1]), 
                    (self.rect[2], self.rect[1]),
                    (self.rect[2], self.rect[3]),
                    (self.rect[0], self.rect[3]),
                    (self.rect[0], self.rect[1]),
                    ]
            )           
            
            ## apply tool and refresh canvas
            self._canvas_renew()
            self._canvas_draw(
                tool="line", coord_list=self.polygons)
            self._canvas_mount(refresh=False)
            
        if event == cv2.EVENT_RBUTTONDOWN:
            
            ## remove polygons and update canvas
            if len(self.polygons) > 0:
                self.polygons = self.polygons[:-1]
                
                ## apply tool and refresh canvas
                self._canvas_renew()
                self._canvas_draw(
                    tool="line", coord_list=self.polygons)
                self._canvas_mount()

                
        ## draw temporary rectangle
        elif self.rect_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:        
                self.canvas = copy.deepcopy(self.canvas_copy)
                self.rect_minpos = min(self.rect_start[0], x), min(self.rect_start[1], y)
                self.rect_maxpos = max(self.rect_start[0], x), max(self.rect_start[1], y)
                cv2.rectangle(
                    self.canvas,
                    self.rect_minpos,
                    self.rect_maxpos,
                    self.line_colour,
                    self.line_width,
                )
                cv2.imshow(self.window_name, self.canvas)
   
                
    def _canvas_renew(self):

        ## pull copy from original image
        image_copy = copy.deepcopy(self.image)

        ## if provided, mix in binary image
        if hasattr(self, "image_bin"):
            image_bin_copy = copy.deepcopy(self.image_bin)
            self.image_copy = cv2.addWeighted(image_copy,
                                              1 - self.canvas_blend_factor,
                                              image_bin_copy,
                                              self.canvas_blend_factor,
                                              0)
        else:
            self.image_copy = image_copy

        
    def _canvas_draw(self, tool, coord_list):
               
        ## apply coords to tool and draw on canvas
        for coords in coord_list:
            if len(coords)==0:
                continue
            if tool == "line":
                self._draw_line(coords)
            elif tool == "point":
                self._draw_point(coords)
                
    def _canvas_mount(self, refresh=True):
        
        ## pass zoomed part of original image to canvas
        self.canvas = self.image_copy[
            self.zoom_y1 : self.zoom_y2, self.zoom_x1 : self.zoom_x2
        ]
        
        ## resize canvas to fit window
        self.canvas = cv2.resize(
            self.canvas,
            (self.canvas_width, self.canvas_height),
            interpolation=cv2.INTER_LINEAR,
        )
        
        ## copy canvas for mousedrag refresh
        self.canvas_copy = copy.deepcopy(self.canvas)
        
        ## refresh canvas
        if refresh:
            cv2.imshow(self.window_name, self.canvas)


            
    def _get_coords_original(self, x, y):
        self.coords_original = (
                int(self.zoom_x1 + (x * self.global_fx)),
                int(self.zoom_y1 + (y * self.global_fy)),
            )
        
    def _draw_line(self, coord_list):
        cv2.polylines(
            self.image_copy,
            np.array([coord_list]),
            False,
            self.line_colour,
            self.line_width,
        )
                   
    def _draw_point(self, coords):
        cv2.circle(
            self.image_copy,
            coords,
            self.point_size,
            self.point_colour,
            -1,
        )
        if self.flag_text_label:
            cv2.putText(
                self.image_copy,
                str(len(self.points)),
                coords,
                cv2.FONT_HERSHEY_SIMPLEX,
                self.text_size,
                self.label_colour,
                self.text_width,
                cv2.LINE_AA,
            )

    def _zoom_fun(self, x, y):
        """
        Helper function for image_viewer. Takes current xy coordinates and 
        zooms in within a rectangle around mouse coordinates while transforming 
        current cursor coordinates back to original coordinate space
        
        """
        if y <= 0:
            y = 1
        if x <= 0:
            x = 1

        x_prop, y_prop = x / self.canvas_width, y / self.canvas_height
        left_padding, right_padding = (
            int(round(x_prop * self.zoom_step_x)),
            int(round((1 - x_prop) * self.zoom_step_x)),
        )
        top_padding, bottom_padding = (
            int(round(y_prop * self.zoom_step_y)),
            int(round((1 - y_prop) * self.zoom_step_y)),
        )

        if self.flag_zoom > 0:
            x1, x2 = self.zoom_x1 + left_padding, self.zoom_x2 - right_padding
            y1, y2 = self.zoom_y1 + top_padding, self.zoom_y2 - bottom_padding
        if self.flag_zoom < 0:
            x1, x2 = (
                self.zoom_x1 - left_padding,
                self.zoom_x2 + right_padding,
            )
            y1, y2 = self.zoom_y1 - top_padding, self.zoom_y2 + bottom_padding
            if x1 < 0:
                x2 = x2 + abs(x1)
                x1 = 0
            if x2 > self.image_width:
                x1 = x1 - (x2 - self.image_width)
                x2 = self.image_width
            if y1 < 0:
                y2 = y2 + abs(y1)
                y1 = 0
            if y2 > self.image_height:
                y1 = y1 - (y2 - self.image_height)
                y2 = self.image_height

        ## failsafe when zooming out, sets zoom-coords to image coords
        if self.zoom_idx == 1:
            x1,x2,y1,y2 = 0, self.image_width, 0, self.image_height

        ## zoom coords
        self.zoom_x1, self.zoom_x2, self.zoom_y1, self.zoom_y2 = x1, x2, y1, y2

        ## global magnification factor
        self.global_fx = self.canvas_fx * (
            (self.zoom_x2 - self.zoom_x1) / self.image_width
        )
        self.global_fy = self.canvas_fy * (
            (self.zoom_y2 - self.zoom_y1) / self.image_height
        )

        ## update canvas
        self._canvas_mount(refresh=False)
        
        

class _yaml_file_monitor:
    def __init__(self, filepath, delay=100):

        ## file, location and event action
        self.dirpath = os.path.dirname(filepath)
        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        self.event_handler = PatternMatchingEventHandler(patterns=["*/" + self.filename])
        self.event_handler.on_any_event = self.on_update

        ## intitialize
        self.content = _load_yaml(self.filepath, typ="safe")
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.dirpath, recursive=False)
        self.observer.start()
        self.ref_time = time.time()
        self.delay = delay

    def on_update(self, event):
        self.content = _load_yaml(self.filepath, typ="safe")
        cv2.destroyWindow("phenopype")
        for i in range(self.delay):
            cv2.waitKey(1)

    def stop(self):
        self.observer.stop()
        self.observer.join()


#%% functions


def _auto_line_width(image, **kwargs):
    factor = kwargs.get("factor", 0.001)
    image_height, image_width = image.shape[0:2]
    image_diagonal = (image_height + image_width) / 2
    line_width = max(int(factor * image_diagonal), 1)

    return line_width


def _auto_point_size(image, **kwargs):
    factor = kwargs.get("factor", 0.002)
    image_height, image_width = image.shape[0:2]
    image_diagonal = (image_height + image_width) / 2
    point_size = max(int(factor * image_diagonal), 1)

    return point_size


def _auto_text_width(image, **kwargs):
    factor = kwargs.get("factor", 0.0005)
    image_height, image_width = image.shape[0:2]
    image_diagonal = (image_height + image_width) / 2
    text_width = max(int(factor * image_diagonal), 1)

    return text_width


def _auto_text_size(image, **kwargs):
    factor = kwargs.get("factor", 0.00025)
    image_height, image_width = image.shape[0:2]
    image_diagonal = (image_height + image_width) / 2
    text_size = max(int(factor * image_diagonal), 1)

    return text_size


def _contours_arr_tup(array):
    coords_arr = array
    coords_tup = []
    for coord in coords_arr:
        coords_tup.append((coord[0][0], coord[0][1]))
    return coords_tup


def _contours_tup_array(list_tup_list):
    coords_arr_list = []
    for tup_list in list_tup_list:
        arr_list = []
        for tup in tup_list:
            arr = []
            arr.append(tup[0])
            arr.append(tup[1])
            arr_list.append([arr])
        coords_arr_list.append(np.array(arr_list, dtype=np.int32))
    return coords_arr_list






def _create_mask_bin(image, masks):
    mask_bin = np.zeros(image.shape[0:2], np.uint8)
    if masks.__class__.__name__ == "DataFrame":
        for index, row in masks.iterrows():
            coords = eval(row["coords"])
            cv2.fillPoly(mask_bin, [np.array(coords, dtype=np.int32)], colours["white"])
    elif masks.__class__.__name__ == "list":
        cv2.fillPoly(mask_bin, [np.array(masks, dtype=np.int32)], colours["white"])
    return mask_bin


def _create_mask_bool(image, masks):
    mask_bin = _create_mask_bin(image, masks)
    return np.array(mask_bin, dtype=bool)


def _decode_fourcc(cc):
    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])


def _del_rw(action, name, exc):
    os.chmod(name, S_IWRITE)
    os.remove(name)
    
    
def _df_overwrite_checker(df, 
                          annotation, 
                          label,
                          flag_overwrite, 
                          flag_edit):

    if df.__class__.__name__ == "NoneType":
        df = pd.DataFrame()
        print("- creating new {}".format(annotation))
        return df, None
    elif df.__class__.__name__ == "DataFrame":
        if label in df["mask"].values:
            if flag_overwrite == False and flag_edit == False:
                print("- {} with label \"{}\" already created (edit/overwrite=False)".format(annotation,label))
                return None, None
            elif flag_overwrite == True and flag_edit == False:
                df = df.drop(df[df["mask"]==label].index)
                print("- creating {} (overwriting)".format(annotation))
                return df, None
            elif flag_edit == True:
                edit_params = df[df["mask"]==label].to_dict("records")[0]
                df = df.drop(df[df["mask"]==label].index)
                print("- creating {} (editing)".format(annotation))
                return df, edit_params  
        else:
            print("- creating another {}".format(annotation))
            return df, None    
    else:
        print("- wrong df supplied to edit {}".format(annotation))

        
    
    
def _equalize_histogram(image, detected_rect_mask, template):
    """Histogram equalization via interpolation, upscales the results from the detected reference card to the entire image.
    May become a standalone function at some point in the future. THIS STRONGLY DEPENDS ON THE QUALITY OF YOUR TEMPLATE.
    Mostly inspired by this SO question: https://stackoverflow.com/questions/32655686/histogram-matching-of-two-images-in-python-2-x
    More theory here: https://docs.opencv.org/master/d4/d1b/tutorial_histogram_equalization.html
    """
    detected_ravel = detected_rect_mask.ravel()
    template_ravel = template.ravel()

    detected_counts = np.bincount(detected_ravel, minlength=256)
    detected_quantiles = np.cumsum(detected_counts).astype(np.float64)
    detected_quantiles /= detected_quantiles[-1]

    template_values = np.arange(0, 256, 1, dtype=np.uint8)
    template_counts = np.bincount(template_ravel, minlength=256)
    template_quantiles = np.cumsum(template_counts).astype(np.float64)
    template_quantiles /= template_quantiles[-1]

    interp_template_values = np.interp(
        detected_quantiles, template_quantiles, template_values
    )
    interp_template_values = interp_template_values.astype(image.dtype)

    return interp_template_values[image]



def _file_walker(
    directory,
    filetypes=[],
    include=[],
    include_all=True,
    exclude=[],
    recursive=False,
    unique="path",
    **kwargs
):
    """
    
    Parameters
    ----------
    directory : str
        path to directory to search for files
    recursive: (optional): bool,
        "False" searches only current directory for valid files; "True" walks 
        through all subdirectories
    filetypes (optional): list of str
        single or multiple string patterns to target files with certain endings
    include (optional): list of str
        single or multiple string patterns to target certain files to include
    include_all (optional): bool,
        either all (True) or any (False) of the provided keywords have to match
    exclude (optional): list of str
        single or multiple string patterns to target certain files to exclude - can overrule "include"
    unique (optional): str (default: "filepath")
        how should unique files be identified: "filepath" or "filename". "filepath" is useful, for example, 
        if identically named files exist in different subfolders (folder structure will be collapsed and goes into the filename),
        whereas filename will ignore all those files after their first occurrence.

    Returns
    -------
    None.

    """
    ## kwargs
    pype_mode = kwargs.get("pype_mode", False)
    if not filetypes.__class__.__name__ == "list":
        filetypes = [filetypes]
    if not include.__class__.__name__ == "list":
        include = [include]
    if not exclude.__class__.__name__ == "list":
        exclude = [exclude]
    flag_include_all = include_all
    flag_recursive = recursive
    flag_unique = unique
    
    ## find files
    filepaths1, filepaths2, filepaths3, filepaths4 = [], [], [], []
    if flag_recursive == True:
        for root, dirs, files in os.walk(directory):
            for file in os.listdir(root):
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath):
                    filepaths1.append(filepath)
    else:
        for file in os.listdir(directory):
            filepath = os.path.join(directory, file)
            if os.path.isfile(filepath):
                filepaths1.append(filepath)

    ## file endings
    if len(filetypes) > 0:
        for filepath in filepaths1:
            if filepath.endswith(tuple(filetypes)):
                filepaths2.append(filepath)
    elif len(filetypes) == 0:
        filepaths2 = filepaths1

    ## include
    if len(include) > 0:
        for filepath in filepaths2:
            if flag_include_all:
                if all(inc in os.path.basename(filepath) for inc in include):
                    filepaths3.append(filepath)
            else:
                if any(inc in os.path.basename(filepath) for inc in include):
                    filepaths3.append(filepath)
    else:
        filepaths3 = filepaths2

    ## exclude
    if len(exclude) > 0:
        for filepath in filepaths3:
            if not any(exc in os.path.basename(filepath) for exc in exclude):
                filepaths4.append(filepath)
    else:
        filepaths4 = filepaths3

    ## check if files found
    filepaths = filepaths4
    if len(filepaths) == 0 and not pype_mode:
        sys.exit("No files found under the given location that match given criteria.")

    ## allow unique filenames filepath or by filename only
    filenames, unique_filename, unique, duplicate = [], [], [], []
    for filepath in filepaths:
        filenames.append(os.path.basename(filepath))
    if flag_unique in ["filepaths", "filepath", "path"]:
        for filename, filepath in zip(filenames, filepaths):
            if not filepath in unique:
                unique.append(filepath)
            else:
                duplicate.append(filepath)
    elif flag_unique in ["filenames", "filename", "name"]:
        for filename, filepath in zip(filenames, filepaths):
            if not filename in unique_filename:
                unique_filename.append(filename)
                unique.append(filepath)
            else:
                duplicate.append(filepath)

    return unique, duplicate


def _get_circle_perimeter(center_x, center_y, radius):
    coordinate_list=[]
    for i in range(360):
        y = center_x + radius * cos(i)
        x = center_y + radius * cos(i)
        coordinate_list.append((int(x),int(y)))
    return coordinate_list
        

def _load_pype_config(config=None, 
                      template=None,
                      name=None):
    
    ## kwargs and setup
    flag_load_existing_config = False
    flag_create_from_phenopype_template = False
    flag_create_from_user_template = False 
    step_names = ["preprocessing", 
                  "segmentation", 
                  "measurement",  
                  "visualization", 
                  "export"]
    
    ## decision tree 1: context
    if config.__class__.__name__ == "str":
        if not config.endswith(".yaml"):
            config = config + ".yaml"
        if os.path.isfile(config):
            flag_load_existing_config = True
        else:    
            print("No config file found at: {}".format(config))
            return
    elif config.__class__.__name__ == "NoneType" and template.__class__.__name__ == "str":
        if not template.endswith(".yaml"):
            template = template + ".yaml"
        if template in pype_config_templates:
            flag_create_from_phenopype_template = True
        elif os.path.isfile(template):
            flag_create_from_user_template = True
        else:
            print("Invalid template supplied - aborting.")
            return
    else:
        print("Could not load config or template - pease check input.")
        return 
    
    ## decision tree 2 - return
    if flag_load_existing_config:
        config_name = os.path.basename(config)
        config_path = config
        print("Succesfully loaded existing pype config ({}) from:\n{} ".format((config_name),(config_path)))
        config = _load_yaml(config_path)
        return config
    if flag_create_from_phenopype_template:
        config_steps = _load_yaml(pype_config_templates[template])
        config_path = "NA"
        template_name = template
        template_path = pype_config_templates[template]
        print("New pype configuration created ({}) from phenopype template:\n{}".format((template),(template_path)))
    if flag_create_from_user_template:
        config_loaded = _load_yaml(template)
        config_path = "NA"
        template_name = os.path.basename(template)
        template_path = template
        print("New pype configuration created ({}) from custom user template:\n{}".format((template),(template_path)))
        if config_loaded.__class__.__name__ in ["dict", 'CommentedMap']:
            if "config_info" in config_loaded:
                config_loaded.pop('config_info', None)
                print("Removed existing \"config_info\" section")
            if "processing_steps" in config_loaded:
                config_steps = config_loaded["processing_steps"]
            else:
                print("Broken template - check for correct template structure")
                return
        elif config_loaded.__class__.__name__ in ["list",'CommentedSeq'] and any(step in config_loaded[0] for step in step_names):
            config_steps = config_loaded
            
    ## create config-layout
    if name.__class__.__name__ == "NoneType":
        config_name = "NA"
    elif name.__class__.__name__ == "str":
        config_name = "pype_config_" + name + ".yaml"
    config_info = {"config_name":config_name,
                   "config_path": config_path,
                   "template_name":template_name,
                   "template_path":template_path,
                   "date_created":datetime.today().strftime("%Y%m%d%H%M%S"),
                   "date_last_modified":None}
    config = {"config_info":config_info,
              "processing_steps":config_steps}
            
    ## return
    return config


def _load_yaml(string, typ="rt"):
        
    yaml = YAML(typ=typ)

    if string.__class__.__name__ == "str":
        if os.path.isfile(string):
            with open(string, "r") as file:
                file = yaml.load(file)
        else:
            file = yaml.load(string)
        return file
    else:
        warnings.warn("Not a valid path - couldn't load yaml.")
        return



def _show_yaml(odict, ret=False, typ="rt"):
    
    yaml =  YAML(typ=typ)
    
    if ret:
        with io.StringIO() as buf, redirect_stdout(buf):
            yaml.dump(odict, sys.stdout)
            return buf.getvalue()
    else:
        yaml.dump(odict, sys.stdout)
    


def _save_yaml(dictionary, filepath, typ="rt"):
    
    yaml = YAML(typ=typ)      
    
    with open(filepath, "w") as out:
        yaml.dump(dictionary, out)

        

# def _timestamp():
#     return datetime.today().strftime("%Y:%m:%d %H:%M:%S")


# def get_median_grayscale(image, **kwargs):
#     if (image.shape[0] + image.shape[1])/2 > 2000:
#         factor = kwargs.get('resize', 0.5)
#         image = cv2.resize(image, (0,0), fx=1*factor, fy=1*factor)

#     vector = np.ravel(image)
#     vector_mc = Counter(vector).most_common(9)
#     g = [item[0] for item in vector_mc]
#     return int(np.median(g))

# def avgit(x):
#     return x.sum(axis=0)/np.shape(x)[0]

# def decode_fourcc(cc):
#     return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
