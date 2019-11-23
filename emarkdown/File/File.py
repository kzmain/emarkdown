import logging
import os
import re
from glob import glob
from pathlib import Path

from emarkdown.Exceptions.FileException import InputFileTypeNotCorrectError, FileAccessModeNotCorrectError
from emarkdown.System import Parameter


def update_user_home_folder(uri):
    # match ~ user location
    user_home_match = re.match("~", uri)
    if user_home_match:
        uri = uri.replace("~", os.path.expanduser('~'), 1)
    return uri


def update_user_current_folder(uri):
    # match . user location
    user_current_folder_match = re.match(r"\.", uri)
    if user_current_folder_match:
        uri = uri.replace(".", os.getcwd(), 1)
    res_name = str(Path(uri).name)
    if res_name == uri:
        uri = os.getcwd() + "/" + res_name
    return uri


def check_file_type(uri, file_type):
    # Check if .md file
    if file_type not in uri:
        return False
    return True


def check_file_read_mode(uri):
    if not os.path.isfile(uri):
        return False
    if not os.access(uri, os.R_OK):
        raise False
    return True


def check_file_write_mode(uri):
    if not os.access(Path(uri).parent, os.W_OK):
        raise False
    return True


def check_folder_write_mode(uri):
    if not os.path.isdir(uri):
        return False
    if not os.access(uri, os.W_OK):
        raise False
    return True

def check_folder_read_mode(uri):
    if not os.path.isdir(uri):
        return False
    if not os.access(uri, os.R_OK):
        raise False
    return True


def get_res_file_uri(argv_list):
    res_uri = ""
    try:
        if Parameter.SIGNAL_RES_FILE not in argv_list: raise FileNotFoundError
        res_uri_index = argv_list.index(Parameter.SIGNAL_RES_FILE) + 1
        res_uri = argv_list[res_uri_index]

        res_uri = update_user_home_folder(res_uri)
        res_uri = update_user_current_folder(res_uri)

        if not check_file_type(res_uri, ".md"): raise InputFileTypeNotCorrectError
        if not check_file_read_mode(res_uri): raise FileAccessModeNotCorrectError

        return res_uri
    except IndexError:
        logging.error("Correct input .md file name is required.")
        exit(1)
    except FileNotFoundError:
        logging.error("Input file \"%s\" cannot be found." % res_uri)
        exit(1)
    except InputFileTypeNotCorrectError:
        logging.error("Input file \"%s\"'s file type is not accepted." % res_uri)
        exit(1)
    except FileAccessModeNotCorrectError:
        logging.error("Input file \"%s\"'s access mode is not accepted." % res_uri)
        exit(1)


def get_dest_file_uri(argv_list):
    dest_uri = ""
    try:
        if Parameter.SIGNAL_DEST_FILE not in argv_list:
            raise FileNotFoundError
        file_location_index = argv_list.index(Parameter.SIGNAL_DEST_FILE) + 1
        dest_uri = argv_list[file_location_index]

        dest_uri = update_user_home_folder(dest_uri)
        dest_uri = update_user_current_folder(dest_uri)

        res_uri_index = argv_list.index(Parameter.SIGNAL_RES_FILE) + 1
        res_uri = argv_list[res_uri_index]

        res_file_name = Path(res_uri)
        res_file_name = str(res_file_name.name).replace(".md", ".html")

        # If destination uri is a directory
        if Path(dest_uri).is_dir():
            if not check_folder_write_mode(dest_uri): raise FileAccessModeNotCorrectError
            dest_uri + "/" + res_file_name
        # If destination uri is a file
        else:
            if not check_file_type(dest_uri, ".html"): raise InputFileTypeNotCorrectError
            if not check_file_write_mode(dest_uri): raise FileAccessModeNotCorrectError
        return dest_uri
    except IndexError:
        logging.error("Destination location is required.")
        return None
    except FileNotFoundError:
        logging.error("Destination location \"%s\" cannot be found." % dest_uri)
        return None
    except InputFileTypeNotCorrectError:
        logging.error("Destination location \"%s\" is not accepted." % dest_uri)
        return None
    except FileAccessModeNotCorrectError:
        logging.error("Destination \"%s\" is not writable." % dest_uri)
        return None


def get_lib_uri(argv_list):
    lib_uri = ""
    try:
        lib_uri_index = argv_list.index(Parameter.SIGNAL_CHANGE_LIB) + 1
        res_uri = argv_list[lib_uri_index]
        libs_raw = glob('./www/*/')
        libs_dict = {}
        for lib_raw in libs_raw:
            libs_dict[Path(lib_raw).name] = lib_raw
        if res_uri in libs_dict.keys():
            lib_uri = libs_dict[res_uri]
        lib_uri = update_user_current_folder(lib_uri)
        lib_uri = update_user_home_folder(lib_uri)
        if not check_folder_read_mode(lib_uri): raise FileNotFoundError
    except IndexError:
        logging.error("Did not enter CSS/JS libraries is entered.")
        exit(1)
    except FileNotFoundError:
        logging.error("No correct CSS/JS libraries is entered.")
        exit(1)
    return lib_uri
