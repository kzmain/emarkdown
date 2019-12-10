import logging

from emarkdown.System.Tool import File
from emarkdown.Controller.ConverterController import ConverterController
from emarkdown.Controller.ExtractController import ExtractController
from emarkdown.System.Mode import Mode
from emarkdown.www.dark import Dark_HTML


def process(argv_list):
    mode_dict = Mode.get_modes(argv_list)
    if mode_dict[Mode.KEY_SYS_MODE] == Mode.MODE_PROCESSING:
        # Get resource file and destination file location
        res_uri = File.get_res_file_uri(argv_list)
        dest_uri = File.get_dest_file_uri(argv_list)
        # Extract input markdown files
        extractor = ExtractController()
        # @TODO Give documentation of return
        md_dict, unmd_dict, citations_dict = extractor.process(res_uri)
        # Convert extracted info into HTML
        # @TODO Give documentation of return
        html_text, menu_text, citations_text = ConverterController.process(md_dict, unmd_dict, citations_dict)
        if dest_uri is not None:
            export = open(dest_uri, "w+")
            export.write(Dark_HTML.FirstContent + html_text +
                         Dark_HTML.SecondContent + menu_text +
                         Dark_HTML.ThirdContent + citations_text + Dark_HTML.FourthContent)
            export.close()
        return html_text

    elif mode_dict[Mode.KEY_SYS_MODE] == Mode.MODE_CHANGE_LIB:
        pass
        # lib_uri = File.get_lib_uri(argv_list)
        # lib_dict = {"lib_loc": lib_uri}
        # lib_file = open(PathsConfig.LIB_CONFIG, "w+")
        # lib_file.write(json.dumps(lib_dict))
        # lib_file.close()
    else:
        logging.error("SYSTEM: No valid mode. exit!")
        exit(1)
