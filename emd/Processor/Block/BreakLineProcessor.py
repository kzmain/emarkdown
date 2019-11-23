import copy
import re

from emd.Processor.BasicProcessor import BasicProcessor
from emd.Processor.Config import TagConfig as con, TagTypes
from emd.System import UUID


class BreakLineProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_BREAK_LINE
    tag_regx = r"\n$"

    def process_tag(self, md_dicts):
        tp_dicts = copy.deepcopy(md_dicts)
        for l_level, l_level_dict in md_dicts.items():
            for t_uuid, tag_dict in l_level_dict.items():
                in_text = tag_dict[con.KEY_TEXT]
                tag_match = re.search(self.tag_regx, in_text, re.MULTILINE)
                while tag_match:
                    before_text = in_text[:tag_match.start()]
                    after_text = in_text[tag_match.end():]

                    new_uuid = UUID.get_new_uuid()
                    insert_dict = copy.deepcopy(con.insert_dict)
                    insert_dict[con.KEY_INLINE_FLAG] = False
                    insert_dict[con.KEY_TYPE] = self.tag_name
                    insert_dict[con.KEY_TEXT] = ""
                    insert_dict[con.KEY_EXTENSION] = ""
                    insert_dict[con.KEY_UUID] = new_uuid

                    store_level = l_level + 1
                    if store_level not in tp_dicts:
                        tp_dicts[store_level] = {}
                    tp_dicts[store_level][new_uuid] = insert_dict

                    in_text = before_text + new_uuid + after_text
                    tp_dicts[l_level][t_uuid][con.KEY_TEXT] = in_text
                    md_dicts[l_level][t_uuid][con.KEY_TEXT] = in_text

                    tag_match = re.search(self.tag_regx, in_text, re.MULTILINE)
        return tp_dicts
