# -*- coding: UTF-8 -*-
from emd.Processor.Config import TagTypes
from emd.Processor.Inline.Media.MediaProcessor import MediaProcessor


class ImageProcessor(MediaProcessor):
    tag_name = TagTypes.TYPE_IMAGE
    tag_prefix = MediaProcessor.IMAGE_TAG_PRE

    # Inline-style:
    # ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")
    # 
    # Reference-style:
    # ![alt text][logo]
    # 
    # [logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2"

    def __init__(self):
        super().__init__()
        # TYPE 1: Inline style Link Format like(Most Common One):
        # ![link_description](link description)
        self.inline_style_regx = self.inline_style_regx % self.tag_prefix
        # TYPE 2: Brackets style
        # ![link_description][reference_name]
        self.brackets_style_regx = self.brackets_style_regx % self.tag_prefix

    def __process_reference_type(self, md_dicts, ref_dict):
        self.__process_reference_type(md_dicts, ref_dict)

    def __process_inline_type(self, md_dicts):
        self.__process_inline_type(md_dicts)

    def process_tag(self, md_dicts, ref_dict):
        return super().process_tag(md_dicts, ref_dict)
