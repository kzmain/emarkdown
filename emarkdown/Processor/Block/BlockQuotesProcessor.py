import copy
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp
from emarkdown.System import UUID
from emarkdown.Processor.Config import TagConfig as Config, TagTypes


class BlockQuotesProcessor(Bp):
    tag_name = TagTypes.TYPE_BLOCK_QUOTE
    # Match '>' with '- ' , '* ', '+', '1. ' before
    raw_regx = r"((((\*)|(\-)|(\d\.)))*( )*(>)( )+.*)(\n(?!((\*)|(\-)|(\d\.)))(.)+)*"
    # Match '>' only
    # block_quote_regx = r"((%s)(( )+((?!\n)(\w|\W))+|( *))(\n)?)+" % ">"
    exact_regx = r"(^( )*)?(>)( )+.*(\n(?!((\*)|(\-)|(\d\.)))(.)+)*"
    # Match all '> ' and prepare to replace
    # block_quote_replace_regx = r"((?<!\W|\w)|(?<=\n))(%s( )*)" % ">"
    replace_regx = r"((?<!\W|\w)|(?<=\n))( )*(>( )*)"

    # Recursive loop
    # Step 1 Match first block quote
    # Step 2 Process matched block quote
    def process_tag(self, md_dict, unmd_dicts):
        tp_dict = copy.deepcopy(md_dict)
        checking_flag = True
        while checking_flag:
            checking_flag = False
            md_dict = copy.deepcopy(tp_dict)
            for level, level_dict in md_dict.items():
                for uuid, tag_dict in level_dict.items():
                    # Raw match
                    in_txt = tag_dict[Config.KEY_TEXT]
                    match, b_raw, m_raw, a_raw = Bp.re_search_get_txt(in_txt, regx=self.raw_regx)
                    while match:
                        checking_flag = True
                        # Exact match
                        exact_match, b_txt, m_txt, a_txt = Bp.re_search_get_txt(m_raw, regx=self.exact_regx)
                        # Replace >
                        m_txt = re.sub(self.replace_regx, "", m_txt)
                        # Check
                        # ```
                        # > Example
                        # ```
                        unmd_dicts = BlockQuotesProcessor.__check_in_unmd_dict(m_txt, unmd_dicts)

                        new_dict, new_uuid = Bp.get_new_dict(m_txt, self.tag_name, is_inline=False)
                        tp_dict = Bp.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)

                        in_txt = b_raw + b_txt + new_uuid + a_raw + a_txt
                        tp_dict[level][uuid][Config.KEY_TEXT] = in_txt
                        md_dict[level][uuid][Config.KEY_TEXT] = in_txt

                        match, b_raw, m_raw, a_raw = Bp.re_search_get_txt(in_txt, regx=self.raw_regx)
        return md_dict, unmd_dicts

    @staticmethod
    def __check_in_unmd_dict(tag_text, unmd_dict):
        check_text = copy.deepcopy(tag_text)
        match_uuid = re.search(UUID.get_regx_uuid(), check_text)
        while match_uuid:
            check_uuid = check_text[match_uuid.start():match_uuid.end()]
            if check_uuid in unmd_dict.keys():
                if not unmd_dict[check_uuid][Config.KEY_INLINE_FLAG]:
                    update_text = unmd_dict[check_uuid][Config.KEY_TEXT]
                    update_text = re.sub(BlockQuotesProcessor.replace_regx, "", update_text)
                    unmd_dict[check_uuid][Config.KEY_TEXT] = update_text
            check_text = check_text.replace(check_uuid, "")
            match_uuid = re.search(UUID.get_regx_uuid(), check_text)
        return unmd_dict
