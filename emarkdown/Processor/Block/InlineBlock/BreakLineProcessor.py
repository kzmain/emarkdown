import re
import copy
from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp
from emarkdown.Processor.Block.InlineBlock.InlineBlockProcessor import InlineBlockProcessor as Ip
from emarkdown.Processor.Config import TagConfig as Config, TagTypes


class BreakLineProcessor(Bp, Ip):
    tag_name = TagTypes.TYPE_BREAK_LINE
    tag_regx = r"\n$"
    filter_list = []

    def filter(self, tag_type):
        filter_list = self.filter_list
        return True
