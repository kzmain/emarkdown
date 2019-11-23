import copy
import pathlib
import re

from emarkdown.Processor.Config import TagConfig as Config, TagTypes
from emarkdown.Processor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.System import HTML_Entities


class ConverterController:
    def __init__(self):
        pass

    def process(self, md_dict, unmd_dict):
        main_text = md_dict[0][0][Config.KEY_TEXT]
        md_dict[0].pop(0)
        md_dict.pop(0)
        md_dict = self.update_md_dict(md_dict)
        unmd_dict = self.update_unmd_dict(unmd_dict)

        tp_dict = copy.deepcopy(md_dict)
        loop_count = -1
        while len(md_dict) > 0:
            md_dict = copy.deepcopy(tp_dict)
            loop_count += 1
            for level, tag_pairs in md_dict.items():
                for l_uuid, tag_dict in tag_pairs.items():
                    tag_text = tag_dict[Config.KEY_TEXT]
                    tag_inline = tag_dict[Config.KEY_INLINE_FLAG]
                    tag_type = tag_dict[Config.KEY_TYPE]
                    if l_uuid in main_text:
                        if not tag_inline:
                            space_num = loop_count + level - 1
                            tag_text = re.sub("^", " " * space_num * 2, tag_text, flags=re.MULTILINE)
                        if tag_type == TagTypes.TYPE_TABLE_TD or tag_type == TagTypes.TYPE_TABLE_TH:
                            tag_text = " " * 2 + tag_text
                        main_text = main_text.replace(l_uuid, tag_text)
                        tp_dict[level].pop(l_uuid)
                        if len(tp_dict[level]) == 0:
                            tp_dict.pop(level)

        tp_dict = copy.deepcopy(unmd_dict)
        while len(unmd_dict) > 0:
            unmd_dict = copy.deepcopy(tp_dict)
            for l_uuid, tag_text in unmd_dict.items():
                if l_uuid in main_text:
                    main_text = main_text.replace(l_uuid, tag_text)
                    tp_dict.pop(l_uuid)
        print()
        print()

    @staticmethod
    def update_md_dict(input_dict):
        for level, level_dict in input_dict.items():
            for t_uuid, tag_dict in level_dict.items():
                # Block
                if not tag_dict[Config.KEY_INLINE_FLAG]:

                    if tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_HEADER \
                            or tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_LIST:
                        input_dict[level][t_uuid][Config.KEY_TYPE] = input_dict[level][t_uuid][Config.KEY_SUB_TYPE]
                    elif tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_HORIZONTAL_RULE \
                            or tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_BREAK_LINE:
                        input_dict[level][t_uuid][Config.KEY_TEXT] = "\n" + input_dict[level][t_uuid][Config.KEY_TYPE]
                        continue

                    tag_type = tag_dict[Config.KEY_TYPE]
                    tag_l = tag_type + "\n"
                    tag_r = "\n" + tag_l.replace("<", "</", 1).replace("\n", "")
                    if tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                        tag_l = tag_dict[Config.KEY_SUB_TYPE] % tag_dict[Config.KEY_EXTENSION].lower() + "\n"
                        tag_r = "\n" + tag_l.split(" ")[0] + ">"
                    # If header
                    elif re.match("^<h", tag_type):
                        tag_l = tag_type
                        tag_r = tag_l.replace("<", "</", 1).replace("\n", "")
                    tag_text = input_dict[level][t_uuid][Config.KEY_TEXT]
                    if tag_type == TagTypes.TYPE_PARAGRAPH:
                        tag_text = tag_text.replace("\n", "<br />\n")
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_l + tag_text + tag_r

                # Inline
                else:
                    tag_text = input_dict[level][t_uuid][Config.KEY_TEXT]
                    tag_type = tag_dict[Config.KEY_TYPE]
                    tag_sub_type = tag_dict[Config.KEY_SUB_TYPE]
                    if tag_type == TagTypes.TYPE_LINK \
                            or tag_type == TagTypes.TYPE_IMAGE \
                            or tag_type == TagTypes.TYPE_VIDEO \
                            or tag_type == TagTypes.TYPE_AUDIO:
                        ext_dict = tag_dict[Config.KEY_EXTENSION]
                        link = ext_dict[MediaProcessor.KEY_LINK]
                        alt = ext_dict[MediaProcessor.KEY_ALT]
                        title = ext_dict[MediaProcessor.KEY_TITLE]
                        m_type = pathlib.Path(link).suffix.replace(".", "", 1)
                        if tag_type == TagTypes.TYPE_LINK:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_LINK % (link, title, tag_text)
                        elif tag_type == TagTypes.TYPE_IMAGE:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % (link, alt, title)
                        elif tag_type == TagTypes.TYPE_AUDIO:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % (link, m_type, alt, title)
                        elif tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_VIDEO:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % (link, m_type, alt, title)
                        continue
                    tag_l = tag_type
                    tag_r = tag_type.replace("<", "</", 1)
                    if tag_type == TagTypes.TYPE_LIST_LI:
                        tag_l = tag_type + "\n"
                        tag_r = "\n" + tag_r
                    tag_list = [x for x in tag_sub_type.split("<") if x != '']
                    if len(tag_list) > 0:
                        tag_list.reverse()
                        tag_l = tag_sub_type
                        tag_r = ""
                        for element in tag_list:
                            tag_r += "</" + element
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_l + tag_text + tag_r
        return input_dict

    @staticmethod
    def update_unmd_dict(input_dict):
        for t_uuid, tag_dict in input_dict.items():
            if not tag_dict[Config.KEY_INLINE_FLAG]:
                if tag_dict[Config.KEY_SUB_TYPE] == TagTypes.TYPE_CODE_BLOCK:
                    tag_text = input_dict[t_uuid][Config.KEY_TEXT]
                    tag_text = tag_text\
                        .replace("<", HTML_Entities.ENTITY_DICT["<"])\
                        .replace(">", HTML_Entities.ENTITY_DICT[">"])
                    extension = tag_dict[Config.KEY_EXTENSION].lower().strip()
                    if extension == "":
                        tag_l = "<pre lang=\"no-highlight\">\n<code>"
                        tag_r = "</code>\n</pre>"
                    else:
                        tag_l = "<div class=\"highlight highlight-source-%s\">\n<pre>" % extension
                        tag_r = "</pre>\n</div>"
                    input_dict[t_uuid] = tag_l + tag_text + tag_r
            else:
                tag_text = input_dict[t_uuid][Config.KEY_TEXT]
                tag_text = tag_text \
                    .replace("<", HTML_Entities.ENTITY_DICT["<"]) \
                    .replace(">", HTML_Entities.ENTITY_DICT[">"])
                tag_type = tag_dict[Config.KEY_TYPE]
                tag_sub_type = tag_dict[Config.KEY_SUB_TYPE]

                tag_l = tag_type
                tag_r = tag_type.replace("<", "</", 1)
                tag_list = [x for x in tag_sub_type.split("<") if x != '']
                if len(tag_list) > 0:
                    tag_list.reverse()
                    tag_l = tag_sub_type
                    tag_r = ""
                    for element in tag_list:
                        tag_r += "</" + element
                input_dict[t_uuid] = tag_l + tag_text + tag_r
        return input_dict
