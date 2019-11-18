import re

from emd.System import UUID


class HeaderProcessor:
    heading_regx = r"((?<=\n)|(?<!\W|\w))^( )*((#){1,6})( +)((?!\n)(\w|\W))*"
    heading_underline_regx = r"(\w|(?!\n)\W)+\n((-){3,}|(=){3,})$"

    def process(self, input_text, md_block_dicts):
        heading_match = re.search(self.heading_regx, input_text, re.MULTILINE)
        md_block_dicts[1] = {}
        while heading_match:
            match_text = input_text[heading_match.start():heading_match.end()]
            match_uuid = UUID.get_new_uuid()

            before_text = input_text[:heading_match.start()]
            after_text = input_text[heading_match.end():]

            header_type_match = re.search("#{1,6}( )*", match_text)
            number_sign = match_text[header_type_match.start():header_type_match.end()].replace(" ", "")

            header_text = match_text[header_type_match.end():]
            header_type = "h" + str(len(number_sign))

            md_block_dicts[1][match_uuid] = {"type": header_type, "text": header_text}

            input_text = before_text + match_uuid + after_text
            heading_match = re.search(self.heading_regx, input_text, re.MULTILINE)

        heading_match = re.search(self.heading_underline_regx, input_text, re.MULTILINE)
        while heading_match:
            match_text = input_text[heading_match.start():heading_match.end()]
            match_uuid = UUID.get_new_uuid()

            before_text = input_text[:heading_match.start()]
            after_text = input_text[heading_match.end():]

            match_text_list = match_text.split("\n")
            heading_type = str(1) if "=" in match_text_list[1] else str(2)

            header_type = "h" + heading_type
            header_text = match_text_list[0]

            md_block_dicts[1][match_uuid] = {"type": header_type, "text": header_text}

            input_text = before_text + match_uuid + after_text
            heading_match = re.search(self.heading_underline_regx, input_text, re.MULTILINE)

        return input_text, md_block_dicts
