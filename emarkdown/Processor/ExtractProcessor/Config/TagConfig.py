from emarkdown.Processor.ExtractProcessor.Config import TagTypes as Tag

CONFIG_TYPE_INLINE_SYMMETRY = "inline_symmetry"
CONFIG_TYPE_BLOCK_SYMMETRY = "block_symmetry"


UNCHANGEABLE_TAG = "unchangeable"
CHANGEABLE_TAG = "changeable"

TAG_REGX = "regx"
TAG_NAME = "tag_name"
TAG_PURE_MD = "is_pure_md"
TAG_BASIC_UNIT = "unit"

CONFIG_DICT = {
    CONFIG_TYPE_INLINE_SYMMETRY: {
        UNCHANGEABLE_TAG: {
            r"`": {
                TAG_REGX: r"`",
                TAG_BASIC_UNIT: r"`",
                TAG_NAME: Tag.TYPE_CODE,
                TAG_PURE_MD: True
            }
        },
        CHANGEABLE_TAG: {
            r"***": {
                TAG_REGX: r"\*\*\*",
                TAG_BASIC_UNIT: r"\*",
                TAG_NAME: Tag.TYPE_ITALIC_BOLD,
                TAG_PURE_MD: True
            },
            r"**": {
                TAG_REGX: r"\*\*",
                TAG_BASIC_UNIT: r"\*",
                TAG_NAME: Tag.TYPE_BOLD,
                TAG_PURE_MD: True
            },
            r"*": {
                TAG_REGX: r"\*",
                TAG_BASIC_UNIT: r"\*",
                TAG_NAME: Tag.TYPE_ITALIC,
                TAG_PURE_MD: True
            },
            r"___": {
                TAG_REGX: r"\_\_\_",
                TAG_BASIC_UNIT: r"\_",
                TAG_NAME: Tag.TYPE_ITALIC_BOLD,
                TAG_PURE_MD: True
            },
            r"__": {
                TAG_REGX: r"\_\_",
                TAG_BASIC_UNIT: r"\_",
                TAG_NAME: Tag.TYPE_BOLD,
                TAG_PURE_MD: True
            },
            r"_": {
                TAG_REGX: r"\_",
                TAG_BASIC_UNIT: r"\_",
                TAG_NAME: Tag.TYPE_ITALIC,
                TAG_PURE_MD: True
            },
            r"~~": {
                TAG_REGX: r"\~\~",
                TAG_BASIC_UNIT: r"\~",
                TAG_NAME: Tag.TYPE_DELETE,
                TAG_PURE_MD: True
            },
            r"~": {
                TAG_REGX: r"\~",
                TAG_BASIC_UNIT: r"\~",
                TAG_NAME: Tag.TYPE_SUB,
                TAG_PURE_MD: False
            }
        }
    },
    CONFIG_TYPE_BLOCK_SYMMETRY: {
        UNCHANGEABLE_TAG: {
            r"```": {
                TAG_REGX: r"```",
                TAG_BASIC_UNIT: r"`",
                TAG_NAME: Tag.TYPE_CODE_BLOCK,
                TAG_PURE_MD: True
            }
        },
        CHANGEABLE_TAG: {
            r"{blue_tag}": {
                TAG_REGX: r"{blue_tag}",
                TAG_BASIC_UNIT: r"{blue_tag}",
                TAG_NAME: Tag.TYPE_BLUE_TAG,
                TAG_PURE_MD: False
            }
        }

    }
}

KEY_TYPE = "type"
KEY_SUB_TYPE = "sub_type"
KEY_TEXT = "text"
KEY_INLINE_FLAG = "inline"
KEY_UUID = "uuid"
KEY_EXTENSION = "extension"

insert_dict = {
    KEY_TYPE: "",
    KEY_SUB_TYPE: "",
    KEY_TEXT: "",
    KEY_INLINE_FLAG: True,
    KEY_UUID: "",
    KEY_EXTENSION: ""
}
