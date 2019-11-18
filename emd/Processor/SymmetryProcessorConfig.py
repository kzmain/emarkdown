CONFIG_TYPE_INLINE = "inline"
CONFIG_TYPE_BLOCK = "block"

TAG_TYPE_INLINE = "inline_tag"
TAG_TYPE_BLOCK = "block_tag"

UNCHANGEABLE_TAG = "unchangeable"
CHANGEABLE_TAG = "changeable"

BASIC_UNIT = "unit"

TAG_RIGHT = "right"
TAG_LEFT = "left"

CONFIG = {
    CONFIG_TYPE_INLINE: "",
    CONFIG_TYPE_BLOCK: {
        UNCHANGEABLE_TAG: {
            "```": {
                BASIC_UNIT: "`",
                TAG_TYPE_BLOCK: {TAG_LEFT: "", TAG_RIGHT: ""},
                TAG_TYPE_INLINE: {TAG_LEFT: "", TAG_RIGHT: ""}
            }
        },
        CHANGEABLE_TAG: {

        }

    }
}
