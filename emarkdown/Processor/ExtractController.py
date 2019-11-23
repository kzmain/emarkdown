import copy

from emarkdown.Processor.Block.BreakLineProcessor import BreakLineProcessor
from emarkdown.Processor.Block.HorizontalRuleProcessor import HorizontalRuleProcessor
from emarkdown.Processor.Block.ParagraphProcessor import ParagraphProcessor
from emarkdown.Processor.Config import TagConfig as Config, TagTypes
from emarkdown.Processor.Block.BlockQuotesProcessor import BlockQuotesProcessor
from emarkdown.Processor.Block.ListProcessor import ListProcessor
from emarkdown.Processor.Block.SymmetryBlockProcessor import SymmetryBlockProcessor
from emarkdown.Processor.Block.TableProcessor import TableProcessor
from emarkdown.Processor.Inline.CitationProcessor import CitationProcessor
from emarkdown.Processor.Block.HeaderProcessor import HeaderProcessor
from emarkdown.Processor.Inline.Media.AudioProcessor import AudioProcessor
from emarkdown.Processor.Inline.Media.ImageProcessor import ImageProcessor
from emarkdown.Processor.Inline.Media.LinkProcessor import LinkProcessor
from emarkdown.Processor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.Processor.Inline.Media.VideoProcessor import VideoProcessor
from emarkdown.Processor.Inline.SymmetryInlineProcessor import SymmetryInlineProcessor


class ExtractController:
    processor_dict = {}

    def __init__(self):
        self.processor_dict["list_processor"] = ListProcessor()
        self.processor_dict["header_processor"] = HeaderProcessor()
        self.processor_dict["table_block_processor"] = TableProcessor()
        self.processor_dict["block_quotes_processor"] = BlockQuotesProcessor()
        self.processor_dict["symmetry_block_processor"] = SymmetryBlockProcessor()
        self.processor_dict["symmetry_inline_processor"] = SymmetryInlineProcessor()
        self.processor_dict["media_processor"] = MediaProcessor()
        self.processor_dict["image_processor"] = ImageProcessor()
        self.processor_dict["audio_processor"] = AudioProcessor()
        self.processor_dict["video_processor"] = VideoProcessor()
        self.processor_dict["link_processor"] = LinkProcessor()
        self.processor_dict["citation_processor"] = CitationProcessor()
        self.processor_dict["horizontal_rule_processor"] = HorizontalRuleProcessor()
        self.processor_dict["paragraph_processor"] = ParagraphProcessor()
        self.processor_dict["break_line_processor"] = BreakLineProcessor()

    def process(self, md_file_uri):
        # 检查文件可读性，读取文件
        file = open(md_file_uri, "r")
        del md_file_uri
        md_text = file.read()
        file.close()
        del file
        # 准备两个dict储存文件
        md_dict = {}
        unmd_dict = {}
        # 准备初始文件的位置
        # md_dict[0][0] 文章基本位置
        new_dict = copy.deepcopy(Config.insert_dict)
        new_dict[Config.KEY_TEXT] = md_text
        new_dict[Config.KEY_TYPE] = TagTypes.TYPE_START
        new_dict[Config.KEY_INLINE_FLAG] = False
        new_dict[Config.KEY_UUID] = 0
        new_dict[Config.KEY_EXTENSION] = ""
        del md_text
        md_dict[0] = {}
        md_dict[0][0] = new_dict
        del new_dict
        # 开始处理不可变区块
        md_dict, unmd_dict = self.processor_dict["symmetry_block_processor"].process_immutable_tag(md_dict, unmd_dict)
        # 开始处理左侧区块
        md_dict, unmd_dict = self.processor_dict["block_quotes_processor"].process_tag(md_dict, unmd_dict)
        # 开始处理对称区块（前面需要容忍列表）
        md_dict = self.processor_dict["symmetry_block_processor"].process_mutable_tag(md_dict)
        # 开始处理列表区块
        md_dict = self.processor_dict["list_processor"].process_tag(md_dict)
        # 开始处理表格区块（无需容忍列表）
        md_dict = self.processor_dict["table_block_processor"].process_tag(md_dict)

        # 开始处理inline的区块们
        md_dict, unmd_dict = self.processor_dict["symmetry_inline_processor"].process_immutable_tag(md_dict, unmd_dict)
        md_dict = self.processor_dict["header_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["horizontal_rule_processor"].process_tag(md_dict)
        # audio/video/image tag/quotation/link html（避免之前的冲突）/
        ref_dict, md_dict = self.processor_dict["media_processor"].get_all_reference(md_dict)
        md_dict = self.processor_dict["image_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["audio_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["video_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["link_processor"].process_tag(md_dict, ref_dict)
        del ref_dict
        md_dict, citations_dict = self.processor_dict["citation_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["symmetry_inline_processor"].process_mutable_tag(md_dict)
        md_dict = self.processor_dict["paragraph_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["break_line_processor"].process_tag(md_dict)
        return md_dict, unmd_dict, citations_dict
