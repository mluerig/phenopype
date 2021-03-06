#%% modules
import ast, cv2, copy, os, sys, warnings
import numpy as np
import glob
import pandas as pd
from pathlib import Path


from pprint import PrettyPrinter
from PIL import Image, ExifTags

from phenopype.utils_lowlevel import _image_viewer, _contours_tup_array, _load_yaml, _show_yaml

from phenopype.core.export import *
from phenopype.settings import colours, default_meta_data_fields, default_filetypes, flag_verbose, pype_config_templates, confirm_options


#%% settings

Image.MAX_IMAGE_PIXELS = 999999999
pretty = PrettyPrinter(width=30)

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return "WARNING: " + str(msg) + "\n"

warnings.formatwarning = custom_formatwarning
warnings.simplefilter("always", UserWarning)

#%% classes


class container(object):
    """
    A phenopype container is a Python class where loaded images, dataframes, 
    detected contours, intermediate output, etc. are stored so that they are 
    available for inspection or storage at the end of the analysis. The 
    advantage of using containers is that they don’t litter the global environment 
    and namespace, while still containing all intermediate steps (e.g. binary 
    masks or contour DataFrames). Containers can be used manually to analyse images, 
    but typically they are created dynamically within the pype-routine. 
    
    Parameters
    ----------
    image : ndarray
        single or multi-channel iamge as an array (can be created using load_image 
        or load_directory).
    df_image_data: DataFrame
        a dataframe that contains meta-data of the provided image to be passed on
        to all results-DataFrames
    save_suffix : str, optional
        suffix to append to filename of results files

    """

    def __init__(self, image, df_image_data, dirpath=None, save_suffix=None):

        ## images
        self.image = image
        self.image_copy = copy.deepcopy(self.image)
        self.image_bin = None
        self.image_gray = None
        self.canvas = None

        ## data frames
        self.df_image_data = df_image_data
        self.df_image_data_copy = copy.deepcopy(self.df_image_data)

        ## attributes
        self.dirpath = dirpath
        self.save_suffix = save_suffix
        self.reference_manual_mode = False

    def load(self, dirpath=None, save_suffix=None, contours=False, canvas=False, **kwargs):
        """
        Autoload function for container: loads results files with given save_suffix
        into the container. Can be used manually, but is typically used within the
        pype routine.
        
        Parameters
        ----------
        save_suffix : str, optional
            suffix to include when looking for files to load

        """
        files, loaded = [], []

        ## data flags
        flag_contours = contours

        ## check dirpath
        if (
            dirpath.__class__.__name__ == "NoneType"
            and not self.dirpath.__class__.__name__ == "NoneType"
        ):
            dirpath = self.dirpath
        if dirpath.__class__.__name__ == "NoneType":
            print('No save directory ("dirpath") specified - cannot load files.')
            return
        if not os.path.isdir(dirpath):
            print("Directory does not exist - cannot load files.")
            return

        ## check save_suffix
        if (
            save_suffix.__class__.__name__ == "NoneType"
            and not self.save_suffix.__class__.__name__ == "NoneType"
        ):
            save_suffix = "_" + self.save_suffix
        elif not save_suffix.__class__.__name__ == "NoneType":
            save_suffix = "_" + save_suffix
        else:
            save_suffix = ""

        # collect
        if len(os.listdir(dirpath)) > 0:
            for file in os.listdir(dirpath):
                if os.path.isfile(os.path.join(dirpath, file)):
                    if (
                        len(save_suffix) > 0
                        and save_suffix in file
                        and not "pype_config" in file
                    ):
                        files.append(file[0 : file.rindex("_")])
                    elif len(save_suffix) == 0:
                        files.append(file[0 : file.rindex(".")])

        else:
            print("No files found in given directory")
            return

        ## load attributes
        attr_local_path = os.path.join(dirpath, "attributes.yaml")
        if os.path.isfile(attr_local_path):

            attr_local = _load_yaml(attr_local_path)
                
            ## other data
            if not hasattr(self, "df_other_data"):
                attr = _load_yaml(attr_local_path)
                if "other" in attr:
                    self.df_other_data = pd.DataFrame(attr["other"], index=[0])
                    loaded.append(
                        "columns "
                        + ", ".join(list(self.df_other_data))
                        + " from attributes.yaml"
                    )
            
            if "reference" in attr_local:
                
                ## manually measured px-mm-ratio
                if "manually_measured_px_mm_ratio" in attr_local["reference"]:
                    self.reference_manually_measured_px_mm_ratio = attr_local["reference"]["manually_measured_px_mm_ratio"]
                    loaded.append("manually measured local reference information loaded")
                    
                ## project level template px-mm-ratio
                if "project_level" in attr_local["reference"]:
                    
                    ## load local (image specific) and global (project level) attributes 
                    attr_proj_path =  os.path.abspath(os.path.join(attr_local_path ,r"../../../","attributes.yaml"))
                    attr_proj = _load_yaml(attr_proj_path)
                                        
                    ## find active project level references
                    n_active = 0
                    for key, value in attr_local["reference"]["project_level"].items():
                        if attr_local["reference"]["project_level"][key]["active"] == True:
                            active_ref = key
                            n_active += 1
                    if n_active > 1:
                        print("WARNING: multiple active reference detected - fix with running add_reference again.")                            
                    self.reference_active = active_ref
                    self.reference_template_px_mm_ratio = attr_proj["reference"][active_ref]["template_px_mm_ratio"]
                    loaded.append("project level reference information loaded for " + active_ref)
                
                    ## load previously detect px-mm-ratio
                    if "detected_px_mm_ratio" in attr_local["reference"]["project_level"]:
                        self.reference_detected_px_mm_ratio = attr_local["reference"]["project_level"]["detected_px_mm_ratio"]
                        loaded.append("detected local reference information loaded for " + active_ref)
                        
                    ## load tempate image from project level attributes
                    if "template_image" in attr_proj["reference"][active_ref]:
                        self.reference_template_image = cv2.imread(str(Path(attr_local_path).parents[2] / attr_proj["reference"][active_ref]["template_image"]))
                        loaded.append("reference template image loaded from root directory")

        ## canvas
        if self.canvas.__class__.__name__ == "NoneType" and canvas == True:
            path = os.path.join(dirpath, "canvas" + save_suffix + ".jpg")
            if os.path.isfile(path):
                self.canvas = load_image(path)
                loaded.append("canvas" + save_suffix + ".jpg")

        ## contours
        if flag_contours:
            if not hasattr(self, "df_contours") and "contours" in files:
                path = os.path.join(dirpath, "contours" + save_suffix + ".csv")
                if os.path.isfile(path):
                    df = pd.read_csv(path, converters={"center": ast.literal_eval})
                    if "x" in df:
                        df["coords"] = list(zip(df.x, df.y))
                        coords = df.groupby("contour")["coords"].apply(list)
                        coords_arr = _contours_tup_array(coords)
                        df.drop(columns=["coords", "x", "y"], inplace=True)
                        df = df.drop_duplicates().reset_index()
                        df["coords"] = pd.Series(coords_arr, index=df.index)
                        self.df_contours = df
                        loaded.append("contours" + save_suffix + ".csv")
                    else:
                        print("Could not load contours - df saved without coordinates.")                  
                
        ## drawings
        if not hasattr(self, "df_drawings") and "drawings" in files:
            path = os.path.join(dirpath, "drawings" + save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_drawings = pd.read_csv(path)
                loaded.append("drawings" + save_suffix + ".csv")
                        
        ## landmarks
        if not hasattr(self, "df_landmarks") and "landmarks" in files:
            path = os.path.join(dirpath, "landmarks" + save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_landmarks = pd.read_csv(path)
                loaded.append("landmarks" + save_suffix + ".csv")

        ## polylines
        if not hasattr(self, "df_polylines") and "polylines" in files:
            path = os.path.join(dirpath, "polylines" + save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_polylines = pd.read_csv(path)
                loaded.append("polylines" + save_suffix + ".csv")
                
        ## masks
        if not hasattr(self, "df_masks") and "masks" in files:
            path = os.path.join(dirpath, "masks" + save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_masks = pd.read_csv(path)
                loaded.append("masks" + save_suffix + ".csv")

        ## feedback
        if len(loaded) > 0:
            print("=== AUTOLOAD ===\n- " + "\n- ".join(loaded))
        else:
            print("Nothing loaded.")
            
            

    def reset(self):
        """
        Resets modified images, canvas and df_image_data to original state. Can be used manually, but is typically used within the
        pype routine.

        """
        ## images
        self.image = copy.deepcopy(self.image_copy)
        self.image_bin = None
        self.image_gray = None
        self.canvas = None

        ## attributes
        self.df_image_data = copy.deepcopy(self.df_image_data_copy)
        self.reference_manual_mode = False

        # if hasattr(self, "df_masks"):
        #     del(self.df_masks)

        if hasattr(self, "df_contours"):
            del self.df_contours

    def save(self, dirpath=None, export_list=[], overwrite=False, **kwargs):
        """
        Autosave function for container. 

        Parameters
        ----------
        dirpath: str, optional
            provide a custom directory where files should be save - overwrites 
            dirpath provided from container, if applicable
        export_list: list, optional
            used in pype rountine to check against already performed saving operations.
            running container.save() with an empty export_list will assumed that nothing
            has been saved so far, and will try 
        overwrite : bool, optional
            gloabl overwrite flag in case file exists

        """

        ## kwargs
        flag_overwrite = overwrite

        ## check dirpath
        if (
            dirpath.__class__.__name__ == "NoneType"
            and not self.dirpath.__class__.__name__ == "NoneType"
        ):
            print("=== AUTOSAVE ===")
            dirpath = self.dirpath
        if dirpath.__class__.__name__ == "NoneType":
            print('No save directory ("dirpath") specified - cannot save files.')
            return
        if not os.path.isdir(dirpath):
            print("Directory does not exist - cannot save files.")


        ## canvas
        if (
            not self.canvas.__class__.__name__ == "NoneType"
            and not "save_canvas" in export_list
        ):
            print("save_canvas")
            save_canvas(self, dirpath=dirpath)

        ## colours
        if hasattr(self, "df_colours") and not "save_colours" in export_list:
            print("save_colours")
            save_colours(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## contours
        if hasattr(self, "df_contours") and not "save_contours" in export_list:
            print("save_contours")
            save_contours(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## entered data
        if hasattr(self, "df_other_data") and not "save_data_entry" in export_list:
            print("save_data_entry")
            save_data_entry(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## landmarks
        if hasattr(self, "df_landmarks") and not "save_landmarks" in export_list:
            print("save_landmarks")
            save_landmarks(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## masks
        if hasattr(self, "df_masks") and not "save_masks" in export_list:
            print("save_masks")
            save_masks(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## polylines
        if hasattr(self, "df_polylines") and not "save_polylines" in export_list:
            print("save_polylines")
            save_polylines(self, dirpath=dirpath, overwrite=flag_overwrite)

        ## drawing
        if hasattr(self, "df_drawings") and not "save_drawings" in export_list:
            print("save_drawings")
            save_drawings(self, dirpath=dirpath, overwrite=True)

        ## reference
        if hasattr(self, "reference_detected_px_mm_ratio") and not "save_reference" in export_list:
            print("save_reference")
            save_reference(self, dirpath=dirpath, overwrite=True, active_ref=self.reference_active)
            
        ## shapes
        if hasattr(self, "df_shapes") and not "save_shapes" in export_list:
            print("save_shapes")
            save_shapes(self, dirpath=dirpath, overwrite=True)
            
        ## textures
        if hasattr(self, "df_textures") and not "save_textures" in export_list:
            print("save_textures")
            save_textures(self, dirpath=dirpath, overwrite=True)


    # def show(self, **kwargs):
    #     """

    #     Parameters
    #     ----------
    #     components : TYPE, optional
    #         DESCRIPTION. The default is [].
    #     **kwargs : TYPE
    #         DESCRIPTION.

    #     Returns
    #     -------
    #     None.

    #     cfg = "pype_config_v1.yaml"
    #     cfg[cfg.rindex('_')+1:cfg.rindex('.')]

    #     """
    #     ## kwargs
    #     show_list = kwargs.get("show_list",[])

    #     ## feedback
    #     print("AUTOSHOW")

    # ## contours
    # if hasattr(self, "df_contours") and not "show_contours" in show_list:
    #     print("show_contours")
    #     show_contours(self)

    # ## landmarks
    # if hasattr(self, "df_landmarks") and not "show_landmarks" in show_list:
    #     print("show_landmarks")
    #     show_landmarks(self)

    # ## masks
    # if hasattr(self, "df_masks") and not "show_masks" in show_list:
    #     print("show_masks")
    #     show_masks(self)

    # ## polylines
    # if hasattr(self, "df_polylines") and not "show_polylines" in show_list:
    #     print("show_polylines")
    #     show_polylines(self)


#%% functions





def load_image(
    obj_input,
    mode="default",
    cont=False,
    df=False,
    dirpath=None,
    meta=False,
    resize=1,
    save_suffix=None,
    **kwargs
):
    """
    Create ndarray from image path or return or resize exising array.

    Parameters
    ----------
    obj_input: str or ndarray
        can be a path to an image stored on the harddrive OR an array already 
        loaded to Python.
    mode: {"default", "colour","gray"} str, optional
        image conversion on loading:
            - default: return image as is
            - colour: convert image to 3channel bgr
            - gray: convert image to single channel 
    cont: bool, optional
        should the loaded image (and DataFrame) be returned as a phenopype 
        container
    df: bool, optional
        should a DataFrame containing image information (e.g. dimensions) be 
        returned.
    dirpath: str, optional
        path to an existing directory where all output should be stored. default 
        is the current working directory ("cwd") of the python session.
    meta: bool, optional
        should the DataFrame encompass image meta data (e.g. from exif-data). 
        This works only when obj_input is a path string to the original file.
    resize: float, optional
        resize factor for the image (1 = 100%, 0.5 = 50%, 0.1 = 10% of 
        original size).
    save_suffix : str, optional
        suffix to append to filename of results files, if container is created
    kwargs: 
        developer options

    Returns
    -------
    ct: container
        A phenopype container is a Python class where loaded images, 
        dataframes, detected contours, intermediate output, etc. are stored 
        so that they are available for inspection or storage at the end of 
        the analysis. 
    image: ndarray
        original image (resized, if selected)
    df_image_data: DataFrame
        contains image data (+meta data), if selected

    """
    ## kwargs
    flag_df = df
    flag_meta = meta
    flag_mode = mode
    flag_container = cont
    
    ## load image
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            ext = os.path.splitext(obj_input)[1]
            if ext.replace(".", "") in default_filetypes:
                if flag_mode == "default":
                    image = cv2.imread(obj_input)
                elif flag_mode == "colour":
                    image = cv2.imread(obj_input, cv2.IMREAD_COLOR)
                elif flag_mode == "gray":
                    image = cv2.imread(obj_input, cv2.IMREAD_GRAYSCALE)     
            else:
                print("Invalid file extension \"{}\" - could not load image:\n".format(ext) \
                        + os.path.basename(obj_input))
                return
        else:
            print("Invalid image path - could not load image.")
            return
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
    else:
        print("Invalid input format - could not load image.")
        return


    ## load image data
    image_data = load_image_data(obj_input, path_and_type=False)
    df_image_data = pd.DataFrame(image_data, index=[0])


    ## check dirpath
    if flag_container == True:
        if dirpath == "cwd":
            dirpath = os.getcwd()
            if flag_verbose:
                print(
                    "Setting directory to save phenopype-container output to current working directory:\n" \
                    + os.path.abspath(dirpath)
                )
        elif dirpath.__class__.__name__ == "str":
            if not os.path.isdir(dirpath):
                user_input = input(
                    "Provided directory to save phenopype-container output {} does not exist - create?.".format(
                        os.path.abspath(dirpath)
                    )
                )
                if user_input in confirm_options:
                    os.makedirs(dirpath)
                else:
                    print("Directory not created - aborting")
                    return
            else:
                print("Directory to save phenopype-container output set at - " + os.path.abspath(dirpath))
        elif dirpath.__class__.__name__ == "NoneType":
            if obj_input.__class__.__name__ == "str":
                if os.path.isfile(obj_input):
                    dirpath = os.path.dirname(os.path.abspath(obj_input))
                    print("Directory to save phenopype-container output set to parent folder of image:\n{}".format(dirpath))
            else: 
                print(
                    "No directory provided to save phenopype-container output" +
                    " - provide dirpath or use dirpath==\"cwd\" to set save" +
                    " paths to current working directory - aborting."
                      )
                return
            
            
    ## create container
    if flag_container == True:
        ct = container(image, df_image_data)
        ct.image_data = image_data
        ct.dirpath = dirpath
        ct.save_suffix = save_suffix
            

    ## return
    if flag_container == True:
        return ct
    elif flag_container == False:
        if flag_df or flag_meta:
            return image, df_image_data
        else:
            return image


def load_image_data(obj_input, path_and_type=True, resize=1):
    """
    Create a DataFreame with image information (e.g. dimensions).

    Parameters
    ----------
    obj_input: str or ndarray
        can be a path to an image stored on the harddrive OR an array already 
        loaded to Python.
    path_and_type: bool, optional
        return image path and filetype to image_data dictionary

    Returns
    -------
    image_data: dict
        contains image data (+meta data, if selected)

    """
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            path = obj_input
        image = Image.open(path)
        width, height = image.size
        image.close()
        image_data = {
            "filename": os.path.split(obj_input)[1],
            "width": width,
            "height": height,
        }
        
        if path_and_type: 
            image_data.update({
                "filepath": obj_input,
                "filetype": os.path.splitext(obj_input)[1]})
            
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
        width, height = image.shape[0:2]
        image_data = {
            "filename": "unknown",
            "filepath": "unknown",
            "filetype": "ndarray",
            "width": width,
            "height": height,
        }
    else:
        warnings.warn("Not a valid image file - cannot read image data.")

    ## issue warnings for large images
    if width * height > 125000000:
        warnings.warn(
            "Large image - expect slow processing and consider \
                      resizing."
        )
    elif width * height > 250000000:
        warnings.warn(
            "Extremely large image - expect very slow processing \
                      and consider resizing."
        )

    ## return image data
    return image_data


def load_meta_data(image_path, show_fields=False, fields=default_meta_data_fields):
    """
    Extracts metadata (mostly Exif) from original image

    Parameters
    ----------
    image_path : str 
        path to image on harddrive
    show_fields: bool, optional
        show which exif data fields are available from given image
    fields: list or str
        which exif data fields should be extracted. default fields can be 
        modified in settings

    Returns
    -------
    exif_data: dict
        image meta data (exif)

    """
    ## kwargs
    flag_show = show_fields
    exif_fields = fields
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]

    # ## check if basic fields are present
    # if exif_fields.__class__.__name__ == "list":
    #     if not len(exif_fields) == 0:
    #         prepend = list(set(default_fields) - set(exif_fields))
    #         exif_fields = prepend + exif_fields

    ## read image
    if image_path.__class__.__name__ == "str":
        if os.path.isfile(image_path):
            image = Image.open(image_path)
        else:
            print("Not a valid image file - cannot read exif data.")
            return {}
    else:
        print("Not a valid image file - cannot read exif data.")
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
        print("no meta-data found")
        return None

    if flag_show:
        print("--------------------------------------------")
        print("Available exif-tags:\n")
        pretty.pprint(exif_data_all)
        print("\n")
        print('Default exif-tags (append list using "fields" argument):\n')
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



def load_directory(
    directory_path, cont=True, df=True, save_suffix=None, **kwargs
):
    """
    Parameters
    ----------
    directory_path: str or ndarray
        path to a phenopype project directory containing raw image, attributes 
        file, masks files, results df, etc.
    cont: bool, optional
        should the loaded image (and DataFrame) be returned as a phenopype 
        container
    df: bool, optional
        should a DataFrame containing image information (e.g. dimensions) 
        be returned.
    save_suffix : str, optional
        suffix to append to filename of results files
    kwargs: 
        developer options
        
    Returns
    -------
    container
        A phenopype container is a Python class where loaded images, 
        dataframes, detected contours, intermediate output, etc. are stored 
        so that they are available for inspection or storage at the end of 
        the analysis. 

    """
    ## kwargs
    flag_df = df
    flag_container = cont

    ## check if directory
    if not os.path.isdir(directory_path):
        print("Not a valid phenoype directory - cannot load files.")
        return
    
    ## check if attributes file and load otherwise
    if not os.path.join(directory_path, "attributes.yaml"):
        print("Attributes file missing - cannot load files.")
        return
    else:
        attributes = _load_yaml(os.path.join(directory_path, "attributes.yaml"))
    
    ## check if requires info is contained in attributes and load image
    if not "image_phenopype" in attributes or not "image_original" in attributes:
        print("Attributes doesn't contain required meta-data - cannot load files.")
        return 
    else:
        image_original = dict(attributes["image_original"])
        image_phenopype = dict(attributes["image_phenopype"])
        image_path = os.path.join(directory_path, image_phenopype["filename"])
        image = load_image(image_path, dirpath=directory_path)
    
    
    ## create image df
    df_image_dict = {
        "filename_original": image_original["filename"],
        "filename_phenopype": image_phenopype["filename"],
        "width": image_phenopype["width"],
        "height": image_phenopype["height"],            
        }
    
    if "resize" in image_phenopype:
        if image_phenopype["resize"] == True:
            df_image_dict.update({
                "resize": image_phenopype["resize"], 
                "resite_factor": image_phenopype["resize_factor"] })
    df_image_data = pd.DataFrame(df_image_dict, index=[0])
    
    ## return
    if flag_container == True:
        ct = container(image, df_image_data)
        ct.dirpath = directory_path
        ct.save_suffix = save_suffix

    if flag_container == True:
        return ct
    elif flag_container == False:
        if flag_df:
            return image, df_image_data
        else:
            return image



def show_image(
    image,
    max_dim=1200,
    position_reset=True,
    position_offset=25,
    window_aspect="free",
    check=True,
    **kwargs
):
    """
    Show one or multiple images by providing path string or array or list of 
    either.
    
    Parameters
    ----------
    image: array, list of arrays
        the image or list of images to be displayed. can be array-type, 
        or list or arrays
    max_dim: int, optional
        maximum dimension on either acis
    window_aspect: {"fixed", "free"} str, optional
        type of opencv window ("free" is resizeable)
    position_reset: bool, optional
        flag whether image positions should be reset when reopening list of 
        images
    position_offset: int, optional
        if image is list, the distance in pixels betweeen the positions of 
        each newly opened window (only works in conjunction with 
        "position_reset")
    check: bool, optional
        user input required when more than 10 images are opened at the same 
        time
    """
    ## kwargs
    flag_check = check
    test_params = kwargs.get("test_params", {})

    ## load image
    if image.__class__.__name__ == "ndarray":
        pass
    elif image.__class__.__name__ == "container":
        if not image.canvas.__class__.__name__ == "NoneType":
            image = copy.deepcopy(image.canvas)
        else:
            image = copy.deepcopy(image.image)
    elif image.__class__.__name__ == "list":
        pass
    else:
        print("wrong input format.")
        return

    ## select window type
    if window_aspect == "free":
        window_aspect = cv2.WINDOW_NORMAL
    elif window_aspect == "fixed":
        window_aspect = cv2.WINDOW_AUTOSIZE

    ## open images list or single images
    while True:
        if isinstance(image, list):
            if len(image) > 10 and flag_check == True:
                warning_string = (
                    "WARNING: trying to open "
                    + str(len(image))
                    + " images - proceed (y/n)?"
                )
                check = input(warning_string)
                if check in ["y", "Y", "yes", "Yes"]:
                    print("Proceed - Opening images ...")
                    pass
                else:
                    print("Aborting")
                    break
            idx = 0
            for i in image:
                idx += 1
                if i.__class__.__name__ == "ndarray":
                    _image_viewer(
                        i,
                        mode="",
                        window_aspect=window_aspect,
                        window_name="phenopype" + " - " + str(idx),
                        window_control="external",
                        max_dim=max_dim,
                        previous=test_params,
                    )
                    if position_reset == True:
                        cv2.moveWindow(
                            "phenopype" + " - " + str(idx),
                            idx + idx * position_offset,
                            idx + idx * position_offset,
                        )
                else:
                    print("skipped showing list item of type " + i.__class__.__name__)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break
        else:
            _image_viewer(
                image,
                mode="",
                window_aspect=window_aspect,
                window_name="phenopype",
                window_control="internal",
                max_dim=max_dim,
                previous=test_params,
            )
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break
        
        
        
def show_config_template(template):
    """
    
    Helper function to print phenopype configuration file in formatted yaml.

    Parameters
    ----------
    template : str
        name of pype configuration file to print (with or without ".yaml")

    Returns
    -------
    None

    """
    
    if not template.endswith(".yaml"):
        template_name = template + ".yaml"
    else:
        template_name = template
    if template_name in pype_config_templates:
        config_steps = _load_yaml(pype_config_templates[template_name])
        print("SHOWING BUILTIN PHENOPYPE TEMPLATE " + template_name + "\n\n")
        _show_yaml(config_steps)
        


def save_image(
    image,
    name,
    dirpath=os.getcwd(),
    resize=1,
    append="",
    extension="jpg",
    overwrite=False,
    **kwargs
):
    """Save an image (array) to jpg.
    
    Parameters
    ----------
    image: array
        image to save
    name: str
        name for saved image
    save_dir: str, optional
        directory to save image
    append: str, optional
        append image name with string to prevent overwriting
    extension: str, optional
        file extension to save image as
    overwrite: boo, optional
        overwrite images if name exists
    resize: float, optional
        resize factor for the image (1 = 100%, 0.5 = 50%, 0.1 = 10% of
        original size).
    kwargs: 
        developer options
    """

    ## kwargs
    flag_overwrite = overwrite

    # set dir and names
    # if "." in name:
    #     warnings.warn("need name and extension specified separately")
    #     return
    if append == "":
        append = ""
    else:
        append = "_" + append
    if "." not in extension:
        extension = "." + extension
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    ## resize
    if resize < 1:
        image = cv2.resize(
            image, (0, 0), fx=1 * resize, fy=1 * resize, interpolation=cv2.INTER_AREA
        )

    ## construct save path
    new_name = name + append + extension
    path = os.path.join(dirpath, new_name)

    ## save
    while True:
        if os.path.isfile(path) and flag_overwrite == False:
            print("Image not saved - file already exists (overwrite=False).")
            break
        elif os.path.isfile(path) and flag_overwrite == True:
            print("Image saved under " + path + " (overwritten).")
            pass
        elif not os.path.isfile(path):
            print("Image saved under " + path + ".")
            pass
        cv2.imwrite(path, image)
        break
