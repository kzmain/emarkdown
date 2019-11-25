# -*- coding: UTF-8 -*-
import copy
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp
from emarkdown.Processor.Config import TagConfig as Config, TagTypes


class TableProcessor(Bp):
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

    def process_tag(self, md_dict):
        # Step 1 Match first block quote
        tp_dict = copy.deepcopy(md_dict)
        # Step 2 Process matched block quote
        check_flag = True
        while check_flag:
            check_flag = False
            md_dict = copy.deepcopy(tp_dict)
            for level, level_dict in md_dict.items():
                for tag_uuid, tag_dict in level_dict.items():
                    in_txt = tag_dict[Config.KEY_TEXT]

                    match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.regx_table)
                    while match:
                        th_txt = self.__get_th_txt(m_txt)
                        td_txt = self.__get_td_txt(m_txt, th_txt)
                        ths, th_width = self.__split_line(th_txt)
                        tds, td_width = self.__split_line(td_txt)
                        max_width = td_width if td_width > th_width else th_width
                        del td_width, td_txt
                        del th_width, th_txt
                        ths = self.__lists_to_dicts(ths, max_width, False)
                        tds = self.__lists_to_dicts(tds, max_width, True)
                        tbs, new_uuid = self.__update_ths_tds_dicts(ths, tds)
                        del max_width
                        del ths, tds

                        for _level, _dict in tbs.items():
                            store_level = level + _level + 1
                            if store_level not in tp_dict.keys():
                                tp_dict[store_level] = {}
                            tp_dict[store_level].update(_dict)
                            del _level, _dict, store_level
                        del tbs

                        in_txt = b_txt + new_uuid + a_txt
                        md_dict[level][tag_uuid][Config.KEY_TEXT] = in_txt
                        tp_dict[level][tag_uuid][Config.KEY_TEXT] = in_txt
                        match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.regx_table)
                        del new_uuid

                    del match, b_txt, m_txt, a_txt, in_txt
                    del tag_uuid, tag_dict
                del level, level_dict
        del check_flag, md_dict
        return tp_dict

    @staticmethod
    def __get_th_txt(m_txt):
        thead_match = re.match(TableProcessor.regx_table_head, m_txt)
        th_txt = m_txt[:thead_match.end()]
        return th_txt

    @staticmethod
    def __get_td_txt(m_txt, th_txt):
        td_txt = m_txt.replace(th_txt, "")
        td_txt = re.sub(TableProcessor.regx_table_splitter, "", td_txt)
        td_txt = re.sub("^\n", "", td_txt)
        return td_txt

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

    @staticmethod
    def __lists_to_dicts(rows_list, max_width, td=True):

        # Table Level 0 match text
        # Table Level 1 tr tag
        # Table Level 2 td/th tag
        result_dict = {0: "", 1: {}, 2: {}}
        table_text = ""
        for elements_list in rows_list:
            row_text = ""
            for element_index in range(max_width):
                row_len = len(elements_list)
                new_txt = elements_list[element_index] if element_index < row_len else ""
                new_type = TagTypes.TYPE_TABLE_TD if td else TagTypes.TYPE_TABLE_TH

                new_dict, new_uuid = Bp.get_new_dict(new_txt, new_type, "", True)
                result_dict[2][new_uuid] = new_dict
                row_text += "\n" + new_uuid

            new_dict, new_uuid = Bp.get_new_dict(re.sub("^\n", "", row_text), TagTypes.TYPE_TABLE_TR, "", False)
            result_dict[1][new_uuid] = new_dict
            table_text += "\n" + new_uuid
        result_dict[0] = table_text
        return result_dict

    def __update_ths_tds_dicts(self, ths, tds):
        ths[1].update(tds[1])
        ths[2].update(tds[2])
        m_txt = re.sub(r"^\n", "", ths[0] + tds[0])
        new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, "", False, "")
        ths[0] = {}
        ths[0][new_uuid] = new_dict
        return ths, new_uuid
