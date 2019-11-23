# -*- coding: UTF-8 -*-
import copy
import re

from emd.Processor.BasicProcessor import BasicProcessor
from emd.Processor.Config import TagConfig as con, TagTypes
from emd.System import UUID, HTML_Entities


# List ol/ul放在inline type里了
class ListProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_LIST
    # Match first list line
    # Match first list line's continue sentences
    # Match next line's line signal or normal line
    # list_block_regx = r"(((?<=\n)|(?<!.))(( )*(\*|\-|\+|\d\.))(( )+(?!\n.)(.)*))(((\n)(.)+)*)"
    list_block_regx = r"(((?<=\n)|(?<!.))(( )*(\*|\-|\+|\d\.))(( )+(?!\n)(.)*))(((\n)(.)+)|(\n)(\n)( )+.+|(\n)(\n)(( )*(\*|\-|\+|\d\.))(( )+(?!\n)(.)*))*"
    sub_list_block_regex = r"( ){%d,}(\d.|\*|\-|\+)( )+.*((\n)( ){%d,}.*)*"

    is_list_line_regx = r"((?<=\n)|(?<!\W|\w))( )*(?=(\d.|\*|\-|\+)( )+)"

    # unordered_regx = r"((?<=\n)|(?<!\W|\w))( )*(\*|\-|\+)( )+.+"
    # ordered_regx = r"((?<=\n)|(?<!\W|\w))( )*(\d.)( )+.+"
    # This only match a element of a list
    ordered_regx = r"(\n)?(\d\.)( )+.*(\n(?!(\d\.)|\*).*)*"
    unordered_regx = r"(\n)?(\*|\-|\+)( )+.*(\n(?!(\d\.)|\*).*)*"

    ls_num = 2

    def __init__(self):
        pass

    def __reformat_list(self, input_text):
        # space_num_pre = 0
        space_num = -1
        result_text = ""
        input_text = input_text.replace("\t", "    ")
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
                        line_text = (line_space - space_num - self.ls_num) * HTML_Entities.ENTITY_DICT[" "] + line_text
                elif line_space < space_num and len(line_text) != 0:
                    space_num = (line_space % self.ls_num) + line_space + self.ls_num
                result_text += (space_num * " ") + line_text + "\n"
            # space_num_pre = line_space
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
                    sub_list_block_regx = self.sub_list_block_regex % (self.ls_num * (level + 1), self.ls_num * (level + 1))
                    match = re.search(sub_list_block_regx, text)
                    while match:
                        checking_flag = True
                        new_key = UUID.get_new_uuid()
                        block_text = text[match.start():match.end()]

                        before_text = text[:match.start()]
                        after_text = text[match.end():]
                        # text = text.replace(block_text, new_key, 1)
                        block_text = re.sub("^( ){%d}" % self.ls_num * (level + 1), "", block_text)
                        block_text = re.sub("(\n( ){%d})" % self.ls_num * (level + 2), "\n", block_text)

                        text = before_text + " " * self.ls_num + new_key + after_text
                        text_dict[level][key_uuid] = text
                        temp_dict[level][key_uuid] = text
                        store_level = level + 1
                        if store_level not in temp_dict:
                            temp_dict[store_level] = {}
                        temp_dict[store_level][new_key] = block_text
                        match = re.search(self.sub_list_block_regex, text)
        return text_dict

    def __update_for_process_list(self, temp_dict, new_text, element_list, level, pre_type):
        new_list_text = ""
        # Store li s first
        store_level = level + 1
        if store_level not in temp_dict:
            temp_dict[store_level] = {}

        for li in element_list:
            new_insert_dict = copy.deepcopy(con.insert_dict)
            li_uuid = UUID.get_new_uuid()
            new_insert_dict[con.KEY_UUID] = li_uuid
            new_insert_dict[con.KEY_EXTENSION] = ""
            new_insert_dict[con.KEY_INLINE_FLAG] = True
            new_insert_dict[con.KEY_TEXT] = li
            new_insert_dict[con.KEY_TYPE] = TagTypes.TYPE_LIST_LI

            temp_dict[store_level][li_uuid] = new_insert_dict
            new_list_text += "\n" + li_uuid
        li_list = []
        # Store ordered/unordered list info
        store_level = level
        if store_level not in temp_dict:
            temp_dict[store_level] = {}

        new_insert_dict = copy.deepcopy(con.insert_dict)
        li_uuid = UUID.get_new_uuid()
        new_insert_dict[con.KEY_UUID] = li_uuid
        new_insert_dict[con.KEY_EXTENSION] = ""
        new_insert_dict[con.KEY_SUB_TYPE] = pre_type
        new_insert_dict[con.KEY_INLINE_FLAG] = False
        new_insert_dict[con.KEY_TEXT] = re.sub(r"^\n", "", new_list_text)
        new_insert_dict[con.KEY_TYPE] = self.tag_name
        temp_dict[store_level][li_uuid] = new_insert_dict

        new_text += "\n" + li_uuid

        return temp_dict, new_text, li_list

    def __process_list(self, list_dict):
        temp_dict = {}
        for level, level_dicts in list_dict.items():
            for key_uuid, old_text in level_dicts.items():
                list_type_pre = ""
                list_type_cur = ""
                element_list = []
                new_text = ""
                while old_text != "":
                    old_text = re.sub("^( )*", "", old_text)
                    or_match = re.match(self.ordered_regx, old_text)
                    un_match = re.match(self.unordered_regx, old_text)
                    match_text = ""
                    if or_match:
                        match_text = old_text[:or_match.end()]
                        match_text = re.sub(r"^\n", "", match_text)
                        # match_text = re.sub(r"^\d\.( )*", "", match_text)
                        old_text = old_text[or_match.end():]
                        list_type_cur = TagTypes.TYPE_LIST_Ol
                    elif un_match:
                        match_text = old_text[:un_match.end()]
                        match_text = re.sub("^\n", "", match_text)
                        # match_text = re.sub(r"^([*\-\+])( )*", "", match_text)
                        list_type_cur = TagTypes.TYPE_LIST_UL
                        old_text = old_text[un_match.end():]
                    if list_type_cur != list_type_pre and list_type_pre != "":
                        temp_dict, new_text, element_list = \
                            self.__update_for_process_list(temp_dict, new_text, element_list, level, list_type_pre)

                    element_list.append(match_text)
                    list_type_pre = list_type_cur
                temp_dict, new_text, element_list = \
                    self.__update_for_process_list(temp_dict, new_text, element_list, level, list_type_pre)

                list_dict[level][key_uuid] = re.sub(r"^\n", "", new_text)
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
        new_text = ""
        for _, replace_text in list_dict[0].items():
            new_text = replace_text
        return new_text, temp_dict
        # Test code
        # while len(temp_dict) != 0:
        #     tt_dict = copy.deepcopy(temp_dict)
        #
        #     for t_level, t_level_dict in temp_dict.items():
        #         for t_uuid, t_tag_dict in t_level_dict.items():
        #             text_n = t_tag_dict[con.KEY_TEXT]
        #             if t_uuid in new_text:
        #                 new_text = new_text.replace(t_uuid, (t_level - 1) * "  " + text_n)
        #                 tt_dict[t_level].pop(t_uuid)
        #             if len(tt_dict[t_level]) == 0:
        #                 tt_dict.pop(t_level)
        #     temp_dict = copy.deepcopy(tt_dict)

    def process_tag(self, md_dicts):
        # Step 1 Match first block quote
        update_dict = copy.deepcopy(md_dicts)
        # Step 2 Process matched block quote
        md_dicts = copy.deepcopy(update_dict)
        for level, level_dict in md_dicts.items():
            for key_uuid, text_dict in level_dict.items():
                input_text = text_dict[con.KEY_TEXT]
                match = re.search(self.list_block_regx, input_text, re.MULTILINE)
                while match:
                    # Split list block and others parts
                    before_text = input_text[:match.start()]
                    after_text = input_text[match.end():]

                    match_text = input_text[match.start():match.end()]
                    match_text = self.__reformat_list(match_text)

                    list_dict = self.__split_sub_list(match_text)
                    match_text, list_dict = self.__process_list(list_dict)

                    for l_level in range(0, len(list_dict)):
                        for tag_uuid, tag_dict in list_dict[l_level].items():
                            store_level = level + l_level + 1
                            if store_level not in update_dict:
                                update_dict[store_level] = {}
                            update_dict[store_level][tag_uuid] = tag_dict
                    input_text = before_text + match_text + after_text
                    update_dict[level][key_uuid][con.KEY_TEXT] = input_text
                    md_dicts[level][key_uuid] = input_text
                    match = re.search(self.list_block_regx, input_text, re.MULTILINE)
        return update_dict
        # # update_dict
        # input_text = ""
        # for _, replace_text in update_dict[0].items():
        #     input_text = replace_text
        #
        # while len(update_dict) != 1:
        #     tt_dict = copy.deepcopy(update_dict)
        #
        #     for t_level, t_level_dict in update_dict.items():
        #         if t_level == 0: continue
        #         for t_uuid, t_tag_dict in t_level_dict.items():
        #             text_n = t_tag_dict[con.KEY_TEXT]
        #             if t_uuid in input_text:
        #                 input_text = input_text.replace(t_uuid, (t_level - 2) * "  " + text_n)
        #                 tt_dict[t_level].pop(t_uuid)
        #             if len(tt_dict[t_level]) == 0:
        #                 tt_dict.pop(t_level)
        #     update_dict = copy.deepcopy(tt_dict)
        # print()
