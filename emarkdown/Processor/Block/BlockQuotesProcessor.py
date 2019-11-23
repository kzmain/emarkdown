import copy
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.System import UUID
from emarkdown.Processor.Config import TagConfig as con, TagTypes


class BlockQuotesProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_BLOCK_QUOTE
    # Match '>' with '- ' , '* ', '+', '1. ' before
    block_quote_regx_raw = r"((((\*)|(\-)|(\d\.)))*( )*(>)( )+.*)(\n(?!((\*)|(\-)|(\d\.)))(.)+)*"
    # Match '>' only
    # block_quote_regx = r"((%s)(( )+((?!\n)(\w|\W))+|( *))(\n)?)+" % ">"
    block_quote_regx = r"(^( )*)?(>)( )+.*(\n(?!((\*)|(\-)|(\d\.)))(.)+)*"
    # Match all '> ' and prepare to replace
    # block_quote_replace_regx = r"((?<!\W|\w)|(?<=\n))(%s( )*)" % ">"
    block_quote_replace_regx = r"((?<!\W|\w)|(?<=\n))( )*(>( )*)"

    def process_tag(self, md_dicts, unmd_dicts):
        # Step 1 Match first block quote
        tp_dict = copy.deepcopy(md_dicts)
        # Step 2 Process matched block quote
        checking_flag = True
        while checking_flag:
            checking_flag = False
            md_dicts = copy.deepcopy(tp_dict)
            for level, level_dict in md_dicts.items():
                for uuid, text_dict in level_dict.items():
                    input_text = text_dict[con.KEY_TEXT]
                    raw_match = re.search(self.block_quote_regx_raw, input_text)
                    while raw_match:
                        checking_flag = True
                        before_text_raw = input_text[:raw_match.start()]
                        after_text_raw = input_text[raw_match.end():]

                        match_text_raw = input_text[raw_match.start():raw_match.end()]
                        # 2.3 Prepare to add <blockquote>
                        real_match = re.search(self.block_quote_regx, match_text_raw)
                        before_text = match_text_raw[:real_match.start()]
                        after_text = match_text_raw[real_match.end():]

                        match_text = match_text_raw[real_match.start():real_match.end()]
                        # 2.4 Replace >
                        match_text = re.sub(self.block_quote_replace_regx, "", match_text)

                        check_text = copy.deepcopy(match_text)
                        match_uuid = re.search(UUID.get_regx_uuid(), check_text)
                        while match_uuid:
                            check_uuid = check_text[match_uuid.start():match_uuid.end()]
                            if check_uuid in unmd_dicts.keys():
                                if not unmd_dicts[check_uuid][con.KEY_INLINE_FLAG]:
                                    update_text = unmd_dicts[check_uuid][con.KEY_TEXT]
                                    update_text = re.sub(self.block_quote_replace_regx, "", update_text)
                                    unmd_dicts[check_uuid][con.KEY_TEXT] = update_text
                            check_text = check_text.replace(check_uuid, "")
                            match_uuid = re.search(UUID.get_regx_uuid(), check_text)

                        new_insert_dict = copy.deepcopy(con.insert_dict)
                        new_uuid = UUID.get_new_uuid()
                        new_insert_dict[con.KEY_UUID] = new_uuid
                        new_insert_dict[con.KEY_EXTENSION] = ""
                        new_insert_dict[con.KEY_INLINE_FLAG] = False
                        new_insert_dict[con.KEY_TEXT] = match_text
                        new_insert_dict[con.KEY_TYPE] = self.tag_name

                        store_level = level + 1
                        if store_level not in tp_dict:
                            tp_dict[store_level] = {}
                        tp_dict[store_level][new_uuid] = new_insert_dict

                        input_text = before_text_raw + before_text + new_uuid + after_text_raw
                        tp_dict[level][uuid][con.KEY_TEXT] = input_text
                        md_dicts[level][uuid][con.KEY_TEXT] = input_text
                        raw_match = re.search(self.block_quote_regx_raw, input_text)
        return md_dicts, unmd_dicts
