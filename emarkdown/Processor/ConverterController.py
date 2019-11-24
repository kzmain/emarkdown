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
        # basic_space_unit = 2
        main_text = md_dict[0][0][Config.KEY_TEXT]
        md_dict[0].pop(0)
        md_dict.pop(0)
        md_dict, menu_dict = self.update_md_dict(md_dict)
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
                            space_level = loop_count + level - 1
                            tag_text = re.sub("^", " " * space_level * self.basic_space_unit, tag_text,
                                              flags=re.MULTILINE)
                        if tag_type == TagTypes.TYPE_TABLE_TD or tag_type == TagTypes.TYPE_TABLE_TH:
                            tag_text = " " * self.basic_space_unit + tag_text
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

        menu = self.make_menu_html(menu_dict)
        citation = self.make_citation_html(citations_dict)
        return main_text, menu, citation

    def update_md_dict(self, input_dict):
        menu_dict = {}
        h1_name = ""
        h2_name = ""
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
                    tag_text = input_dict[level][t_uuid][Config.KEY_TEXT]
                    header_match = re.match(r"^<h\d", tag_type)
                    if tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                        tag_l = tag_dict[Config.KEY_SUB_TYPE] % tag_dict[Config.KEY_EXTENSION].lower() + "\n"
                        tag_r = "\n" + tag_l.split(" ")[0] + ">"
                        tag_r = tag_r.replace("<", "</")
                    # If header
                    elif header_match:
                        tag_l = tag_type % tag_text.lower().replace(" ", "-")
                        tag_r = tag_type[:header_match.end()] + ">"
                        tag_r = tag_r.replace("<", "</", 1).replace("\n", "")
                    if tag_type == TagTypes.TYPE_PARAGRAPH:
                        tag_text = tag_text.replace("\n", "<br />\n")
                        tag_text = re.sub("^", " " * self.basic_space_unit, tag_text, flags=re.MULTILINE)
                    tag_text = tag_l + tag_text + tag_r
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_text
                    if re.match(r"^<h1", tag_text):
                        h1_name = tag_text
                        if h1_name not in menu_dict.keys():
                            menu_dict[h1_name] = {}
                    elif re.match(r"^<h2", tag_text):
                        h2_name = tag_text
                        if h1_name not in menu_dict.keys():
                            menu_dict[h1_name] = {}
                        menu_dict[h1_name][h2_name] = {}
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
        return input_dict, menu_dict

    @staticmethod
    def update_unmd_dict(input_dict):
        for t_uuid, tag_dict in input_dict.items():
            if not tag_dict[Config.KEY_INLINE_FLAG]:
                if tag_dict[Config.KEY_SUB_TYPE] == TagTypes.TYPE_CODE_BLOCK:
                    tag_text = input_dict[t_uuid][Config.KEY_TEXT]
                    tag_text = tag_text \
                        .replace("<", HTML_Entities.ENTITY_DICT["<"]) \
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

    @staticmethod
    def make_menu_html(menu_dict):
        menu = "<ul>"
        for h1, h2s in menu_dict.items():
            id_match = re.search(r"(?<=id = \")((?!\")(.))*", h1)
            h1_id = h1[id_match.start(): id_match.end()]
            txt_match = re.search(r"(?<=\>)((?!<\/)(.))*", h1)
            h1_txt = h1[txt_match.start(): txt_match.end()]
            h1_href = "<a href=\"#%s\" title=\"\">%s</a>" % (h1_id, h1_txt)
            if len(h2s) == 0:

                menu = menu + "\n<li>" + h1_href + "</li>"
            else:
                menu = menu + "\n<li>\n<span class=\"opener active\">" + h1_href + "</span>\n<ul>"
                for h2, _ in h2s.items():
                    id_match = re.search(r"(?<=id = \")((?!\")(.))*", h2)
                    h2_id = h2[id_match.start(): id_match.end()]
                    txt_match = re.search(r"(?<=\>)((?!<\/)(.))*", h2)
                    h2_txt = h2[txt_match.start(): txt_match.end()]
                    h2_href = "<a href=\"#%s\" title=\"\">%s</a>" % (h2_id, h2_txt)
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
