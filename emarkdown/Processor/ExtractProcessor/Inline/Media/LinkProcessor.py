# -*- coding: UTF-8 -*-
import copy
import re

from emarkdown.Processor.ExtractProcessor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.Processor.ExtractProcessor.Config import TagConfig as con, TagTypes


class LinkProcessor(MediaProcessor):
    tag_name = TagTypes.TYPE_LINK
    tag_prefix = MediaProcessor.LINK_TAG_PRE

    # Inline-style:
    # @[alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")
    #
    # Reference-style:
    # @[alt text][logo]
    #
    # [logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2"

    def __init__(self):
        super().__init__()
        # TYPE 1: Inline style Link Format like(Most Common One):
        # [link_description](link description)
        self.inline_style_regx = r"(?<!\%s|\%s|\%s)(\[)((\n)?(?!\[|\]).)+(\n?)(\])" \
                                 r"(\()((?! )(.))+" \
                                 r"(( )+\"((?!\").)*\")?( )*(\))" \
                                 % (MediaProcessor.VIDEO_TAG_PRE,
                                    MediaProcessor.AUDIO_TAG_PRE,
                                    MediaProcessor.IMAGE_TAG_PRE)
        # TYPE 2: Brackets style
        # [link_description][reference_name]
        self.brackets_style_regx = r"(?<!\%s|\%s|\%s)((\[)((\n)?(?!\[|\]).)+(\])){2}" \
                                   % (MediaProcessor.VIDEO_TAG_PRE,
                                      MediaProcessor.AUDIO_TAG_PRE,
                                      MediaProcessor.IMAGE_TAG_PRE)
        self.url_only_regx = r"((((https:|http:|ftp:)\/\/))((?! ).)+)|" \
                             r"(www\.)?(((?! |\W).)|\.|\-|\=|\/|\\|\?|\&)+\.(com|net|cn|sh|eu|au|uk|aspx)|" \
                             r"(\d){1,3}\.(\d){1,3}\.(\d){1,3}\.(\d){1,3}|" \
                             r"((\d|\w){3,4}(:){1,2}){4}(\d|\w){3,4}"

    def __process_reference_type(self, md_dicts, ref_dict):
        self.__process_reference_type(md_dicts, ref_dict)

    def __process_inline_type(self, md_dicts):
        self.__process_inline_type(md_dicts)

    def process_tag(self, md_dicts, ref_dict):
        md_dicts = super().process_tag(md_dicts, ref_dict)
        for l_level, l_level_dict in md_dicts.items():
            for l_uuid, tag_dict in l_level_dict.items():
                if self.tag_name == tag_dict[con.KEY_TYPE]:
                    md_dicts[l_level][l_uuid][con.KEY_TEXT] = md_dicts[l_level][l_uuid][con.KEY_EXTENSION][self.KEY_ALT]
                    md_dicts[l_level][l_uuid][con.KEY_EXTENSION][self.KEY_ALT] = ""
        tp_dict = copy.deepcopy(md_dicts)
        for l_level, l_level_dict in md_dicts.items():
            for l_uuid, tag_dict in l_level_dict.items():
                in_txt = md_dicts[l_level][l_uuid][con.KEY_TEXT]
                match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.url_only_regx, re.MULTILINE)
                while match:
                    if "http" in m_txt or "ftp" in m_txt:
                        m_link = m_txt
                    else:
                        m_link = "http://" + m_txt
                    ext_dict = {self.KEY_LINK: m_link,
                                self.KEY_ALT: "",
                                self.KEY_TITLE: ""}
                    new_dict, new_uuid = self.get_new_dict(m_txt, self.tag_name, "", True, ext_dict, None)
                    tp_dict = self.insert_tag_md_dict(tp_dict, l_level, new_uuid, new_dict)
                    in_txt = b_txt + new_uuid + a_txt
                    tp_dict[l_level][l_uuid][con.KEY_TEXT] = in_txt
                    match, b_txt, m_txt, a_txt = self.re_search_get_txt(in_txt, None, self.url_only_regx, re.MULTILINE)
        return tp_dict
