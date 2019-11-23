import copy
import re

from emarkdown.Processor.Block.TableProcessor import TableProcessor
from emarkdown.System import UUID
from emarkdown.Processor.Config import TagConfig as con, TagTypes
from emarkdown.Processor.BasicProcessor import BasicProcessor


# H1 - #6 Tags
# 比===及---先

class HeaderProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_HEADER
    # Type 1
    heading_regx = r"((?<=\n)|(?<!\W|\w))^( )*((#){1,6})( +)((?!\n)(\w|\W))*"
    # Type 2
    heading_underline_regx = r"(\w|(?!\n)\W)+\n((-){3,}|(=){3,})$"

    # 在block里面都可以处理header，除了List和Table
    def process_tag(self, md_dicts):
        tp_dicts = copy.deepcopy(md_dicts)
        for l_level, l_level_dicts in md_dicts.items():
            for l_uuid, tag_dict in l_level_dicts.items():
                tag_type = tag_dict[con.KEY_TYPE]
                tag_inline = tag_dict[con.KEY_INLINE_FLAG]
                if not tag_inline and TableProcessor.tag_name != tag_type and HeaderProcessor.tag_name != tag_type:

                    tag_text = tag_dict[con.KEY_TEXT]
                    heading_match = re.search(self.heading_regx, tag_text, re.MULTILINE)
                    while heading_match:
                        header_text = tag_text[heading_match.start():heading_match.end()]

                        before_text = tag_text[:heading_match.start()]
                        after_text = tag_text[heading_match.end():]

                        header_type_match = re.search("#{1,6}( )*", header_text)
                        number_sign = header_text[header_type_match.start():header_type_match.end()].replace(" ", "")
                        header_type = "<h" + str(len(number_sign)) + " id = \"%s\">"

                        header_text = header_text[header_type_match.end():]

                        new_uuid = UUID.get_new_uuid()
                        insert_dict = copy.deepcopy(con.insert_dict)
                        insert_dict[con.KEY_INLINE_FLAG] = False
                        insert_dict[con.KEY_TYPE] = self.tag_name
                        insert_dict[con.KEY_TEXT] = header_text
                        insert_dict[con.KEY_EXTENSION] = ""
                        insert_dict[con.KEY_SUB_TYPE] = header_type
                        insert_dict[con.KEY_UUID] = new_uuid

                        store_level = l_level + 1
                        if store_level not in tp_dicts:
                            tp_dicts[store_level] = {}
                        tp_dicts[store_level][new_uuid] = insert_dict

                        tag_text = before_text + new_uuid + after_text
                        tp_dicts[l_level][l_uuid][con.KEY_TEXT] = tag_text
                        md_dicts[l_level][l_uuid][con.KEY_TEXT] = tag_text

                        heading_match = re.search(self.heading_regx, tag_text, re.MULTILINE)

                    heading_match = re.search(self.heading_underline_regx, tag_text, re.MULTILINE)
                    while heading_match:
                        match_text = tag_text[heading_match.start():heading_match.end()]
                        # match_uuid = UUID.get_new_uuid()

                        before_text = tag_text[:heading_match.start()]
                        after_text = tag_text[heading_match.end():]

                        match_text_list = match_text.split("\n")
                        heading_type = str(1) if "=" in match_text_list[1] else str(2)
                        header_type = "<h" + heading_type + " id = \"%s\">"

                        header_text = match_text_list[0]

                        new_uuid = UUID.get_new_uuid()
                        insert_dict = copy.deepcopy(con.insert_dict)
                        insert_dict[con.KEY_INLINE_FLAG] = True
                        insert_dict[con.KEY_TYPE] = self.tag_name
                        insert_dict[con.KEY_TEXT] = header_text
                        insert_dict[con.KEY_EXTENSION] = ""
                        insert_dict[con.KEY_SUB_TYPE] = header_type
                        insert_dict[con.KEY_UUID] = new_uuid

                        store_level = l_level + 1
                        if store_level not in tp_dicts:
                            tp_dicts[store_level] = {}
                        tp_dicts[store_level][new_uuid] = insert_dict

                        tag_text = before_text + new_uuid + after_text
                        tp_dicts[l_level][l_uuid][con.KEY_TEXT] = tag_text
                        md_dicts[l_level][l_uuid][con.KEY_TEXT] = tag_text

                        heading_match = re.search(self.heading_regx, tag_text, re.MULTILINE)
        return tp_dicts
