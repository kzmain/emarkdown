# ---------------------------------------------------------------------------------------------------------------
import logging
from emd.System import Parameter
# MODE TYPES-----------------------------------------------------------------------------------------------------
MODE_PROCESSING = "PROCESSING_MODE"
MODE_CHANGE_LIB = "CHANGE_LIB_MODE"

# MODE DICTIONARY------------------------------------------------------------------------------------------------
KEY_SYS_MODE = "SYS_MODE"
KEY_HTML_MODE = "HTML_MODE"
KEY_MARKDOWN_MODE = "MARKDOWN_MODE"
# ---------------------------------------------------------------------------------------------------------------


def get_modes(argv_list):
    modes = {KEY_SYS_MODE: "", KEY_MARKDOWN_MODE: "", KEY_HTML_MODE: ""}
    if Parameter.SIGNAL_RES_FILE in argv_list and Parameter.SIGNAL_DEST_FILE in argv_list:
        modes[KEY_SYS_MODE] = MODE_PROCESSING
        modes[KEY_HTML_MODE] = Parameter.MODE_ALL_WEB_TECH
        modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_E_MARKDOWN
        # -------------------------------------------------------------------------------------------------------
        if Parameter.MODE_PURE_HTML in argv_list:
            modes[KEY_HTML_MODE] = Parameter.MODE_PURE_HTML
        elif Parameter.MODE_ALL_WEB_TECH in argv_list:
            modes[KEY_HTML_MODE] = Parameter.MODE_ALL_WEB_TECH
        # -------------------------------------------------------------------------------------------------------
        if Parameter.SIGNAL_PURE_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_PURE_MARKDOWN
        elif Parameter.SIGNAL_E_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_E_MARKDOWN
        elif Parameter.SIGNAL_HTML_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_HTML_MARKDOWN
        # -------------------------------------------------------------------------------------------------------
    elif Parameter.SIGNAL_CHANGE_LIB:
        modes[KEY_SYS_MODE] = MODE_CHANGE_LIB
    else:
        logging.error("SYSTEM: No valid mode. exit!")
        exit(1)
    return modes
