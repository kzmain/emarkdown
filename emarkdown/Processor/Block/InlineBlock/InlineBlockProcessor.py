import copy
import re
from abc import abstractmethod
from emarkdown.Processor.Config import TagConfig as Config
from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp


class InlineBlockProcessor:
    @property
    @abstractmethod
    def tag_name(self):
        return NotImplementedError

    @property
    @abstractmethod
    def tag_regx(self):
        return NotImplementedError

    @property
    @abstractmethod
    def filter_list(self):
        return NotImplementedError

    @abstractmethod
    def filter(self, tag_type):
        return NotImplementedError

    def process_tag(self, md_dict):
        tp_dict = copy.deepcopy(md_dict)
        for level, level_dict in md_dict.items():
            for tag_uuid, tag_dict in level_dict.items():
                tag_type = tag_dict[Config.KEY_TYPE]
                if not self.filter(tag_type):
                    continue

                in_txt = tag_dict[Config.KEY_TEXT]
                match, b_txt, m_txt, a_txt = Bp.re_search_get_txt(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
                while match:
                    new_dict, new_uuid = Bp.get_new_dict("", self.tag_name, is_inline=False)
                    tp_dict = Bp.insert_tag_md_dict(tp_dict, level, new_uuid, new_dict)
                    del new_dict
                    in_txt = b_txt + new_uuid + a_txt
                    tp_dict[level][tag_uuid][Config.KEY_TEXT] = in_txt
                    md_dict[level][tag_uuid][Config.KEY_TEXT] = in_txt

                    match, b_txt, m_txt, a_txt = Bp.re_search_get_txt(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
                    del new_uuid
                del match, b_txt, m_txt, a_txt, in_txt
                del tag_uuid, tag_dict, tag_type
            del level, level_dict
        del md_dict
        return tp_dict
