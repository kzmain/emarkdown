import copy
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.System import UUID
from emarkdown.Processor.Config import TagConfig as con, TagTypes


# 只处理 start/block quote/symmetry block/li
class ParagraphProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_PARAGRAPH
    paragraph_regx = UUID.get_regx_paragraph()

    def process_tag(self, md_dicts):
        tp_dicts = copy.deepcopy(md_dicts)
        for level, level_dict in md_dicts.items():
            for l_uuid, l_tag_dict in level_dict.items():
                in_text = l_tag_dict[con.KEY_TEXT]
                p_match = re.search(self.paragraph_regx, in_text, re.MULTILINE)

                tag_type = l_tag_dict[con.KEY_TYPE]
                if tag_type == TagTypes.TYPE_LIST_LI \
                        or tag_type == TagTypes.TYPE_BLOCK_QUOTE \
                        or tag_type == TagTypes.TYPE_START \
                        or tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                    while p_match:
                        p_text = in_text[p_match.start(): p_match.end()]
                        p_text = re.sub("^\n", "", p_text)
                        before_text = in_text[: p_match.start()]
                        after_text = in_text[p_match.end():]

                        p_text = re.sub("^\n", "", p_text, 1)

                        # Replace
                        new_insert_dict = copy.deepcopy(con.insert_dict)
                        new_uuid = UUID.get_new_uuid()
                        new_insert_dict[con.KEY_UUID] = new_uuid
                        new_insert_dict[con.KEY_EXTENSION] = ""
                        new_insert_dict[con.KEY_INLINE_FLAG] = False
                        new_insert_dict[con.KEY_TEXT] = p_text
                        new_insert_dict[con.KEY_TYPE] = self.tag_name

                        store_level = level + 1
                        if store_level not in tp_dicts:
                            tp_dicts[store_level] = {}
                        tp_dicts[store_level][new_uuid] = new_insert_dict

                        in_text = before_text + new_uuid + after_text
                        tp_dicts[level][l_uuid][con.KEY_TEXT] = in_text

                        p_match = re.search(self.paragraph_regx, in_text, re.MULTILINE)
        return tp_dicts
