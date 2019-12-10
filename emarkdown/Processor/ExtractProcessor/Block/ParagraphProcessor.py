import copy
import re

from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor
from emarkdown.System.Tool import UUID
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as con, TagTypes


# 只处理 start/block quote/symmetry block/li
class ParagraphProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_PARAGRAPH
    p_regx = UUID.get_regx_paragraph()

    def process_tag(self, md_dicts):
        tp_dict = copy.deepcopy(md_dicts)
        for level, level_dict in md_dicts.items():
            for uuid, tag_dict in level_dict.items():

                tag_type = tag_dict[con.KEY_TYPE]
                if tag_type == TagTypes.TYPE_LIST_LI or tag_type == TagTypes.TYPE_BLOCK_QUOTE \
                        or tag_type == TagTypes.TYPE_START or tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                    pass
                else:
                    continue

                in_text = tag_dict[con.KEY_TEXT]
                match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_text, None, self.p_regx, re.MULTILINE)
                while match:
                    m_txt = re.sub("^\n", "", m_txt, 1)
                    new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, "", False, "")
                    tp_dict = self.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)

                    in_text = b_txt + new_uuid + a_txt
                    tp_dict[level][uuid][con.KEY_TEXT] = in_text

                    match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_text, None, self.p_regx, re.MULTILINE)
        return tp_dict
