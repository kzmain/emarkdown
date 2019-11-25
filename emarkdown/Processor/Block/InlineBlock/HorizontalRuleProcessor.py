from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp
from emarkdown.Processor.Block.InlineBlock.InlineBlockProcessor import InlineBlockProcessor as Ip
from emarkdown.Processor.Config import TagTypes


class HorizontalRuleProcessor(Bp, Ip):
    tag_name = TagTypes.TYPE_HORIZONTAL_RULE
    tag_regx = r"^((-){3,}|(_){3,}|(\*){3,})$"
    filter_list = [TagTypes.TYPE_BLOCK_QUOTE, TagTypes.TYPE_START, TagTypes.TYPE_SYMMETRY_BLOCK]

    def filter(self, tag_type):
        if tag_type in self.filter_list:
            return True
        else:
            return False
