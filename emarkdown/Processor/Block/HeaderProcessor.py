import copy
import re
from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.Processor.Block.TableProcessor import TableProcessor
from emarkdown.Processor.Config import TagConfig as Config, TagTypes


class HeaderProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_HEADER
    # Type 1
    regx1 = r"((?<=\n)|(?<!\W|\w))^( )*((#){1,6})( +)((?!\n)(\w|\W))*"
    # Type 2
    regx2 = r"(\w|(?!\n)\W)+\n((-){3,}|(=){3,})$"

    # 在block里面都可以处理header，除了List和Table
    def process_tag(self, md_dict):
        tp_dict = copy.deepcopy(md_dict)
        for level, level_dict in md_dict.items():
            for uuid, tag_dict in level_dict.items():
                # Filter
                tag_type = tag_dict[Config.KEY_TYPE]
                tag_inline = tag_dict[Config.KEY_INLINE_FLAG]
                if not tag_inline and TableProcessor.tag_name != tag_type and HeaderProcessor.tag_name != tag_type:
                    pass
                else:
                    continue
                # Start process
                in_txt = tag_dict[Config.KEY_TEXT]
                in_txt, tp_dict, md_dict = self.__process_head(in_txt, level, uuid, self.regx1, 1, tp_dict, md_dict)
                in_txt, tp_dict, md_dict = self.__process_head(in_txt, level, uuid, self.regx2, 2, tp_dict, md_dict)
        return tp_dict

    def __process_head(self, in_txt, in_level, in_uuid, in_regx, in_type, tp_dict, md_dict):
        match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, in_regx, re.MULTILINE)
        while match:
            m_txt, exact_type = self.__get_exact_type(m_txt, in_type)

            new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, exact_type, False, "")
            tp_dict = self.insert_tag_md_dict(tp_dict, in_level, new_uuid, new_dict)

            in_txt = b_txt + new_uuid + a_txt
            tp_dict[in_level][in_uuid][Config.KEY_TEXT] = in_txt
            md_dict[in_level][in_uuid][Config.KEY_TEXT] = in_txt

            match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, in_regx, re.MULTILINE)
        return in_txt, tp_dict, md_dict

    @staticmethod
    def __get_exact_type(m_txt, in_type):
        exact_type = ""
        if in_type == 1:
            type_match = re.search("#{1,6}( )*", m_txt)
            number_sign = m_txt[type_match.start():type_match.end()].replace(" ", "")
            exact_type = "<h" + str(len(number_sign)) + " id = \"%s\">"
            m_txt = m_txt[type_match.end():]
        elif in_type == 2:
            match_text_list = m_txt.split("\n")
            heading_type = str(1) if "=" in match_text_list[1] else str(2)
            exact_type = "<h" + heading_type + " id = \"%s\">"
            m_txt = match_text_list[0]
        return m_txt, exact_type
