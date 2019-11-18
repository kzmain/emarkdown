from emd.Processor.Block.SymmetryBlockProcessor import SymmetryBlockProcessor
from emd.Processor.Inline.HeaderProcessor import HeaderProcessor
from emd.Processor.Block.BlockQuotesProcessor import BlockQuotesProcessor


class UnionProcessor:
    def __init__(self):
        self.processor_dict = {}
        self.processor_dict["symmetry_block_processor"] = SymmetryBlockProcessor()
        self.processor_dict["header_processor"] = HeaderProcessor()
        self.processor_dict["block_quotes_processor"] = BlockQuotesProcessor()

    def process(self, md_file_uri):
        file = open(md_file_uri, "r")
        md_text = file.read()
        md_dict = {0: {}}
        unmd_dict = {}
        md_dict[0][0] = {"type": "normal_text", "text": md_text}
        self.processor_dict["symmetry_block_processor"].process(md_dict, unmd_dict)
        md_dict = self.processor_dict["block_quotes_processor"].process(md_dict)
        md_dict = self.processor_dict["header_processor"].process(md_dict)

