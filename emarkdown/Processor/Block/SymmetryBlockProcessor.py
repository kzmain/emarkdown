import copy
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.Processor.Config import TagConfig as con, TagTypes
from emarkdown.Processor.Inline.SymmetryInlineProcessor import SymmetryInlineProcessor
from emarkdown.System import UUID


class SymmetryBlockProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_SYMMETRY_BLOCK

    # Start with "\n" or start with spaces ( )
    # Can start with 1. ordered list/2. unordered list/3. block
    # Start with tag but no unit follow
    # Code block elements
    # End with tag but no unit follow
    s_immutable_block_regx_raw = r"(((?<=(\n))|(?<!\W|\w))( )*)" \
                                 r"(((\*)|(\-)|(\d\.)|(>))( )+)*" \
                                 r"(%s)(?!%s)" \
                                 r"((?!%s)(\w|\W))*(\n)((?!%s)(\w|\W))*" \
                                 r"(%s)(?!%s)"
    s_immutable_block_regx_exact = r"(%s)(?!%s)((?!%s)(\w|\W))*(\n)((?!%s)(\w|\W))*(%s)(?!%s)"
    s_immutable_block_regx_info = r"(?<=(%s))(((?!\n)\W)|\w)*\n"
    # (?<=({blue_tag}))(((?!\n)\W)|\w)*\n
    s_immutable_block_regx_end = r"(\n)?%s(?!\w|(?!\n)\W)"

    # Start with "\n" or start with spaces ( )
    # Can start with 1. ordered list/2. unordered list/3. block
    # Start with tag but no unit follow
    # Code block elements
    # End with tag but no unit follow
    s_mutable_block_regx_raw = r"(((?<=(\n))|(?<!\W|\w))( )*)" \
                               r"(((\*)|(\-)|(\+)|(\d\.)|(>))( )+)*" \
                               r"(%s)(?!%s)" \
                               r"((?!%s)(\w|\W))*(\n)((?!%s)(\w|\W))*" \
                               r"(%s)(?!%s)"
    s_mutable_block_regx_exact = r"(%s)(?!%s)((?!%s)(\w|\W))*(\n)((?!%s)(\w|\W))*(%s)(?!%s)"
    s_mutable_block_regx_info = r"(?<=(%s))(((?!\n)\W)|\w)*\n"
    # (?<=({blue_tag}))(((?!\n)\W)|\w)*\n
    s_mutable_block_regx_end = r"(\n)?%s(?!\w|(?!\n)\W)"

    # (```)(?!`)((?!```)(\w | \W))*(\n)((?!```)(\w |\W))*(```)(?!`)

    def process_immutable_tag(self, md_dicts, unmd_dicts):
        # Unchangeable First
        for _, tag_dict in con.CONFIG_DICT[con.CONFIG_TYPE_BLOCK_SYMMETRY][con.UNCHANGEABLE_TAG].items():
            tag_unit = tag_dict[con.BASIC_UNIT]
            tag = tag_dict[con.TAG_REGX]

            block_regx = self.s_immutable_block_regx_raw % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_exact = self.s_immutable_block_regx_exact % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_info = self.s_immutable_block_regx_info % tag
            block_regx_end = self.s_immutable_block_regx_end % tag

            # Step 1 BLOCK condition must be first
            checking_flag = True
            while checking_flag:
                checking_flag = False
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        input_text = text_dict[con.KEY_TEXT]
                        raw_match = re.search(block_regx, input_text)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            before_text_raw = input_text[:raw_match.start()]
                            after_text_raw = input_text[raw_match.end():]

                            match_raw_text = input_text[raw_match.start():raw_match.end()]
                            del raw_match
                            # Find exact math code block
                            real_match = re.search(block_regx_exact, match_raw_text)
                            before_text = match_raw_text[:real_match.start()]
                            after_text = match_raw_text[real_match.end():]

                            match_text = match_raw_text[real_match.start():real_match.end()]
                            del match_raw_text
                            del real_match
                            # Find exact math code block
                            info_match = re.search(block_regx_info, match_text)
                            info_text = match_text[info_match.start():info_match.end()].replace("\n", "")
                            div_text = match_text[info_match.end():]
                            div_text = re.sub(block_regx_end, "", div_text)

                            # Replace
                            new_insert_dict = copy.deepcopy(con.insert_dict)
                            new_uuid = UUID.get_new_uuid()
                            new_insert_dict[con.KEY_UUID] = new_uuid
                            new_insert_dict[con.KEY_EXTENSION] = info_text
                            new_insert_dict[con.KEY_INLINE_FLAG] = False
                            new_insert_dict[con.KEY_TEXT] = div_text
                            new_insert_dict[con.KEY_TYPE] = self.tag_name
                            new_insert_dict[con.KEY_SUB_TYPE] = tag_dict[con.TAG_NAME]
                            unmd_dicts[new_uuid] = new_insert_dict

                            del new_insert_dict
                            input_text = before_text_raw + before_text + new_uuid + after_text + after_text_raw
                            # Update original dict
                            md_dicts[level][uuid][con.KEY_TEXT] = input_text
                            raw_match = re.search(block_regx, input_text)

        inline_processor = SymmetryInlineProcessor()
        tags_dict = con.CONFIG_DICT[con.CONFIG_TYPE_BLOCK_SYMMETRY][con.UNCHANGEABLE_TAG]
        md_dicts, unmd_dicts = inline_processor.process_immutable_tag(md_dicts, unmd_dicts, tags_dict)
        return md_dicts, unmd_dicts

    def process_mutable_tag(self, md_dicts):
        # Changeable Second
        for sub_tag_name, tag_dict in con.CONFIG_DICT[con.CONFIG_TYPE_BLOCK_SYMMETRY][con.CHANGEABLE_TAG].items():
            tag_unit = tag_dict[con.BASIC_UNIT]
            tag = tag_dict[con.TAG_REGX]

            block_regx = self.s_mutable_block_regx_raw % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_exact = self.s_mutable_block_regx_exact % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_info = self.s_mutable_block_regx_info % tag
            block_regx_end = self.s_mutable_block_regx_end % tag

            # Step 1 BLOCK condition must be first
            checking_flag = True
            tp_dicts = copy.deepcopy(md_dicts)
            while checking_flag:
                checking_flag = False
                md_dicts = copy.deepcopy(tp_dicts)
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        input_text = text_dict[con.KEY_TEXT]
                        raw_match = re.search(block_regx, input_text)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            before_text_raw = input_text[:raw_match.start()]
                            after_text_raw = input_text[raw_match.end():]

                            match_raw_text = input_text[raw_match.start():raw_match.end()]
                            # Find exact math code block
                            real_match = re.search(block_regx_exact, match_raw_text)
                            before_text = match_raw_text[:real_match.start()]
                            after_text = match_raw_text[real_match.end():]

                            match_text = match_raw_text[real_match.start():real_match.end()]
                            # Find exact math code block
                            info_match = re.search(block_regx_info, match_text)
                            info_text = match_text[info_match.start():info_match.end()].replace("\n", "")
                            div_text = match_text[info_match.end():]
                            div_text = re.sub(block_regx_end, "", div_text)

                            # Replace
                            new_insert_dict = copy.deepcopy(con.insert_dict)
                            new_uuid = UUID.get_new_uuid()
                            new_insert_dict[con.KEY_UUID] = new_uuid
                            new_insert_dict[con.KEY_EXTENSION] = info_text
                            new_insert_dict[con.KEY_INLINE_FLAG] = False
                            new_insert_dict[con.KEY_TEXT] = div_text
                            new_insert_dict[con.KEY_TYPE] = self.tag_name
                            new_insert_dict[con.KEY_SUB_TYPE] = tag_dict[con.TAG_NAME]

                            store_level = level + 1
                            if store_level not in tp_dicts:
                                tp_dicts[store_level] = {}
                            tp_dicts[store_level][new_uuid] = new_insert_dict

                            input_text = before_text_raw + before_text + new_uuid + after_text_raw
                            tp_dicts[level][uuid]["text"] = input_text
                            md_dicts[level][uuid]["text"] = input_text

                            # Update original dict
                            md_dicts[level][uuid][con.KEY_TEXT] = input_text
                            raw_match = re.search(block_regx, input_text)

            # Step 2 INLINE condition must be second
            inline_processor = SymmetryInlineProcessor()
            tags_dict = con.CONFIG_DICT[con.CONFIG_TYPE_BLOCK_SYMMETRY][con.CHANGEABLE_TAG]
            md_dicts = inline_processor.process_mutable_tag(md_dicts, tags_dict)
        return md_dicts

    def process_tag(self, md_dicts, unmd_dicts):
        md_dicts, unmd_dicts = self.process_immutable_tag(md_dicts, unmd_dicts)
        md_dicts = self.process_mutable_tag(md_dicts)
        return md_dicts, unmd_dicts
