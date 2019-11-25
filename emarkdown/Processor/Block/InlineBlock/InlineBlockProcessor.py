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
        for l_level, l_level_dict in md_dict.items():
            for l_uuid, tag_dict in l_level_dict.items():
                tag_type = tag_dict[Config.KEY_TYPE]
                if not self.filter(tag_type):
                    continue

                in_txt = tag_dict[Config.KEY_TEXT]
                match, b_txt, m_txt, a_txt = Bp.re_search_get_txt(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
                while match:
                    new_dict, new_uuid = Bp.get_new_dict("", self.tag_name, is_inline=False)
                    tp_dict = Bp.insert_tag_md_dict(tp_dict, l_level, new_uuid, new_dict)

                    in_txt = b_txt + new_uuid + a_txt
                    tp_dict[l_level][l_uuid][Config.KEY_TEXT] = in_txt
                    md_dict[l_level][l_uuid][Config.KEY_TEXT] = in_txt

                    match, b_txt, m_txt, a_txt = Bp.re_search_get_txt(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
        return tp_dict
