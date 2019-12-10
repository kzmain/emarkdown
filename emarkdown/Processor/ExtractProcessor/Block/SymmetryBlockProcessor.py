import copy
import re

from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as Config, TagTypes
from emarkdown.Processor.ExtractProcessor.Inline.SymmetryInlineProcessor import SymmetryInlineProcessor


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
    s_mutable_block_regx_end = r"(\n)?%s(?!\w|(?!\n)\W)"

    def process_immutable_tag(self, md_dicts, unmd_dict):
        # Unchangeable First
        for _, tag_dict in Config.CONFIG_DICT[Config.CONFIG_TYPE_BLOCK_SYMMETRY][Config.UNCHANGEABLE_TAG].items():
            tag_unit = tag_dict[Config.TAG_BASIC_UNIT]
            tag = tag_dict[Config.TAG_REGX]

            block_regx = self.s_immutable_block_regx_raw % (tag, tag_unit, tag, tag, tag, tag_unit)
            exact_regx = self.s_immutable_block_regx_exact % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_info = self.s_immutable_block_regx_info % tag
            block_regx_end = self.s_immutable_block_regx_end % tag

            # Step 1 BLOCK condition must be first
            checking_flag = True
            while checking_flag:
                checking_flag = False
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        in_txt = text_dict[Config.KEY_TEXT]
                        match, b_raw, m_raw, a_raw = self.re_search_get_txt(in_txt, None, block_regx)
                        while match:
                            checking_flag = True
                            del match
                            # Find exact math code block
                            e_match, b_txt, m_txt, a_txt = self.re_search_get_txt(m_raw, None, exact_regx)
                            del m_raw
                            del e_match
                            # Find info tag and real txt
                            info_match = re.search(block_regx_info, m_txt)

                            info_text = m_txt[info_match.start():info_match.end()].replace("\n", "")

                            div_text = m_txt[info_match.end():]
                            div_text = re.sub(block_regx_end, "", div_text)

                            new_dict, new_uuid = self.get_new_dict(div_text, self.tag_name, tag_dict[Config.TAG_NAME], False, info_text)

                            unmd_dict[new_uuid] = new_dict

                            del new_dict
                            in_txt = b_raw + b_txt + new_uuid + a_txt + a_raw
                            # Update original dict
                            md_dicts[level][uuid][Config.KEY_TEXT] = in_txt
                            match, b_raw, m_raw, a_raw = self.re_search_get_txt(in_txt, None, block_regx)

        inline_processor = SymmetryInlineProcessor()
        tags_dict = Config.CONFIG_DICT[Config.CONFIG_TYPE_BLOCK_SYMMETRY][Config.UNCHANGEABLE_TAG]
        md_dicts, unmd_dict = inline_processor.process_immutable_tag(md_dicts, unmd_dict, tags_dict)
        return md_dicts, unmd_dict

    def process_mutable_tag(self, md_dict):
        # Changeable Second
        for sub_tag_name, tag_dict in Config.CONFIG_DICT[Config.CONFIG_TYPE_BLOCK_SYMMETRY][Config.CHANGEABLE_TAG].items():
            tag_unit = tag_dict[Config.TAG_BASIC_UNIT]
            tag = tag_dict[Config.TAG_REGX]

            block_regx = self.s_mutable_block_regx_raw % (tag, tag_unit, tag, tag, tag, tag_unit)
            exact_regx = self.s_mutable_block_regx_exact % (tag, tag_unit, tag, tag, tag, tag_unit)
            block_regx_info = self.s_mutable_block_regx_info % tag
            block_regx_end = self.s_mutable_block_regx_end % tag

            # Step 1 BLOCK condition must be first
            checking_flag = True
            tp_dict = copy.deepcopy(md_dict)
            while checking_flag:
                checking_flag = False
                md_dict = copy.deepcopy(tp_dict)
                for level, level_dict in md_dict.items():
                    for uuid, text_dict in level_dict.items():
                        in_txt = text_dict[Config.KEY_TEXT]
                        match, b_raw, m_raw, a_raw = self.re_search_get_txt(in_txt, None, block_regx)
                        while match:
                            checking_flag = True
                            # Find exact math code block
                            e_match, b_txt, m_txt, a_txt = self.re_search_get_txt(m_raw, None, exact_regx)

                            # Find exact math code block
                            info_match = re.search(block_regx_info, m_txt)
                            info_text = m_txt[info_match.start():info_match.end()].replace("\n", "")
                            div_text = m_txt[info_match.end():]
                            div_text = re.sub(block_regx_end, "", div_text)

                            new_dict, new_uuid = self.get_new_dict(div_text, self.tag_name, tag_dict[Config.TAG_NAME], False, info_text)
                            tp_dict = self.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)

                            in_txt = b_raw + b_txt + new_uuid + a_txt + a_raw

                            # Update original dict
                            tp_dict[level][uuid][Config.KEY_TEXT] = in_txt
                            md_dict[level][uuid][Config.KEY_TEXT] = in_txt
                            match, b_raw, m_raw, a_raw = self.re_search_get_txt(in_txt, None, block_regx)

            # Step 2 INLINE condition must be second
            inline_processor = SymmetryInlineProcessor()
            tags_dict = Config.CONFIG_DICT[Config.CONFIG_TYPE_BLOCK_SYMMETRY][Config.CHANGEABLE_TAG]
            md_dict = inline_processor.process_mutable_tag(md_dict, tags_dict)
        return md_dict

    def process_tag(self, md_dicts, unmd_dicts):
        md_dicts, unmd_dicts = self.process_immutable_tag(md_dicts, unmd_dicts)
        md_dicts = self.process_mutable_tag(md_dicts)
        return md_dicts, unmd_dicts
