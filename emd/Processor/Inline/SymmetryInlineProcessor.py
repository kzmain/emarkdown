import copy
import re

from emd.System import UUID
from emd.Processor.Config import TagConfig as con, TagTypes
from emd.Processor.BasicProcessor import BasicProcessor


class SymmetryInlineProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_SYMMETRY_INLINE
    inline_regx = r"(%s)(?!%s)((\n)?(?!%s)(.))*(%s)(?!%s)"
    inline_regx_end = r"(\n)?%s(?!\w|(?!\n)\W)"
    inline_regx_start = r"^%s"

    def __init__(self):
        pass

    def process_mutable_tag(self, md_dicts, tags_dict=con.CONFIG_DICT[con.CONFIG_TYPE_INLINE_SYMMETRY][con.CHANGEABLE_TAG]):
        # Changeable Second
        for _, tag_dict in tags_dict.items():
            tag_unit = tag_dict[con.BASIC_UNIT]
            tag = tag_dict[con.TAG_REGX]
            line_regx = self.inline_regx % (tag, tag_unit, tag, tag, tag_unit)
            inline_regx_end = self.inline_regx_end % tag
            inline_regx_start = self.inline_regx_start % tag

            checking_flag = True
            tp_dicts = copy.deepcopy(md_dicts)
            while checking_flag:
                checking_flag = False
                md_dicts = copy.deepcopy(tp_dicts)
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        input_text = text_dict[con.KEY_TEXT]
                        raw_match = re.search(line_regx, input_text)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            before_text = input_text[:raw_match.start()]
                            after_text = input_text[raw_match.end():]

                            match_text = input_text[raw_match.start():raw_match.end()]
                            match_text = re.sub(inline_regx_end, "", match_text)
                            match_text = re.sub(inline_regx_start, "", match_text)

                            new_insert_dict = copy.deepcopy(con.insert_dict)
                            new_uuid = UUID.get_new_uuid()
                            new_insert_dict[con.KEY_UUID] = new_uuid
                            new_insert_dict[con.KEY_EXTENSION] = ""
                            new_insert_dict[con.KEY_SUB_TYPE] = tag_dict[con.TAG_NAME]
                            new_insert_dict[con.KEY_INLINE_FLAG] = True
                            new_insert_dict[con.KEY_TEXT] = match_text
                            new_insert_dict[con.KEY_TYPE] = self.tag_name

                            store_level = level + 1
                            if store_level not in tp_dicts:
                                tp_dicts[store_level] = {}
                            tp_dicts[store_level][new_uuid] = new_insert_dict

                            input_text = before_text + new_uuid + after_text
                            tp_dicts[level][uuid][con.KEY_TEXT] = input_text
                            md_dicts[level][uuid][con.KEY_TEXT] = input_text

                            raw_match = re.search(line_regx, input_text)
        return md_dicts

    def process_immutable_tag(self, md_dicts, unmd_dicts, tags_dict=con.CONFIG_DICT[con.CONFIG_TYPE_INLINE_SYMMETRY][con.UNCHANGEABLE_TAG]):
        # Unchangeable First
        for _, tag_dict in tags_dict.items():
            tag_unit = tag_dict[con.BASIC_UNIT]
            tag = tag_dict[con.TAG_REGX]
            line_regx = self.inline_regx % (tag, tag_unit, tag, tag, tag_unit)
            inline_regx_end = self.inline_regx_end % tag
            inline_regx_start = self.inline_regx_start % tag

            # Step 2 INLINE condition must be second
            checking_flag = True
            while checking_flag:
                checking_flag = False
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        input_text = text_dict[con.KEY_TEXT]
                        raw_match = re.search(line_regx, input_text)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            before_text = input_text[:raw_match.start()]
                            after_text = input_text[raw_match.end():]

                            match_text = input_text[raw_match.start():raw_match.end()]
                            match_text = re.sub(inline_regx_end, "", match_text)
                            match_text = re.sub(inline_regx_start, "", match_text)

                            new_insert_dict = copy.deepcopy(con.insert_dict)
                            new_uuid = UUID.get_new_uuid()
                            new_insert_dict[con.KEY_UUID] = new_uuid
                            new_insert_dict[con.KEY_EXTENSION] = tag_dict[con.TAG_NAME]
                            new_insert_dict[con.KEY_INLINE_FLAG] = True
                            new_insert_dict[con.KEY_TEXT] = match_text
                            new_insert_dict[con.KEY_TYPE] = self.tag_name
                            new_insert_dict[con.KEY_SUB_TYPE] = tag_dict[con.TAG_NAME]

                            unmd_dicts[new_uuid] = new_insert_dict

                            input_text = before_text + new_uuid + after_text
                            # Update original dict
                            md_dicts[level][uuid][con.KEY_TEXT] = input_text
                            raw_match = re.search(line_regx, input_text)
        return md_dicts, unmd_dicts

    def __process_tag(self, md_dicts, unmd_dicts):
        md_dicts, unmd_dicts = self.process_immutable_tag(md_dicts, unmd_dicts)
        md_dicts = self.process_mutable_tag(md_dicts)
        return md_dicts, unmd_dicts
