from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor as Bp
from emarkdown.Processor.ExtractProcessor.Block.InlineBlock.InlineBlockProcessor import InlineBlockProcessor as Ip
from emarkdown.Processor.ExtractProcessor.Config import TagTypes


class BreakLineProcessor(Bp, Ip):
    tag_name = TagTypes.TYPE_BREAK_LINE
    tag_regx = r"\n{2}"
    filter_list = []

    def filter(self, tag_type):
        return True
