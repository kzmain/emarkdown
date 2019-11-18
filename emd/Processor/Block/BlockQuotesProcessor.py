import copy
import re

from emd.System import UUID


class BlockQuotesProcessor:
    # Match '>' with '- ' , '* ', '1. ' before
    block_quote_regx_raw = r"(((?<=(\n))|(?<!\W|\w))( )*)(((\*)|(\-)|(\d\.))( )+)*((>)(( )+((?!\n)(\w|\W))+|( *))(\n)?)+"
    # Match '>' only
    block_quote_regx = r"((%s)(( )+((?!\n)(\w|\W))+|( *))(\n)?)+" % ">"
    # Match all '> ' and prepare to replace
    block_quote_replace_regx = r"((?<!\W|\w)|(?<=\n))(%s( )*)" % ">"

    def process(self, md_block_dicts):
        # Step 1 Match first block quote
        update_dict = copy.deepcopy(md_block_dicts)
        # Step 2 Process matched block quote
        checking_flag = True
        while checking_flag:
            checking_flag = False
            md_block_dicts = copy.deepcopy(update_dict)
            for level, level_dict in md_block_dicts.items():
                for uuid, text_dict in level_dict.items():
                    input_text = text_dict["text"]
                    raw_match = re.search(self.block_quote_regx_raw, input_text)
                    while raw_match:
                        checking_flag = True
                        before_text_raw = input_text[:raw_match.start()]
                        after_text_raw = input_text[raw_match.end():]

                        match_text_raw = input_text[raw_match.start():raw_match.end()]
                        match_uuid = UUID.get_new_uuid()
                        # 2.3 Prepare to add <blockquote>
                        real_match = re.search(self.block_quote_regx, match_text_raw)
                        before_text = match_text_raw[:real_match.start()]
                        after_text = match_text_raw[real_match.end():]

                        match_text = match_text_raw[real_match.start():real_match.end()]
                        # 2.4 Replace >
                        match_text = re.sub(self.block_quote_replace_regx, "", match_text)

                        store_level = level + 1
                        if store_level not in update_dict:
                            update_dict[store_level] = {}
                        update_dict[store_level][match_uuid] = {"type": "blockquote", "text": match_text, "inline": True}

                        update_dict[level][uuid]["text"] = before_text_raw + before_text + match_uuid + after_text_raw
                        md_block_dicts[level][uuid]["text"] = before_text_raw + before_text + match_uuid + "\n" + after_text_raw

                        input_text = text_dict["text"]
                        raw_match = re.search(self.block_quote_regx_raw, input_text)
        return md_block_dicts