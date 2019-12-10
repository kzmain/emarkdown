import copy
import re
from abc import abstractmethod
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as Tag
from emarkdown.System.Tool import UUID, HTML_Entities


class BasicProcessor:
    @property
    @abstractmethod
    def tag_name(self):
        return NotImplementedError

    @staticmethod
    def html_pre_process(input_text):
        input_text = input_text.replace("&#", HTML_Entities.ENTITY_DICT["&#"])
        input_text = input_text.replace("<", HTML_Entities.ENTITY_DICT["<"])
        input_text = input_text.replace(">", HTML_Entities.ENTITY_DICT[">"])
        input_text = input_text.replace("\"", HTML_Entities.ENTITY_DICT["\""])
        input_text = input_text.replace("\'", HTML_Entities.ENTITY_DICT["\'"])
        return input_text

    @staticmethod
    def get_new_dict(tag_text, tag_type, tag_sub_type="", is_inline=True, tag_extension="", new_uuid=None):
        new_dict = copy.deepcopy(Tag.insert_dict)
        new_dict[Tag.KEY_TEXT] = tag_text
        new_dict[Tag.KEY_TYPE] = tag_type
        new_dict[Tag.KEY_SUB_TYPE] = tag_sub_type
        new_dict[Tag.KEY_INLINE_FLAG] = is_inline
        new_dict[Tag.KEY_EXTENSION] = tag_extension
        if new_uuid is None:
            new_uuid = UUID.get_new_uuid()
            new_dict[Tag.KEY_UUID] = new_uuid
            return new_dict, new_uuid
        else:
            new_dict[Tag.KEY_UUID] = new_uuid
            return new_dict

    @staticmethod
    def insert_tag_md_dict(md_dict, current_level, new_uuid, insert_dict):
        store_level = current_level + 1
        if store_level not in md_dict:
            md_dict[store_level] = {}
        md_dict[store_level][new_uuid] = insert_dict
        return md_dict

    @staticmethod
    def re_search_get_txt(in_text, match=None, regx=None, flag=None):
        if regx is not None and flag is None:
            match = re.search(regx, in_text)
        elif regx is not None and flag is not None:
            match = re.search(regx, in_text, flag)
        b_text = ""
        m_text = ""
        a_text = ""
        if match is not None:
            b_text = in_text[:match.start()]
            m_text = in_text[match.start():match.end()]
            a_text = in_text[match.end():]
        else:
            pass
        return match, b_text, m_text, a_text
