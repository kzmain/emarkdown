# -*- coding: UTF-8 -*-
import copy
import re

from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as con, TagTypes
from emarkdown.System.Tool import HTML_Entities, UUID
from emarkdown.System.Config import Config

# List ol/ul放在inline type里了


class ListProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_LIST
    # Match first list line
    # Match first list line's continue sentences
    # Match next line's line signal or normal line
    # list_block_regx = r"(((?<=\n)|(?<!.))(( )*(\*|\-|\+|\d\.))(( )+(?!\n.)(.)*))(((\n)(.)+)*)"
    list_regx = r"(((?<=\n)|(?<!.))(( )*(\*|\-|\+|\d\.))(( )+(?!\n)(.)*))(((\n)(.)+)|(\n)(\n)( )+.+|(\n)(\n)(( )*(\*|\-|\+|\d\.))(( )+(?!\n)(.)*))*"
    sub_list_regx = r"( ){%d,}(\d.|\*|\-|\+)( )+.*((\n)( ){%d,}.*)*"

    is_list_line_regx = r"((?<=\n)|(?<!\W|\w))( )*(?=(\d.|\*|\-|\+)( )+)"

    # unordered_regx = r"((?<=\n)|(?<!\W|\w))( )*(\*|\-|\+)( )+.+"
    # ordered_regx = r"((?<=\n)|(?<!\W|\w))( )*(\d.)( )+.+"
    # This only match a element of a list
    ordered_regx = r"(\n)?(\d\.)( )+.*(\n(?!(\d\.)|\*).*)*"
    unordered_regx = r"(\n)?(\*|\-|\+)( )+.*(\n(?!(\d\.)|\*|\-|\+).*)*"
    # Match space before list symbol to replace
    space_regx = r"^( ){%d,%d}(?=\*|\+|\-|\d\.)"
    ls_num = 2

    def __init__(self):
        pass

    def __reformat_list(self, input_text):
        input_text = input_text.replace("\t", "    ")
        space_set = {0}
        for line_text in input_text.splitlines():
            space_match = re.match("^( )*", line_text)
            space_count = len(line_text[space_match.start():space_match.end()])
            if space_count % 2 != 0:
                space_count += 1
            space_set.add(space_count)
        space_set = sorted(space_set)
        space_l = 0
        for space_num in space_set:
            if space_num == 0:
                continue
            space_l += 1
            input_text = re.sub(self.space_regx % (space_num - 1, space_num), " " * space_l * self.ls_num, input_text,
                                flags=re.MULTILINE)

        space_num = -1
        result_text = ""
        for line in input_text.splitlines():
            space_match = re.match("^( )*", line)
            line_text = line[space_match.end():]
            line_space = space_match.end() - space_match.start()
            del space_match

            is_list = True if re.search(self.is_list_line_regx, line) else False

            if is_list:
                if space_num < 0:
                    space_num = self.ls_num
                elif line_space >= space_num:
                    space_num += self.ls_num
                else:
                    space_num = (line_space % self.ls_num) + line_space + self.ls_num
                result_text += ((space_num - self.ls_num) * " ") + line_text + "\n"
            else:
                if line_space > space_num:
                    if line_space - space_num > 0:
                        if Config.converter_mode == Config.CONVERTER_TYPE_HTML:
                            line_text = (line_space - space_num - self.ls_num) * HTML_Entities.ENTITY_DICT[" "] + line_text
                elif line_space < space_num and len(line_text) != 0:
                    space_num = (line_space % self.ls_num) + line_space + self.ls_num
                result_text += (space_num * " ") + line_text + "\n"
        result_text = re.sub(r"(\n)$", "", result_text)
        return result_text

    def __split_sub_list(self, input_text):
        list_level = 0
        text_dict = {list_level: {UUID.get_new_uuid(): input_text}}
        temp_dict = copy.deepcopy(text_dict)
        checking_flag = True
        # Split different level lists
        while checking_flag:
            checking_flag = False
            text_dict = copy.deepcopy(temp_dict)
            for level, level_dict in text_dict.items():
                for key_uuid, text in level_dict.items():
                    sub_list_block_regx = self.sub_list_regx % (
                        self.ls_num * (level + 1), self.ls_num * (level + 1))
                    match = re.search(sub_list_block_regx, text)
                    while match:
                        checking_flag = True
                        new_key = UUID.get_new_uuid()
                        block_text = text[match.start():match.end()]

                        before_text = text[:match.start()]
                        after_text = text[match.end():]

                        block_text = re.sub("^( ){%d}" % self.ls_num * (level + 1), "", block_text, flags=re.MULTILINE)

                        text = before_text + " " * self.ls_num + new_key + after_text
                        text_dict[level][key_uuid] = text
                        temp_dict[level][key_uuid] = text
                        store_level = level + 1
                        if store_level not in temp_dict:
                            temp_dict[store_level] = {}
                        temp_dict[store_level][new_key] = block_text
                        match = re.search(self.sub_list_regx, text)
        return text_dict

    def __update_for_process_list(self, tp_dict, new_text, element_list, level, pre_type):
        li_uuids = ""
        # # Store li s first
        for li in element_list:
            new_dict, new_uuid = self.get_new_dict(li, TagTypes.TYPE_LIST_LI, "", True, "")
            tp_dict = self.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)
            li_uuids += "\n" + new_uuid
        # Store ordered/unordered list info
        store_level = level
        if store_level not in tp_dict:
            tp_dict[store_level] = {}

        new_txt = re.sub(r"^\n", "", li_uuids)
        new_dict, new_uuid = self.get_new_dict(new_txt, self.tag_name, pre_type, False, "")
        tp_dict[store_level][new_uuid] = new_dict

        new_text += "\n" + new_uuid

        return tp_dict, new_text, []

    def __process_list(self, list_dict):
        temp_dict = {}
        for level, level_dicts in list_dict.items():
            for key_uuid, old_text in level_dicts.items():
                list_type_pre = ""
                list_type_cur = ""
                element_list = []
                new_uuid = ""
                while old_text != "":
                    old_text = re.sub("^( )*", "", old_text)
                    or_match = re.search(self.ordered_regx, old_text, re.MULTILINE)
                    un_match = re.search(self.unordered_regx, old_text, re.MULTILINE)
                    match_text = ""
                    if or_match:
                        match_text = old_text[:or_match.end()]
                        match_text = re.sub(r"^\n", "", match_text)
                        # match_text = re.sub(r"^( )*", "\n", match_text, flags=re.MULTILINE)
                        # match_text = re.sub(r"^\d\.( )*", "", match_text)
                        old_text = old_text[or_match.end():]
                        list_type_cur = TagTypes.TYPE_LIST_Ol
                    elif un_match:
                        match_text = old_text[:un_match.end()]
                        match_text = re.sub("^\n", "", match_text)
                        # match_text = re.sub(r"^\n( )*", "\n", match_text, flags=re.MULTILINE)
                        # match_text = re.sub(r"^([*\-\+])( )*", "", match_text)
                        list_type_cur = TagTypes.TYPE_LIST_UL
                        old_text = old_text[un_match.end():]
                    if list_type_cur != list_type_pre and list_type_pre != "":
                        temp_dict, new_uuid, element_list = \
                            self.__update_for_process_list(temp_dict, new_uuid, element_list, level, list_type_pre)

                    element_list.append(match_text)
                    list_type_pre = list_type_cur
                temp_dict, new_uuid, element_list = \
                    self.__update_for_process_list(temp_dict, new_uuid, element_list, level, list_type_pre)

                list_dict[level][key_uuid] = re.sub(r"^\n", "", new_uuid)
        for l_level in range(1, len(list_dict.keys())):
            for l_old_uuid, l_new_uuid in list_dict[l_level].items():
                break_flag = False
                for t_level, t_level_dict in temp_dict.items():
                    for t_uuid, t_tag_dict in t_level_dict.items():
                        if l_old_uuid in t_tag_dict[con.KEY_TEXT]:
                            update_text = t_tag_dict[con.KEY_TEXT]
                            update_text = update_text.replace(l_old_uuid, l_new_uuid)
                            temp_dict[t_level][t_uuid][con.KEY_TEXT] = update_text
                            break_flag = True
                        if break_flag:
                            break
                    if break_flag:
                        break
        new_uuid = ""
        for _, replace_text in list_dict[0].items():
            new_uuid = replace_text
        return new_uuid, temp_dict

    def process_tag(self, md_dict):
        # Step 1 Match first block quote
        tp_dict = copy.deepcopy(md_dict)
        # Step 2 Process matched block quote
        md_dict = copy.deepcopy(tp_dict)
        for level, level_dict in md_dict.items():
            for tag_uuid, tag_dict in level_dict.items():
                in_txt = tag_dict[con.KEY_TEXT]

                match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.list_regx, re.MULTILINE)
                while match:

                    # Reformat spaces of list
                    m_txt = self.__reformat_list(m_txt)
                    # Split list block and others parts
                    list_dict = self.__split_sub_list(m_txt)
                    # Process the list
                    new_uuid, list_dict = self.__process_list(list_dict)

                    for _level, _dict in list_dict.items():
                        store_level = level + _level + 1
                        if store_level not in tp_dict.keys():
                            tp_dict[store_level] = {}
                        tp_dict[store_level].update(_dict)
                        del _level, _dict, store_level
                    del list_dict
                    in_txt = b_txt + new_uuid + a_txt
                    tp_dict[level][tag_uuid][con.KEY_TEXT] = in_txt
                    md_dict[level][tag_uuid][con.KEY_TEXT] = in_txt

                    match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.list_regx, re.MULTILINE)
                del match, b_txt, m_txt, a_txt, in_txt
                del tag_uuid, tag_dict
            del level, level_dict
        return tp_dict
