import copy
import re
from abc import abstractmethod
from emarkdown.Processor.Config import TagConfig as con
from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.System import UUID, HTML_Entities


class MediaProcessor(BasicProcessor):
    KEY_LINK = "src"
    KEY_ALT = "alt"
    KEY_TITLE = "title"
    KEY_REF_NAME = 'ref_name'

    IMAGE_TAG_PRE = "!"
    AUDIO_TAG_PRE = "@"
    VIDEO_TAG_PRE = "$"
    LINK_TAG_PRE = ""

    def __init__(self):
        # TYPE 1: Inline style Link Format like(Most Common One):
        # %s[link_description](link description)
        self.inline_style_regx = r"(\%s)(\[)((\n)?(?!\[|\]).)+(\n?)(\])" \
                                 r"(\()((?! )(.))+" \
                                 r"(( )+\"((?!\").)*\")?( )*(\))"
        # TYPE 2: Brackets style
        # %s[link_description][reference_name]
        self.brackets_style_regx = r"(\%s)((\[)((\n)?(?!\[|\]).)+(\])){2}"

    @property
    @abstractmethod
    def tag_name(self):
        pass

    @property
    @abstractmethod
    def tag_prefix(self):
        pass

    # Used to match reference
    # @[reference_name]: link "Description"
    # @[reference_name]: link
    reference_regx = r"^(\n)?(\[)((\n)?(?!\[|\]).)+(\n?)(\])" \
                     r"( )*(:)( )*" \
                     r"((?! )(.))+(( )+\"((?!\")(.))+\"( )*)?"

    def get_all_reference(self, md_dicts):
        ref_dict = {}
        input_text = md_dicts[0][0][con.KEY_TEXT]
        reference_match = re.search(self.reference_regx, input_text, re.MULTILINE)
        while reference_match:
            before_text = input_text[:reference_match.start()]
            after_text = input_text[reference_match.end():]

            match_text = input_text[reference_match.start():reference_match.end()]
            # @TODO 这个可能会提关掉输入的空格
            match_text = re.sub(r"( )+", " ", match_text)
            match_text = re.sub(r"\n", "", match_text)
            reference_list = match_text.split(" ", 2)
            reference_name = reference_list[0].replace("[", "").replace("]:", "").replace("\n", "").lower()
            link = reference_list[1]
            title = reference_list[2].replace("\"", "").replace("\n", "").lower()

            ref_dict[reference_name] = {self.KEY_LINK: link,
                                        self.KEY_REF_NAME: reference_name,
                                        self.KEY_TITLE: title}

            input_text = before_text + after_text
            reference_match = re.search(self.reference_regx, input_text, re.MULTILINE)
        md_dicts[0][0][con.KEY_TEXT] = input_text
        return md_dicts, ref_dict

    @abstractmethod
    def process_tag(self, md_dicts, ref_dict):
        md_dicts = self.__process_inline_type(md_dicts)
        md_dicts = self.__process_reference_type(md_dicts, ref_dict)
        return md_dicts

    @abstractmethod
    def __process_reference_type(self, md_dicts, ref_dict):
        tp_dicts = copy.deepcopy(md_dicts)
        for l_level, l_level_dicts in md_dicts.items():
            for l_uuid, tag_dict in l_level_dicts.items():
                input_text = tag_dict[con.KEY_TEXT]
                ref_match = re.search(self.brackets_style_regx, input_text, re.MULTILINE)
                while ref_match:
                    raw_text = input_text[ref_match.start(): ref_match.end()]
                    before_text = input_text[:ref_match.start()]
                    after_text = input_text[ref_match.end():]
                    match_text = raw_text.replace(self.tag_prefix, "").replace("]", "").replace("[", "", 1)
                    info_list = match_text.split("[")

                    reference_text = info_list[1].replace("\n", "").lower()
                    alt_text = info_list[1].replace("\n", "").lower()

                    if reference_text in ref_dict.keys():
                        new_uuid = UUID.get_new_uuid()
                        insert_dict = copy.deepcopy(con.insert_dict)
                        insert_dict[con.KEY_INLINE_FLAG] = True
                        insert_dict[con.KEY_TYPE] = self.tag_name
                        insert_dict[con.KEY_TEXT] = ""
                        insert_dict[con.KEY_EXTENSION] = {
                            self.KEY_LINK: ref_dict[reference_text][self.KEY_LINK],
                            self.KEY_ALT: alt_text,
                            self.KEY_TITLE: ref_dict[reference_text][self.KEY_TITLE]}
                        insert_dict[con.KEY_UUID] = new_uuid

                        store_level = l_level + 1
                        if store_level not in tp_dicts:
                            tp_dicts[store_level] = {}
                        tp_dicts[store_level][new_uuid] = insert_dict

                        input_text = before_text + new_uuid + after_text
                    else:
                        raw_text = raw_text.replace("[", HTML_Entities.ENTITY_DICT["["])
                        raw_text = raw_text.replace("]", HTML_Entities.ENTITY_DICT["]"])
                        raw_text = raw_text.replace(self.tag_prefix, HTML_Entities.ENTITY_DICT[self.tag_prefix])
                        input_text = before_text + raw_text + after_text
                    tp_dicts[l_level][l_uuid][con.KEY_TEXT] = input_text
                    md_dicts[l_level][l_uuid][con.KEY_TEXT] = input_text
                    ref_match = re.search(self.brackets_style_regx, input_text, re.MULTILINE)
        return tp_dicts

    @abstractmethod
    def __process_inline_type(self, md_dicts):
        tp_dicts = copy.deepcopy(md_dicts)
        for l_level, l_level_dicts in md_dicts.items():
            for l_uuid, tag_dict in l_level_dicts.items():
                input_text = tag_dict[con.KEY_TEXT]
                inline_match = re.search(self.inline_style_regx, input_text, re.MULTILINE)
                while inline_match:
                    match_text = input_text[inline_match.start(): inline_match.end()]
                    before_text = input_text[:inline_match.start()]
                    after_text = input_text[inline_match.end():]
                    # related_info[0] => description_text/related_info[1] => link + title
                    related_info = match_text \
                        .replace(self.tag_prefix, "", 1) \
                        .replace("[", "") \
                        .replace("]", "") \
                        .replace(")", "") \
                        .split("(", 1)
                    description_text = re.sub("^( )*", "", related_info[0]) \
                        .replace("\n", "") \
                        .lower()
                    related_info[1] = re.sub("^( )*", "", related_info[1].replace("\"", ""))

                    link_title_list = related_info[1].split(" ", 1)
                    link_text = link_title_list[0].replace("\n", "").lower()

                    try:
                        title = re.sub("^( )*", "", link_title_list[1].replace("\n", "").lower())
                    except IndexError:
                        title = ""

                    new_uuid = UUID.get_new_uuid()
                    insert_dict = copy.deepcopy(con.insert_dict)
                    insert_dict[con.KEY_INLINE_FLAG] = True
                    insert_dict[con.KEY_TYPE] = self.tag_name
                    insert_dict[con.KEY_TEXT] = ""
                    insert_dict[con.KEY_EXTENSION] = {self.KEY_LINK: link_text,
                                                      self.KEY_ALT: description_text,
                                                      self.KEY_TITLE: title}
                    insert_dict[con.KEY_UUID] = new_uuid

                    store_level = l_level + 1
                    if store_level not in tp_dicts:
                        tp_dicts[store_level] = {}
                    tp_dicts[store_level][new_uuid] = insert_dict

                    input_text = before_text + new_uuid + after_text
                    tp_dicts[l_level][l_uuid][con.KEY_TEXT] = input_text
                    md_dicts[l_level][l_uuid][con.KEY_TEXT] = input_text

                    inline_match = re.search(self.inline_style_regx, input_text, re.MULTILINE)
        return tp_dicts
