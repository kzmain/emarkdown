from emarkdown.Processor.ExtractProcessor.Config import TagTypes
from emarkdown.Processor.ExtractProcessor.BasicProcessor import BasicProcessor
from emarkdown.Processor.ExtractProcessor.Block.ListProcessor import ListProcessor
from emarkdown.Processor.ExtractProcessor.Block.TableProcessor import TableProcessor
from emarkdown.Processor.ExtractProcessor.Block.HeaderProcessor import HeaderProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.LinkProcessor import LinkProcessor
from emarkdown.Processor.ExtractProcessor.Inline.CitationProcessor import CitationProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.AudioProcessor import AudioProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.ImageProcessor import ImageProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.MediaProcessor import MediaProcessor
from emarkdown.Processor.ExtractProcessor.Inline.Media.VideoProcessor import VideoProcessor
from emarkdown.Processor.ExtractProcessor.Block.ParagraphProcessor import ParagraphProcessor
from emarkdown.Processor.ExtractProcessor.Block.BlockQuotesProcessor import BlockQuotesProcessor
from emarkdown.Processor.ExtractProcessor.Block.SymmetryBlockProcessor import SymmetryBlockProcessor
from emarkdown.Processor.ExtractProcessor.Inline.SymmetryInlineProcessor import SymmetryInlineProcessor
from emarkdown.Processor.ExtractProcessor.Block.InlineBlock.BreakLineProcessor import BreakLineProcessor
from emarkdown.Processor.ExtractProcessor.Block.InlineBlock.HorizontalRuleProcessor import HorizontalRuleProcessor
from emarkdown.System.Config import Config


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
        md_file = open(md_file_uri, "r")
        md_text = md_file.read()
        if Config.converter_mode == Config.CONVERTER_TYPE_HTML:
            md_text = BasicProcessor.html_pre_process(md_text)
        md_file.close()
        del md_file
        del md_file_uri
        # 准备两个dict储存文件
        md_dict = {}
        unmd_dict = {}
        # 准备初始文件的位置
        # md_dict[0][0] 文章基本位置
        md_dict[0] = {}
        md_dict[0][0] = BasicProcessor.get_new_dict(md_text, TagTypes.TYPE_START, "", False, new_uuid=0)
        del md_text
        # 开始处理不可变区块
        md_dict, unmd_dict = self.processor_dict["symmetry_block_processor"].process_immutable_tag(md_dict, unmd_dict)
        # 开始处理左侧区块 （包括 区块引用模块 及 列表引用模块）
        md_dict, unmd_dict = self.processor_dict["block_quotes_processor"].process_tag(md_dict, unmd_dict)
        # 开始处理列表区块
        md_dict = self.processor_dict["list_processor"].process_tag(md_dict)
        # audio/video/image tag/quotation/link html（避免之前的冲突）/ 在对称区块之前避免Link中文字被处理
        md_dict, ref_dict = self.processor_dict["media_processor"].get_all_reference(md_dict)
        md_dict = self.processor_dict["image_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["audio_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["video_processor"].process_tag(md_dict, ref_dict)
        md_dict = self.processor_dict["link_processor"].process_tag(md_dict, ref_dict)
        del ref_dict
        # 开始处理对称区块（前面需要容忍列表）
        # TODO 改为无需容忍列表
        md_dict = self.processor_dict["symmetry_block_processor"].process_mutable_tag(md_dict)
        # 开始处理表格区块（无需容忍列表）
        md_dict = self.processor_dict["table_block_processor"].process_tag(md_dict)
        # 开始处理inline的区块们
        md_dict, unmd_dict = self.processor_dict["symmetry_inline_processor"].process_immutable_tag(md_dict, unmd_dict)
        md_dict = self.processor_dict["header_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["horizontal_rule_processor"].process_tag(md_dict)
        md_dict, citations_dict = self.processor_dict["citation_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["symmetry_inline_processor"].process_mutable_tag(md_dict)
        md_dict = self.processor_dict["paragraph_processor"].process_tag(md_dict)
        md_dict = self.processor_dict["break_line_processor"].process_tag(md_dict)
        return md_dict, unmd_dict, citations_dict
