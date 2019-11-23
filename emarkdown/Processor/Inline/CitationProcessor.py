# -*- coding: UTF-8 -*-
import re

from emarkdown.Processor.BasicProcessor import BasicProcessor
from emarkdown.Processor.Config import TagConfig as con, TagTypes


class CitationProcessor(BasicProcessor):
    tag_name = TagTypes.TYPE_CITATION

    nor_regx = r"^(\n)?(\!)(\(((?!\(|\)).)*\)){7}$"
    web_regx = r"^(\n)?(\!)(\(((?!\(|\)).)*\)){8}$"

    KEY_TYPE = "type"
    KEY_AUTHOR = "author"
    KEY_TITLE = "title"
    KEY_PAGE = "page"
    KEY_EDITION = "edition"
    KEY_DATE_PUBLISH = "publish_date"
    KEY_DATE_ACCESS = "access_date"
    KEY_URL = "url"

    def __init__(self):
        pass

    def process_tag(self, md_dicts):
        citations_dict = {}
        citations_num = 0
        in_text = md_dicts[0][0][con.KEY_TEXT]
        web_match = re.search(self.web_regx, in_text, re.MULTILINE)
        nor_match = re.search(self.nor_regx, in_text, re.MULTILINE)
        while web_match or nor_match:
            insert_dict = {}
            citation_text = ""
            before_text = ""
            after_text = ""
            if web_match:
                before_text = in_text[:web_match.start()]
                after_text = in_text[web_match.end():]
                citation_text = in_text[web_match.start(): web_match.end()]

            elif nor_match:
                before_text = in_text[:nor_match.start()]
                after_text = in_text[nor_match.end():]
                citation_text = in_text[nor_match.start(): nor_match.end()]

            citation_list = citation_text \
                .replace("!(", "", 1) \
                .replace(")", "") \
                .split("(")

            insert_dict[self.KEY_TYPE] = citation_list[0].lower()
            insert_dict[self.KEY_AUTHOR] = citation_list[1]
            insert_dict[self.KEY_TITLE] = citation_list[2]
            insert_dict[self.KEY_PAGE] = citation_list[3].lower()
            insert_dict[self.KEY_EDITION] = citation_list[4]
            insert_dict[self.KEY_DATE_PUBLISH] = citation_list[5].lower()
            insert_dict[self.KEY_DATE_ACCESS] = citation_list[6].lower()

            if web_match:
                insert_dict[self.KEY_URL] = citation_list[7]

            citations_dict[citations_num] = insert_dict
            citations_num += 1

            in_text = before_text + after_text
            web_match = re.search(self.web_regx, in_text, re.MULTILINE)
            nor_match = re.search(self.nor_regx, in_text, re.MULTILINE)
        md_dicts[0][0][con.KEY_TEXT] = in_text
        return md_dicts, citations_dict
