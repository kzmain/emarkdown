import json
import re
import os
import logging

from emarkdown.File import File, Paths
from emarkdown.Processor.ConverterController import ConverterController
from emarkdown.Processor.ExtractController import ExtractController
from emarkdown.System import Mode


def process(argv_list):
    mode_dict = Mode.get_modes(argv_list)
    if mode_dict[Mode.KEY_SYS_MODE] == Mode.MODE_PROCESSING:
        res_uri = File.get_res_file_uri(argv_list)
        dest_uri = File.get_dest_file_uri(argv_list)
        extractor = ExtractController()
        md_dict, unmd_dict, citations_dict = extractor.process(res_uri)
        converter = ConverterController()
        html_text = converter.process(md_dict, unmd_dict)
        if dest_uri is not None:
            export = open(dest_uri, "w+")
            export.write(html_text)
            export.close()
        return html_text

    elif mode_dict[Mode.KEY_SYS_MODE] == Mode.MODE_CHANGE_LIB:
        lib_uri = File.get_lib_uri(argv_list)
        lib_dict = {"lib_loc": lib_uri}
        lib_file = open(Paths.LIB_CONFIG, "w+")
        lib_file.write(json.dumps(lib_dict))
        lib_file.close()
    else:
        logging.error("SYSTEM: No valid mode. exit!")
        exit(1)
