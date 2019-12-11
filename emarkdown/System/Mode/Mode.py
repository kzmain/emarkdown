# ---------------------------------------------------------------------------------------------------------------
from emarkdown.System.Mode import Parameter
from emarkdown.System.Tool.Logger import Logger

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
    if Parameter.SIGNAL_R_FILE in argv_list:
        modes[KEY_SYS_MODE] = MODE_PROCESSING
        modes[KEY_HTML_MODE] = Parameter.SIGNAL_L_HTML
        modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_E_MARKDOWN
        # -------------------------------------------------------------------------------------------------------
        if Parameter.SIGNAL_P_HTML in argv_list:
            modes[KEY_HTML_MODE] = Parameter.SIGNAL_P_HTML
        elif Parameter.SIGNAL_L_HTML in argv_list:
            modes[KEY_HTML_MODE] = Parameter.SIGNAL_L_HTML
        # -------------------------------------------------------------------------------------------------------
        if Parameter.SIGNAL_P_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_P_MARKDOWN
        elif Parameter.SIGNAL_E_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_E_MARKDOWN
        elif Parameter.SIGNAL_H_MARKDOWN in argv_list:
            modes[KEY_MARKDOWN_MODE] = Parameter.SIGNAL_H_MARKDOWN
        # -------------------------------------------------------------------------------------------------------
    elif Parameter.SIGNAL_CHANGE_LIB:
        modes[KEY_SYS_MODE] = MODE_CHANGE_LIB
    else:
        Logger.error_logger("No valid mode for emarkdown module. Exit!")
        exit(1)
    return modes
