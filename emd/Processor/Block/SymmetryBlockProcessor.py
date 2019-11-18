import copy
import re

from emd.Processor import SymmetryProcessorConfig as config


class SymmetryBlockProcessor:
    s_inline_regx = r"(((?<=(\n))|(?<!\W|\w))( )*)" \
                    r"(%s)(?!%s)" \
                    r"((?!%s|\n)(\w|\W))*" \
                    r"(%s)(?!%s)"
    # % ("```", "`", "```", "```", "`")

    s_block_regx = r"(((?<=(\n))|(?<!\W|\w))( )*)" \
                   r"(%s)(?!%s)" \
                   r"((?!%s)(\w|\W))*(\n)((?!%s)(\w|\W))*" \
                   r"(%s)(?!%s)"

    # % ("```", "`", "```", "```", "```", "`")

    def process(self, md_dicts, unmd_dicts):
        # Unchangeable first
        for tag, tag_dict in config.CONFIG[config.CONFIG_TYPE_BLOCK][config.UNCHANGEABLE_TAG].items():
            tag_unit = tag_dict[config.BASIC_UNIT]
            line_regx = self.s_inline_regx % (tag, tag_unit, tag, tag, tag_unit)
            block_regx = self.s_block_regx % (tag, tag_unit, tag, tag, tag, tag_unit)
            for regx in [line_regx, block_regx]:
                # Step 1 Match first block quote
                update_dict = copy.deepcopy(md_dicts)
                # Line condition must be first
                checking_flag = True
                while checking_flag:
                    checking_flag = False
                    for level, level_dict in md_dicts.items():
                        for uuid, text_dict in level_dict.items():
                            input_text = text_dict["text"]

                            # raw_match = re.search(self.block_quote_regx_raw, input_text)
                            # while raw_match:
                            #     checking_flag = True
                            #     before_text_raw = input_text[:raw_match.start()]
                            #     after_text_raw = input_text[raw_match.end():]
                            #
                            #     match_text_raw = input_text[raw_match.start():raw_match.end()]
                            #     match_uuid = UUID.get_new_uuid()
                            #     # 2.3 Prepare to add <blockquote>
                            #     real_match = re.search(self.block_quote_regx, match_text_raw)
                            #     before_text = match_text_raw[:real_match.start()]
                            #     after_text = match_text_raw[real_match.end():]
                            #
                            #     match_text = match_text_raw[real_match.start():real_match.end()]
                            #     # 2.4 Replace >
                            #     match_text = re.sub(self.block_quote_replace_regx, "", match_text)
                            #
                            #     store_level = level + 1
                            #     if store_level not in update_dict:
                            #         update_dict[store_level] = {}
                            #     update_dict[store_level][match_uuid] = {"type": "blockquote", "text": match_text,
                            #                                             "inline": True}
                            #
                            #     update_dict[level][uuid][
                            #         "text"] = before_text_raw + before_text + match_uuid + after_text_raw
                            #     md_block_dicts[level][uuid][
                            #         "text"] = before_text_raw + before_text + match_uuid + "\n" + after_text_raw
                            #
                            #     input_text = text_dict["text"]
                            #     raw_match = re.search(self.block_quote_regx_raw, input_text)

            print(line_regx)
            print(block_regx)

        print()
