import copy
import pathlib
import re

from bs4 import BeautifulSoup

from emarkdown.Processor.ExtractProcessor.Config import TagConfig as Config, TagTypes
from emarkdown.Processor.ExtractProcessor.Inline.CitationProcessor import CitationProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.System.Tool import HTML_Entities


class ConverterController:
    BASIC_SPACE_NUM = 2

    def __init__(self):
        pass

    @staticmethod
    def process(md_dict, unmd_dict, citations_dict):
        main_text = md_dict[0][0][Config.KEY_TEXT]
        md_dict[0].pop(0)
        md_dict.pop(0)

        md_dict = ConverterController.__update_md_dict(md_dict)
        unmd_dict = ConverterController.__update_unmd_dict(unmd_dict)

        main_text = ConverterController.__md_dict_to_main_text(md_dict, main_text)
        main_text = ConverterController.__unmd_dict_to_main_text(unmd_dict, main_text)

        menu = ConverterController.__make_menu_html(main_text)
        citation = ConverterController.__make_citation_html(citations_dict)



        return main_text, menu, citation

    @staticmethod
    def __md_dict_to_main_text(md_dict, main_text):
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
                            tag_text = re.sub("^", " " * space_level * ConverterController.BASIC_SPACE_NUM, tag_text,
                                              flags=re.MULTILINE)
                        if tag_type == TagTypes.TYPE_TABLE_TD or tag_type == TagTypes.TYPE_TABLE_TH:
                            space_level = loop_count + level - 1
                            tag_text = " " * space_level * ConverterController.BASIC_SPACE_NUM + tag_text
                        main_text = main_text.replace(l_uuid, tag_text)
                        tp_dict[level].pop(l_uuid)
                        if len(tp_dict[level]) == 0:
                            tp_dict.pop(level)
        return main_text

    @staticmethod
    def __unmd_dict_to_main_text(unmd_dict, main_text):
        tp_dict = copy.deepcopy(unmd_dict)
        while len(unmd_dict) > 0:
            unmd_dict = copy.deepcopy(tp_dict)
            for l_uuid, tag_text in unmd_dict.items():
                if l_uuid in main_text:
                    main_text = main_text.replace(l_uuid, tag_text)
                    tp_dict.pop(l_uuid)
        return main_text

    @staticmethod
    def __update_md_dict(input_dict):
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
                    tag_text = tag_dict[Config.KEY_TEXT]
                    # Process
                    tag_l = ConverterController.__generate_left_tag(tag_type, False)
                    tag_r = ConverterController.__generate_right_tag(tag_type, False)

                    header_match = re.match(r"^<h\d", tag_type)
                    # If <div>...</div>'s tag
                    if tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                        tag_type = tag_dict[Config.KEY_SUB_TYPE] % tag_dict[Config.KEY_EXTENSION].lower()
                        tag_l = ConverterController.__generate_left_tag(tag_type, False)
                        tag_r = ConverterController.__generate_right_tag(tag_type, False)
                    # If <h1>, <h2>, <h3>, <h4>, <h5>, <h6>'s tag
                    elif header_match:
                        tag_type = tag_type % tag_text.lower().replace(" ", "-")
                        tag_l = ConverterController.__generate_left_tag(tag_type, True)
                        tag_r = ConverterController.__generate_right_tag(tag_type, True)
                    # If <p> tag
                    if tag_type == TagTypes.TYPE_PARAGRAPH:
                        tag_text = re.sub("^", " " * ConverterController.BASIC_SPACE_NUM, tag_text, flags=re.MULTILINE)

                    tag_text = tag_l + tag_text + tag_r
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_text
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
                    tag_l = ConverterController.__generate_left_tag(tag_type)
                    tag_r = ConverterController.__generate_right_tag(tag_type)
                    is_symmetry = True if len([x for x in tag_sub_type.split("<") if x != '']) > 0 else False
                    if is_symmetry > 0:
                        tag_l = ConverterController.__generate_left_tag(tag_sub_type, True)
                        tag_r = ConverterController.__generate_right_tag(tag_sub_type, True)
                    elif tag_type == TagTypes.TYPE_LIST_LI:
                        tag_l = ConverterController.__generate_left_tag(tag_type, False)
                        tag_r = ConverterController.__generate_right_tag(tag_type, False)
                    tag_text = tag_l + tag_text + tag_r
                    input_dict[level][t_uuid][Config.KEY_TEXT] = tag_text
        return input_dict

    @staticmethod
    def __update_unmd_dict(input_dict):
        for t_uuid, tag_dict in input_dict.items():
            tag_text = input_dict[t_uuid][Config.KEY_TEXT]
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

                tag_l = ConverterController.__generate_left_tag(tag_type)
                tag_r = ConverterController.__generate_right_tag(tag_type)
                is_symmetry = True if len([x for x in tag_sub_type.split("<") if x != '']) > 0 else False
                if is_symmetry > 0:
                    tag_l = ConverterController.__generate_left_tag(tag_sub_type, True)
                    tag_r = ConverterController.__generate_right_tag(tag_sub_type, True)
                input_dict[t_uuid] = tag_l + tag_text + tag_r
        return input_dict

    @staticmethod
    def __head_to_href(tag_id, tag__txt):
        h_href = "<a href=\"#%s\" title=\"\">%s</a>" % (tag_id, tag__txt)
        return h_href

    @staticmethod
    def __make_menu_html(main_text):
        menu = "<ul>"
        soup = BeautifulSoup(main_text, features="html5lib")
        tags = soup.findAll(re.compile(r'(h1|h2)'))
        has_h1 = False
        for count in range(len(tags)):
            c_tag = str(tags[count])
            tag_id = tags[count].attrs["id"]\
                .replace("\"", HTML_Entities.ENTITY_DICT["\""])\
                .replace("\'", HTML_Entities.ENTITY_DICT["\'"])
            tag_txt = tags[count].contents[0]\
                .replace("\"", HTML_Entities.ENTITY_DICT["\""])\
                .replace("\'", HTML_Entities.ENTITY_DICT["\'"])
            if count < len(tags) - 1:
                n_tag = str(tags[count + 1])
            else:
                n_tag = "<h1></h1>"
            if not has_h1:
                c_tag = c_tag.replace("h2", "h1")
            href = ConverterController.__head_to_href(tag_id, tag_txt)
            if "<h1" in c_tag:
                has_h1 = True
                if "<h1" in n_tag:
                    menu = menu + "\n<li>" + href + "</li>"
                else:
                    menu = menu + "\n<li>\n<span class=\"opener active\">" + href + "</span>\n<ul>"
            else:
                menu = menu + "\n<li>" + href + "</li>"
                if "<h1" in n_tag:
                    menu = menu + "\n</ul>" + "\n</li>"
        menu = menu + "\n</ul>"
        return menu

    @staticmethod
    def __make_citation_html(citations_dict):
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
    def __generate_right_tag(tag_type, is_inline=True):
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
    def __generate_left_tag(tag_type, is_inline=True):
        tag_l = tag_type
        if is_inline:
            return tag_l
        else:
            return tag_l + "\n"
