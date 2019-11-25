import re
import copy
from emarkdown.Processor.BasicProcessor import BasicProcessor as Bp
from emarkdown.Processor.Config import TagConfig as Config, TagTypes


class BreakLineProcessor(Bp):
    tag_name = TagTypes.TYPE_BREAK_LINE
    tag_regx = r"\n$"

    # Just one loop
    def process_tag(self, md_dicts):
        tp_dict = copy.deepcopy(md_dicts)
        for l_level, l_level_dict in md_dicts.items():
            for t_uuid, tag_dict in l_level_dict.items():
                in_txt = tag_dict[Config.KEY_TEXT]
                match, b_txt, m_txt, a_txt = Bp.re_search_get_text(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
                while match:

                    insert_dict, new_uuid = Bp.get_new_dict("", self.tag_name, is_inline=False)
                    tp_dict = Bp.insert_tag_md_dict(tp_dict, l_level, new_uuid, insert_dict)

                    in_txt = b_txt + new_uuid + a_txt
                    tp_dict[l_level][t_uuid][Config.KEY_TEXT] = in_txt
                    md_dicts[l_level][t_uuid][Config.KEY_TEXT] = in_txt

                    match, b_txt, m_txt, a_txt = Bp.re_search_get_text(in_txt, regx=self.tag_regx, flag=re.MULTILINE)
        return tp_dict
