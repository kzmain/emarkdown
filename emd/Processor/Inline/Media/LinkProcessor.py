# -*- coding: UTF-8 -*-
from emd.Processor.Inline.Media.MediaProcessor import MediaProcessor
from emd.Processor.Config import TagConfig as con, TagTypes


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
        return md_dicts
