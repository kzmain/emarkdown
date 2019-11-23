import copy
import re

from emd.Processor.BasicProcessor import BasicProcessor
from emd.Processor.Config import TagConfig as Config, TagTypes
from emd.System import UUID


class HorizontalRuleProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_HORIZONTAL_RULE
    tag_regx = r"^((-){3,}|(_){3,}|(\*){3,})$"

    def process_tag(self, md_dicts):
        tp_dicts = copy.deepcopy(md_dicts)
        for l_level, l_level_dict in md_dicts.items():
            for t_uuid, tag_dict in l_level_dict.items():

                tag_type = tag_dict[Config.KEY_TYPE]
                if tag_type == TagTypes.TYPE_BLOCK_QUOTE \
                        or tag_type == TagTypes.TYPE_START \
                        or tag_type == TagTypes.TYPE_SYMMETRY_BLOCK:
                    in_text = tag_dict[Config.KEY_TEXT]
                    tag_match = re.search(self.tag_regx, in_text, re.MULTILINE)
                    while tag_match:
                        before_text = in_text[:tag_match.start()]
                        after_text = in_text[tag_match.end():]

                        new_uuid = UUID.get_new_uuid()
                        insert_dict = copy.deepcopy(Config.insert_dict)
                        insert_dict[Config.KEY_INLINE_FLAG] = False
                        insert_dict[Config.KEY_TYPE] = self.tag_name
                        insert_dict[Config.KEY_TEXT] = ""
                        insert_dict[Config.KEY_EXTENSION] = ""
                        insert_dict[Config.KEY_UUID] = new_uuid

                        store_level = l_level + 1
                        if store_level not in tp_dicts:
                            tp_dicts[store_level] = {}
                        tp_dicts[store_level][new_uuid] = insert_dict

                        in_text = before_text + new_uuid + after_text
                        tp_dicts[l_level][t_uuid][Config.KEY_TEXT] = in_text
                        md_dicts[l_level][t_uuid][Config.KEY_TEXT] = in_text

                        tag_match = re.search(self.tag_regx, in_text, re.MULTILINE)
        return tp_dicts
