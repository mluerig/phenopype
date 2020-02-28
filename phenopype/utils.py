#%% modules

import cv2, copy, os, sys, warnings
import numpy as np
import pandas as pd

from pprint import PrettyPrinter
from PIL import Image, ExifTags
from ruamel.yaml import YAML

from phenopype.utils_lowlevel import _image_viewer 
from phenopype.utils_lowlevel import _load_yaml, _show_yaml, _save_yaml, _yaml_file_monitor
from phenopype.settings import *
from phenopype.core.export import *
from phenopype.core.visualization import *

#%% settings

Image.MAX_IMAGE_PIXELS = 999999999
pretty = PrettyPrinter(width=30)

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return "WARNING: " + str(msg) + '\n'
warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', UserWarning)

#%% classes

class container(object):
    def __init__(self, image, df_image_data, **kwargs):
        """
        Parameters
        ----------
        image : TYPE
            DESCRIPTION.
        df_image_data: TYPE
            DESCRIPTION.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """

        ## kwargs
        self.save_suffix = kwargs.get("save_suffix", None)
        
        self.image = image
        self.image_copy = copy.deepcopy(self.image)
        self.image_mod = copy.deepcopy(self.image)
        self.image_bin = None
        self.image_gray = None
        self.canvas = copy.deepcopy(self.image)
        
        self.df_image_data = df_image_data
        self.df_image_data_copy = copy.deepcopy(self.df_image_data)

        ## attributes
        self.dirpath = None



    def load(self):
        """
        
        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """

        files, loaded = [], []
        if self.save_suffix:
            for file in os.listdir(self.dirpath):
                if self.save_suffix in file and not "pype_config" in file:
                    files.append(file[0:file.rindex('_')])
        else:
            for file in os.listdir(self.dirpath):
                files.append(file[0:file.rindex('.')])
        
        ## contours
        if not hasattr(self, "df_contours") and "contours" in files:
            path = os.path.join(self.dirpath, "contours_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_contours = pd.read_csv(path) 
                loaded.append("contours_" + self.save_suffix + ".csv")

        ## landmarks
        if not hasattr(self, "df_landmarks") and "landmarks" in files:
            path = os.path.join(self.dirpath, "landmarks_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_landmarks = pd.read_csv(path) 
                loaded.append("landmarks_" + self.save_suffix + ".csv")

        ## polylines
        if not hasattr(self, "df_polyline"):
            path = os.path.join(self.dirpath, "polylines_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_polylines = pd.read_csv(path) 
                loaded.append("polylines_" + self.save_suffix + ".csv")

        ## masks
        if not hasattr(self, "df_masks"):
            path = os.path.join(self.dirpath, "masks_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_masks = pd.read_csv(path) 
                loaded.append("masks_" + self.save_suffix + ".csv")

        ## feedback
        if len(loaded)>0:
            print("AUTOLOAD\n- " + '\n- '.join(loaded) )



    def reset(self):
        """
        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """
        self.image = copy.deepcopy(self.image_copy)
        self.canvas = copy.deepcopy(self.image_copy)



    def save(self, **kwargs):
        """
        

        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        cfg = "pype_config_v1.yaml"
        cfg[cfg.rindex('_')+1:cfg.rindex('.')]

        """
        ## kwargs
        export_list = kwargs.get("export_list",[])
        
        ## feedback
        print("AUTOSAVE")
        
        ## canvas
        if not self.canvas.__class__.__name__ == "NoneType" and not "save_canvas" in export_list:
            print("save_canvas")
            save_canvas(self)

        ## contours
        if hasattr(self, "df_contours") and not "save_contours" in export_list:
            print("save_contours")
            save_contours(self, overwrite=False)

        ## landmarks
        if hasattr(self, "df_landmarks") and not "save_landmarks" in export_list:
            print("save_landmarks")
            save_landmarks(self, overwrite=False)

        ## masks
        if hasattr(self, "df_masks") and not "save_masks" in export_list:
            print("save_masks")
            save_masks(self, overwrite=False)

        ## polylines
        if hasattr(self, "df_polylines") and not "save_polylines" in export_list:
            print("save_polylines")
            save_polylines(self, overwrite=False)



    def show(self, **kwargs):
        """
        
    
        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].
        **kwargs : TYPE
            DESCRIPTION.
    
        Returns
        -------
        None.
    
        cfg = "pype_config_v1.yaml"
        cfg[cfg.rindex('_')+1:cfg.rindex('.')]
    
        """
        ## kwargs
        show_list = kwargs.get("show_list",[])
        
        ## feedback
        print("AUTOSHOW")
        
        ## canvas
        if not "select_canvas" in show_list:
            select_canvas(self)
    
        ## contours
        if hasattr(self, "df_contours") and not "show_contours" in show_list:
            print("show_contours")
            show_contours(self)
    
        ## landmarks
        if hasattr(self, "df_landmarks") and not "save_landmarks" in export_list:
            print("save_landmarks")
            save_landmarks(self, overwrite=False)
    
        ## masks
        if hasattr(self, "df_masks") and not "show_masks" in show_list:
            print("show_masks")
            show_masks(self)
    
        # ## polylines
        # if hasattr(self, "df_polylines") and not "save_polylines" in export_list:
        #     save_polylines(self, overwrite=False)

#%% functions
            
def load_directory(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    ## kwargs
    flag_container = kwargs.get("container", True)
    flag_df = kwargs.get("df", False)
    flag_meta = kwargs.get("meta", True)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]
        
    if not os.path.isdir(obj_input):
        sys.exit("Not a valid phenoype directory - cannot load files.")
        
    attr = _load_yaml(os.path.join(obj_input, "attributes.yaml"))
    image = cv2.imread(attr["project"]["raw_path"])
    df = pd.DataFrame({"filename": attr["image"]["filename"],
                       "width": attr["image"]["width"],
                       "height": attr["image"]["height"]
                       }, index=[0])

    ## add meta-data 
    if flag_meta:
        exif_data_all, exif_data = attr["meta"], {}
        for field in exif_fields:
            if field in exif_data_all:
                exif_data[field] = exif_data_all[field]
        exif_data = dict(sorted(exif_data.items()))
        df = pd.concat([df.reset_index(drop=True), pd.DataFrame(exif_data, index=[0])], axis=1)

    ## return
    if flag_container == True:
        ct = container(image, df)
        ct.dirpath = obj_input
        ct.image_data = attr["image"]
        
    ## check for masks
    masks_path = os.path.join(obj_input, "masks.yaml")
    if os.path.isfile(masks_path):
        ct.masks = _load_yaml(masks_path)

    ## for future release 
    # ==> here, other objects from directory can be loaded and injected to container

    if flag_container == True:
        return ct
    elif flag_container == False:
        if flag_df:
            return image, df
        else:
            return image



def load_image(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    ## kwargs 
    flag_container = kwargs.get("container", False)
    flag_df = kwargs.get("df", False)
    flag_meta = kwargs.get("meta", False)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]

    ## method
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            image = cv2.imread(obj_input)
        else:
            sys.exit("Invalid image path - cannot load image from str.")
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
    else:
        sys.exit("Invalid input format - cannot load image.")

    ## load image data
    image_data = load_image_data(obj_input)
    df_image_data = pd.DataFrame({"filename": image_data["filename"],
          "width": image_data["width"],
          "height": image_data["height"]}, index=[0])

    ## add meta-data 
    if flag_meta:
        meta_data = load_meta_data(obj_input, fields=exif_fields)        
        df_image_data = pd.concat([df_image_data.reset_index(drop=True), pd.DataFrame(meta_data, index=[0])], axis=1)

    ## return
    if flag_container == True:
        ct = container(image, df_image_data)
        ct.image_data = image_data
        ct.dirpath = os.getcwd()
        return ct
    elif flag_container == False:
        if flag_df:
            return image, df_image_data
        else:
            return image



def load_image_data(obj_input):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.

    Returns
    -------
    image_data : TYPE
        DESCRIPTION.

    """
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            path = obj_input
        elif os.path.isdir(obj_input):
            attr = _load_yaml(os.path.join(obj_input, "attributes.yaml"))
            path = attr["project"]["raw_path"]
        image = Image.open(path)
        width, height = image.size
        image.close()
        image_data = {
            "filename": os.path.split(obj_input)[1],
            "filepath": obj_input,
            "filetype": os.path.splitext(obj_input)[1],
            "width": width,
            "height": height
            }
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
        width, height = image.shape[0:2]
        image_data = {
                "filename": "unknown",
                "filepath": "unkown",
                "filetype": "array_type",
                "width": width,
                "height": height
            }
    else:
        warnings.warn("Not a valid image file - cannot read image data.")

    ## issue warnings for large images
    if width*height > 125000000:
        warnings.warn("Large image - expect slow processing and consider resizing.")
    elif width*height > 250000000:
        warnings.warn("Extremely large image - expect very slow processing and consider resizing.")

    ## return image data
    return image_data



def load_meta_data(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    ## kwargs
    flag_show = kwargs.get("show_fields", False)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]
        
    # ## check if basic fields are present
    # if exif_fields.__class__.__name__ == "list":
    #     if not len(exif_fields) == 0:
    #         prepend = list(set(default_fields) - set(exif_fields))
    #         exif_fields = prepend + exif_fields

    ## read image
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            image = Image.open(obj_input)
        else:
            warnings.warn("Not a valid image file - cannot read exif data.")
            return {}
    else:
        warnings.warn("Not a valid image file - cannot read exif data.")
        return {}

    ## populate dictionary
    exif_data_all = {}
    exif_data = {}
    try:
        for k, v in image._getexif().items():
            if k in ExifTags.TAGS:
                exif_data_all[ExifTags.TAGS[k]] = v
        exif_data_all = dict(sorted(exif_data_all.items()))
    except Exception:
        warnings.warn("No exif data found.")

    if flag_show:
        print("--------------------------------------------")
        print("Available exif-tags:\n")
        pretty.pprint(exif_data_all)
        print("\n")
        print("Default exif-tags (append list using \"fields\" argument):\n")
        print(default_meta_data_fields)
        print("--------------------------------------------")

    ## subset exif_data
    for field in exif_fields:
        if field in exif_data_all:
            exif_data[field] = str(exif_data_all[field])
    exif_data = dict(sorted(exif_data.items()))

    ## close image and return meta data
    image.close()
    return exif_data






def show_image(image, **kwargs):
    """Show one or multiple images by providing path string or array or list of either.
    
    Parameters
    ----------
    image: str, array, or list
        the image or list of images to be displayed. can be path to image (string), array-type, or list of strings or arrays
    window_aspect: str (default: "fixed")
        "fixed" or "free" aspect ratio
    position_reset: bool
        flag whether image positions should be reset when reopening list of images
    position_offset: int 
        if image is list, the distance in pixels betweeen the positions of each newly opened window (only works in conjunction with "position_reset")
    """
    
    ## kwargs
    max_dim = kwargs.get("max_dim", 1200)
    pos_offset = kwargs.get("position_offset", 25)
    pos_reset = kwargs.get("position_reset", False)
    window_aspect = kwargs.get("aspect", "free")
    if window_aspect == "free":
        window_aspect = cv2.WINDOW_NORMAL
    elif window_aspect == "fixed":
        window_aspect = cv2.WINDOW_AUTOSIZE

    
    ## open images list or single images
    while True:
        if isinstance(image, list):
            if len(image)>10:
                warning_banner = np.zeros((30,900,3))
                warning_string = "WARNING: trying to open " + str(len(image)) + " images - proceed (Enter) or stop (Esc)?"
                warning_image = cv2.putText(warning_banner,  warning_string ,(11,22), cv2.FONT_HERSHEY_SIMPLEX  , 0.75, colours.green,1,cv2.LINE_AA)
                cv2.namedWindow('phenopype' ,cv2.WINDOW_AUTOSIZE )
                cv2.imshow('phenopype', warning_image)
                k = cv2.waitKey(0)
                cv2.destroyAllWindows()
                if k == 27:
                    print("Stop - terminating.")
                    break
                elif k == 13:
                    print("Proceed - Opening images ...")
            idx=0
            for i in image:
                idx+=1
                _image_viewer(i, 
                              mode = "", 
                              window_aspect = window_aspect, 
                              window_name='phenopype' + " - " + str(idx), 
                              window_control="external",
                              max_dim=max_dim)
                if pos_reset == True:
                    cv2.moveWindow('phenopype' + " - " + str(idx),idx+idx*pos_offset,idx+idx*pos_offset)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break
        else:
            _image_viewer(image, 
                  mode = "", 
                  window_aspect = window_aspect, 
                  window_name='phenopype', 
                  window_control="internal",
                  max_dim=max_dim)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break





def save_image(image, name, **kwargs):
    """Save an image (array) to jpg.
    
    Parameters
    ----------
    image: array
        image to save
    name: str
        name for saved image
    save_dir: str
        location to save image
    append: str ("")
        append image name with string to prevent overwriting
    extension: str ("")
        file extension to save image with
    overwrite: bool (optional, default: False)
        overwrite images if name exists
    """
    # set dir and names
    out_dir = kwargs.get('save_dir', os.getcwd())     
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    app = kwargs.get('append',"")
    new_name = os.path.splitext(name)[0] + app
        
    ext = kwargs.get('extension',os.path.splitext(name)[1])
    new_name = new_name + ext
    
    im_path=os.path.join(out_dir , new_name)
    
    if "resize" in kwargs:
        factor = kwargs.get('resize')
        image = cv2.resize(image, (0,0), fx=1*factor, fy=1*factor) 
    
    if kwargs.get('overwrite',False) == False:
        if not os.path.exists(im_path):
            cv2.imwrite(im_path, image)
    else:
        cv2.imwrite(im_path, image)


