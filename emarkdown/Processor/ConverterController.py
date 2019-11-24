import copy
import pathlib
import re

from emarkdown.Processor.Config import TagConfig as Config, TagTypes
from emarkdown.Processor.Inline.CitationProcessor import CitationProcessor
from emarkdown.Processor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.System import HTML_Entities


class ConverterController:
    basic_space_unit = 2

    def __init__(self):
        pass

    def process(self, md_dict, unmd_dict, citations_dict):
        main_text = md_dict[0][0][Config.KEY_TEXT]
        md_dict[0].pop(0)
        md_dict.pop(0)

        md_dict, menu_dict = ConverterController.update_md_dict(md_dict)
        unmd_dict = ConverterController.update_unmd_dict(unmd_dict)

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
                            space_level = loop_count + level - 1
                            tag_text = re.sub("^", " " * space_level * ConverterController.basic_space_unit, tag_text,
                                              flags=re.MULTILINE)
                        if tag_type == TagTypes.TYPE_TABLE_TD or tag_type == TagTypes.TYPE_TABLE_TH:
                            tag_text = " " * ConverterController.basic_space_unit + tag_text
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

        menu = ConverterController.make_menu_html(menu_dict)
        citation = ConverterController.make_citation_html(citations_dict)
        return main_text, menu, citation

    @staticmethod
    def update_md_dict(input_dict):
        menu_dict = {}
        h1_name = ""
        for level, level_dict in input_dict.items():
            for t_uuid, tag_dict in level_dict.items():
                # Block Type
                if not tag_dict[Config.KEY_INLINE_FLAG]:
                    tag_type = tag_dict[Config.KEY_TYPE]
                    tag_sub_type = tag_dict[Config.KEY_SUB_TYPE]
                    # Preprocess
                    if tag_type == TagTypes.TYPE_HEADER or tag_type == TagTypes.TYPE_LIST:
                        input_dict[level][t_uuid][Config.KEY_TYPE] = tag_sub_type
                    elif tag_type == TagTypes.TYPE_HORIZONTAL_RULE or tag_type == TagTypes.TYPE_BREAK_LINE:
                        input_dict[level][t_uuid][Config.KEY_TEXT] = "\n" + tag_type
                        continue
                    # Prepare for process
                    tag_type = tag_dict[Config.KEY_TYPE]
                    tag_text = tag_dict[Config.KEY_TEXT].replace("\n", "<br />\n")
                    # Process
                    tag_l = ConverterController.generate_left_tag(tag_type, False)
                    tag_r = ConverterController.generate_right_tag(tag_type, False)

                    header_match = re.match(r"^<h\d", tag_type)
                    # If <div>...</div>'s tag
                    if tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                        tag_type = tag_dict[Config.KEY_SUB_TYPE] % tag_dict[Config.KEY_EXTENSION].lower()
                        tag_l = ConverterController.generate_left_tag(tag_type, False)
                        tag_r = ConverterController.generate_right_tag(tag_type, False)
                    # If <h1>, <h2>, <h3>, <h4>, <h5>, <h6>'s tag
                    elif header_match:
                        tag_type = tag_type % tag_text.lower().replace(" ", "-")
                        tag_l = ConverterController.generate_left_tag(tag_type, True)
                        tag_r = ConverterController.generate_right_tag(tag_type, True)
                    # If <p> tag
                    if tag_type == TagTypes.TYPE_PARAGRAPH:
                        tag_text = re.sub("^", " " * ConverterController.basic_space_unit, tag_text, flags=re.MULTILINE)

                    tag_text = tag_l + tag_text + tag_r
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_text
                    # Update citations
                    if re.match(r"^<h1", tag_text):
                        h1_name = tag_text
                        if h1_name not in menu_dict.keys():
                            menu_dict[h1_name] = {}
                    elif re.match(r"^<h2", tag_text):
                        h2_name = tag_text
                        if h1_name not in menu_dict.keys():
                            menu_dict[h1_name] = {}
                        menu_dict[h1_name][h2_name] = {}
                # Inline Type
                else:
                    tag_text = tag_dict[Config.KEY_TEXT].replace("\n", "<br />\n")
                    tag_type = tag_dict[Config.KEY_TYPE]
                    tag_sub_type = tag_dict[Config.KEY_SUB_TYPE]
                    # If Media types, different from others, process => continue
                    if tag_type == TagTypes.TYPE_LINK or tag_type == TagTypes.TYPE_IMAGE \
                            or tag_type == TagTypes.TYPE_VIDEO or tag_type == TagTypes.TYPE_AUDIO:
                        ext_dict = tag_dict[Config.KEY_EXTENSION]
                        link = ext_dict[MediaProcessor.KEY_LINK]
                        alt = ext_dict[MediaProcessor.KEY_ALT]
                        title = ext_dict[MediaProcessor.KEY_TITLE]
                        m_type = pathlib.Path(link).suffix.replace(".", "", 1)
                        if tag_type == TagTypes.TYPE_LINK:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_LINK % \
                                                                         (link, title, tag_text)
                        elif tag_type == TagTypes.TYPE_IMAGE:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % \
                                                                         (link, alt, title)
                        elif tag_type == TagTypes.TYPE_AUDIO:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % \
                                                                         (link, m_type, alt, title)
                        elif tag_dict[Config.KEY_TYPE] == TagTypes.TYPE_VIDEO:
                            input_dict[level][t_uuid][Config.KEY_TEXT] = TagTypes.TYPE_IMAGE % \
                                                                         (link, m_type, alt, title)
                        continue
                    # Process
                    tag_l = ConverterController.generate_left_tag(tag_type)
                    tag_r = ConverterController.generate_right_tag(tag_type)
                    is_symmetry = True if len([x for x in tag_sub_type.split("<") if x != '']) > 0 else False
                    if is_symmetry > 0:
                        tag_l = ConverterController.generate_left_tag(tag_sub_type, True)
                        tag_r = ConverterController.generate_right_tag(tag_sub_type, True)
                    elif tag_type == TagTypes.TYPE_LIST_LI:
                        tag_l = ConverterController.generate_left_tag(tag_type, False)
                        tag_r = ConverterController.generate_right_tag(tag_type, False)
                    tag_text = tag_l + tag_text + tag_r
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_text
        return input_dict, menu_dict

    @staticmethod
    def update_unmd_dict(input_dict):
        for t_uuid, tag_dict in input_dict.items():
            tag_text = input_dict[t_uuid][Config.KEY_TEXT]
            tag_text = tag_text \
                .replace("<", HTML_Entities.ENTITY_DICT["<"]) \
                .replace(">", HTML_Entities.ENTITY_DICT[">"])
            if not tag_dict[Config.KEY_INLINE_FLAG]:
                if tag_dict[Config.KEY_SUB_TYPE] == TagTypes.TYPE_CODE_BLOCK:
                    extension = tag_dict[Config.KEY_EXTENSION].lower().strip()
                    if extension == "":
                        tag_l = "<pre lang=\"no-highlight\">\n<code>"
                        tag_r = "</code>\n</pre>"
                    else:
                        tag_l = "<div class=\"highlight highlight-source-%s\">\n<pre>" % extension
                        tag_r = "</pre>\n</div>"
                    input_dict[t_uuid] = tag_l + tag_text + tag_r
            else:
                tag_type = tag_dict[Config.KEY_TYPE]
                tag_sub_type = tag_dict[Config.KEY_SUB_TYPE]

                tag_l = ConverterController.generate_left_tag(tag_type)
                tag_r = ConverterController.generate_right_tag(tag_type)
                is_symmetry = True if len([x for x in tag_sub_type.split("<") if x != '']) > 0 else False
                if is_symmetry > 0:
                    tag_l = ConverterController.generate_left_tag(tag_sub_type, True)
                    tag_r = ConverterController.generate_right_tag(tag_sub_type, True)
                input_dict[t_uuid] = tag_l + tag_text + tag_r
        return input_dict

    @staticmethod
    def head_to_href(head):
        id_match = re.search(r"(?<=id = \")((?!\")(.))*", head)
        h_id = head[id_match.start(): id_match.end()]
        txt_match = re.search(r"(?<=>)((?!</)(.))*", head)
        h_txt = head[txt_match.start(): txt_match.end()]
        h_href = "<a href=\"#%s\" title=\"\">%s</a>" % (h_id, h_txt)
        return h_href

    @staticmethod
    def make_menu_html(menu_dict):
        menu = "<ul>"
        for h1, h2s in menu_dict.items():
            h1_href = ConverterController.head_to_href(h1)
            if len(h2s) == 0:
                menu = menu + "\n<li>" + h1_href + "</li>"
            else:
                menu = menu + "\n<li>\n<span class=\"opener active\">" + h1_href + "</span>\n<ul>"
                for h2, _ in h2s.items():
                    h2_href = ConverterController.head_to_href(h2)
                    menu = menu + "\n<li>" + h2_href + "</li>"
                menu = menu + "\n</ul>" + "\n</li>"
        menu = menu + "\n</ul>"
        return menu

    @staticmethod
    def make_citation_html(citations_dict):
        if len(citations_dict) == 0:
            return ""
        citations = "<ol>"
        for _, c_dict in citations_dict.items():
            if CitationProcessor.VALUE_TYPE_WEB != c_dict[CitationProcessor.KEY_TYPE]:
                citations += "\n<li>%s. (%s). <i>%s</i>. %s, pp.%s. [Access Date: %s].</li>" % \
                             (c_dict[CitationProcessor.KEY_AUTHOR], c_dict[CitationProcessor.KEY_DATE_PUBLISH],
                              c_dict[CitationProcessor.KEY_TITLE], c_dict[CitationProcessor.KEY_EDITION],
                              c_dict[CitationProcessor.KEY_PAGE], c_dict[CitationProcessor.KEY_DATE_ACCESS])
            else:
                if CitationProcessor.KEY_URL not in c_dict:
                    c_dict[CitationProcessor.KEY_URL] = ""
                citations += "<li>\n%s. (%s). <i>%s</i>[online]. %s, pp.%s. Available at: %s [Accessed %s].</li>" % \
                             (c_dict[CitationProcessor.KEY_AUTHOR], c_dict[CitationProcessor.KEY_DATE_PUBLISH],
                              c_dict[CitationProcessor.KEY_TITLE], c_dict[CitationProcessor.KEY_EDITION],
                              c_dict[CitationProcessor.KEY_PAGE], c_dict[CitationProcessor.KEY_URL],
                              c_dict[CitationProcessor.KEY_DATE_ACCESS])
        citations += "</ol>"
        return citations

    @staticmethod
    def generate_right_tag(tag_type, is_inline=True):
        tag_list = [x.replace("<", "</", 1) for x in tag_type.split(">") if x != '']

        if len(tag_list) > 0:
            tag_list.reverse()
            tag_r = ""
            for element in tag_list:
                tag_r += element.split(" ")[0] + ">"
            if is_inline:
                return tag_r
            else:
                return "\n" + tag_r
        else:
            tag_r = tag_type.replace("<", "</")
            return tag_r

    @staticmethod
    def generate_left_tag(tag_type, is_inline=True):
        tag_l = tag_type
        if is_inline:
            return tag_l
        else:
            return tag_l + "\n"
