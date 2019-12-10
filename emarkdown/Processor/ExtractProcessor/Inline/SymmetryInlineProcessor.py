import copy
import re

from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as Config, TagTypes


class SymmetryInlineProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_SYMMETRY_INLINE
    inline_regx = r"(%s)(?!%s)((\n)?(?!%s)(.))*(%s)(?!%s)"
    inline_regx_end = r"(\n)?%s(?!\w|(?!\n)\W)"
    inline_regx_start = r"^%s"

    def __init__(self):
        pass

    def process_mutable_tag(self, md_dicts, tags_dict=Config.CONFIG_DICT[Config.CONFIG_TYPE_INLINE_SYMMETRY][Config.CHANGEABLE_TAG]):
        # Changeable Second
        for _, tag_dict in tags_dict.items():
            tag_unit = tag_dict[Config.TAG_BASIC_UNIT]
            tag = tag_dict[Config.TAG_REGX]
            line_regx = self.inline_regx % (tag, tag_unit, tag, tag, tag_unit)
            inline_regx_end = self.inline_regx_end % tag
            inline_regx_start = self.inline_regx_start % tag

            checking_flag = True
            tp_dict = copy.deepcopy(md_dicts)
            while checking_flag:
                checking_flag = False
                md_dicts = copy.deepcopy(tp_dict)
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        in_txt = text_dict[Config.KEY_TEXT]
                        raw_match = re.search(line_regx, in_txt)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            b_txt = in_txt[:raw_match.start()]
                            a_txt = in_txt[raw_match.end():]

                            m_txt = in_txt[raw_match.start():raw_match.end()]
                            m_txt = re.sub(inline_regx_end, "", m_txt)
                            m_txt = re.sub(inline_regx_start, "", m_txt)

                            sub_type_name = tag_dict[Config.TAG_NAME]
                            new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, sub_type_name, True, "")
                            tp_dict = self.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)

                            in_txt = b_txt + new_uuid + a_txt
                            tp_dict[level][uuid][Config.KEY_TEXT] = in_txt
                            md_dicts[level][uuid][Config.KEY_TEXT] = in_txt

                            raw_match = re.search(line_regx, in_txt)
        return md_dicts

    def process_immutable_tag(self, md_dicts, unmd_dicts, tags_dict=Config.CONFIG_DICT[Config.CONFIG_TYPE_INLINE_SYMMETRY][Config.UNCHANGEABLE_TAG]):
        # Unchangeable First
        for _, tag_dict in tags_dict.items():
            tag_unit = tag_dict[Config.TAG_BASIC_UNIT]
            tag = tag_dict[Config.TAG_REGX]
            line_regx = self.inline_regx % (tag, tag_unit, tag, tag, tag_unit)
            inline_regx_end = self.inline_regx_end % tag
            inline_regx_start = self.inline_regx_start % tag

            # Step 2 INLINE condition must be second
            checking_flag = True
            while checking_flag:
                checking_flag = False
                for level, level_dict in md_dicts.items():
                    for uuid, text_dict in level_dict.items():
                        input_text = text_dict[Config.KEY_TEXT]
                        raw_match = re.search(line_regx, input_text)

                        while raw_match:
                            checking_flag = True
                            # Find raw match with special symbol before
                            b_txt = input_text[:raw_match.start()]
                            a_txt = input_text[raw_match.end():]

                            m_txt = input_text[raw_match.start():raw_match.end()]
                            m_txt = re.sub(inline_regx_end, "", m_txt)
                            m_txt = re.sub(inline_regx_start, "", m_txt)

                            # new_insert_dict = copy.deepcopy(Config.insert_dict)
                            # new_uuid = UUID.get_new_uuid()
                            # new_insert_dict[Config.KEY_UUID] = new_uuid
                            # new_insert_dict[Config.KEY_TEXT] = m_txt
                            # new_insert_dict[Config.KEY_INLINE_FLAG] = True
                            # new_insert_dict[Config.KEY_TYPE] = self.tag_name
                            # new_insert_dict[Config.KEY_SUB_TYPE] = tag_dict[Config.TAG_NAME]
                            # new_insert_dict[Config.KEY_EXTENSION] = tag_dict[Config.TAG_NAME]

                            new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, tag_dict[Config.TAG_NAME], True, "")

                            unmd_dicts[new_uuid] = new_dict

                            input_text = b_txt + new_uuid + a_txt
                            # Update original dict
                            md_dicts[level][uuid][Config.KEY_TEXT] = input_text
                            raw_match = re.search(line_regx, input_text)
        return md_dicts, unmd_dicts

    def __process_tag(self, md_dicts, unmd_dicts):
        md_dicts, unmd_dicts = self.process_immutable_tag(md_dicts, unmd_dicts)
        md_dicts = self.process_mutable_tag(md_dicts)
        return md_dicts, unmd_dicts
