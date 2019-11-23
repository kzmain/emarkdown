from emd.Processor.Config import TagTypes

CONFIG_TYPE_INLINE_SYMMETRY = "inline_symmetry"
CONFIG_TYPE_BLOCK_SYMMETRY = "block_symmetry"

TAG_NAME = "tag_name"

UNCHANGEABLE_TAG = "unchangeable"
CHANGEABLE_TAG = "changeable"

BASIC_UNIT = "unit"

TAG_RIGHT = "right"
TAG_LEFT = "left"
TAG_REGX = "regx"

CONFIG_DICT = {
    CONFIG_TYPE_INLINE_SYMMETRY: {
        UNCHANGEABLE_TAG: {
            r"`": {
                TAG_REGX: r"`",
                BASIC_UNIT: r"`",
                TAG_NAME: TagTypes.TYPE_CODE
            }
        },
        CHANGEABLE_TAG: {
            r"***": {
                TAG_REGX: r"\*\*\*",
                BASIC_UNIT: r"\*",
                TAG_NAME: TagTypes.TYPE_ITALIC_BOLD
            },
            r"**": {
                TAG_REGX: r"\*\*",
                BASIC_UNIT: r"\*",
                TAG_NAME: TagTypes.TYPE_BOLD
            },
            r"*": {
                TAG_REGX: r"\*",
                BASIC_UNIT: r"\*",
                TAG_NAME: TagTypes.TYPE_ITALIC
            },
            r"___": {
                TAG_REGX: r"\_\_\_",
                BASIC_UNIT: r"\_",
                TAG_NAME: TagTypes.TYPE_ITALIC_BOLD
            },
            r"__": {
                TAG_REGX: r"\_\_",
                BASIC_UNIT: r"\_",
                TAG_NAME: TagTypes.TYPE_BOLD
            },
            r"_": {
                TAG_REGX: r"\_",
                BASIC_UNIT: r"\_",
                TAG_NAME: TagTypes.TYPE_ITALIC
            },
            r"~~": {
                TAG_REGX: r"\~\~",
                BASIC_UNIT: r"\~",
                TAG_NAME: TagTypes.TYPE_DELETE
            },
            r"~": {
                TAG_REGX: r"\~",
                BASIC_UNIT: r"\~",
                TAG_NAME: TagTypes.TYPE_SUB
            }
        }
    },
    CONFIG_TYPE_BLOCK_SYMMETRY: {
        UNCHANGEABLE_TAG: {
            r"```": {
                TAG_REGX: r"```",
                BASIC_UNIT: r"`",
                TAG_NAME: TagTypes.TYPE_CODE_BLOCK
            }
        },
        CHANGEABLE_TAG: {
            r"{blue_tag}": {
                TAG_REGX: r"{blue_tag}",
                BASIC_UNIT: r"{blue_tag}",
                TAG_NAME: TagTypes.TYPE_BLUE_TAG
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
