#!/usr/bin/python
# -*- coding: UTF-8 -*-
import copy
import re

from emd.Processor.BasicProcessor import BasicProcessor
from emd.Processor.Config import TagConfig as Config, TagTypes
from emd.System import UUID


class TableProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_TABLE

    def __init__(self):
        pass

    # Table Header
    # Table Header / Table Body Splitter
    # Table Body
    regx_table = r"(.)+\|(.)+((\n)(\|| |\:)*(\-){3,}(\|| |\:|\-)*)(\n(.)+\|(.)+)*"
    regx_table_head = r"(.)+\|(.)+"
    regx_table_splitter = r"((\n)(\|| |\:)*(\-){3,}(\|| |\:|\-)*)"
    regx_table_body = r"(\n(.)+\|(.)+)*"

    def __lists_to_dicts(self, rows_list, max_width, td=True):

        # Table Level 0 match text
        # Table Level 1 tr tag
        # Table Level 2 td/th tag
        result_dict = {0: "", 1: {}, 2: {}}
        table_text = ""
        for elements_list in rows_list:
            row_text = ""
            for element_index in range(max_width):
                insert_dict = copy.deepcopy(Config.insert_dict)
                row_length = len(elements_list)
                if element_index < row_length:
                    insert_dict[Config.KEY_TEXT] = elements_list[element_index]
                else:
                    insert_dict[Config.KEY_TEXT] = ""
                insert_dict[Config.KEY_EXTENSION] = ""
                new_uuid = UUID.get_new_uuid()
                insert_dict[Config.KEY_UUID] = new_uuid
                insert_dict[Config.KEY_INLINE_FLAG] = True
                if td:
                    insert_dict[Config.KEY_TYPE] = TagTypes.TYPE_TABLE_TD
                else:
                    insert_dict[Config.KEY_TYPE] = TagTypes.TYPE_TABLE_TH

                row_text += "\n" + new_uuid
                result_dict[2][new_uuid] = insert_dict
            new_uuid = UUID.get_new_uuid()
            insert_dict = copy.deepcopy(Config.insert_dict)
            insert_dict[Config.KEY_TEXT] = re.sub("^\n", "", row_text)
            insert_dict[Config.KEY_EXTENSION] = ""
            insert_dict[Config.KEY_INLINE_FLAG] = False
            insert_dict[Config.KEY_TYPE] = TagTypes.TYPE_TABLE_TR
            insert_dict[Config.KEY_UUID] = new_uuid
            table_text += "\n" + new_uuid
            result_dict[1][new_uuid] = insert_dict
        result_dict[0] = table_text
        return result_dict

    @staticmethod
    def __split_line(text):
        max_width = 0
        line_list = text.splitlines()
        for line_index in range(len(line_list)):
            row_text = line_list[line_index]
            row_text = re.sub(r"^\|", "", row_text)
            row_text = re.sub(r"\|$", "", row_text)
            tds = row_text.split("|")
            for element_index in range(len(tds)):
                tds[element_index] = tds[element_index].strip()
            line_list[line_index] = tds
            if max_width < len(tds):
                max_width = len(tds)
        return line_list, max_width

    def process_tag(self, md_dicts):
        # Step 1 Match first block quote
        tp_dicts = copy.deepcopy(md_dicts)
        # Step 2 Process matched block quote
        checking_flag = True
        while checking_flag:
            checking_flag = False
            md_dicts = copy.deepcopy(tp_dicts)
            for level, level_dict in md_dicts.items():
                for l_uuid, l_tag_dict in level_dict.items():

                    input_text = l_tag_dict[Config.KEY_TEXT]
                    table_match = re.search(self.regx_table, input_text)
                    while table_match:
                        before_text = input_text[:table_match.start()]
                        after_text = input_text[table_match.end():]

                        table_text = input_text[table_match.start():table_match.end()]

                        thead_match = re.match(self.regx_table_head, table_text)
                        thead_text = table_text[:thead_match.end()]
                        del thead_match
                        tbody_text = table_text.replace(thead_text, "")
                        tbody_text = re.sub(self.regx_table_splitter, "", tbody_text)
                        tbody_text = re.sub("^\n", "", tbody_text)

                        ths, th_width = self.__split_line(thead_text)
                        tds, td_width = self.__split_line(tbody_text)
                        del thead_text
                        del tbody_text
                        max_width = td_width if td_width > th_width else th_width
                        del td_width
                        del th_width
                        ths = self.__lists_to_dicts(ths, max_width, False)
                        tds = self.__lists_to_dicts(tds, max_width, True)
                        del max_width
                        ths[1].update(tds[1])
                        ths[2].update(tds[2])
                        table_text = re.sub(r"^\n", "", ths[0] + tds[0])
                        del tds
                        new_uuid = UUID.get_new_uuid()
                        insert_dict = copy.deepcopy(Config.insert_dict)
                        insert_dict[Config.KEY_TEXT] = table_text
                        insert_dict[Config.KEY_EXTENSION] = ""
                        insert_dict[Config.KEY_INLINE_FLAG] = False
                        insert_dict[Config.KEY_TYPE] = self.tag_name
                        insert_dict[Config.KEY_UUID] = new_uuid
                        ths[0] = {}
                        ths[0][new_uuid] = insert_dict
                        del table_text
                        del insert_dict

                        input_text = before_text + new_uuid + after_text
                        del new_uuid
                        del before_text
                        del after_text
                        md_dicts[level][l_uuid][Config.KEY_TEXT] = input_text
                        tp_dicts[level][l_uuid][Config.KEY_TEXT] = input_text

                        for l_level, l_level_dict in ths.items():
                            store_level = level + l_level + 1
                            if store_level not in tp_dicts.keys():
                                tp_dicts[store_level] = {}
                            tp_dicts[store_level].update(l_level_dict)
                            del l_level
                            del store_level
                            del l_level_dict
                        table_match = re.search(self.regx_table, input_text)
                        del ths
                    del input_text
                    del table_match
                    del l_uuid
                    del l_tag_dict
                del level
                del level_dict
        del md_dicts
        del checking_flag
        return tp_dicts
