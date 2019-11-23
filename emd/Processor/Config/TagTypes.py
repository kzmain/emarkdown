# START
TYPE_START = "start"
# BLOCK TYPE -----------------------------------------------------------------------------------------------------------
# header 需要翻转，list 需要翻转， symmetry_block 需要注意extract info
TYPE_HEADER = "header"
TYPE_HORIZONTAL_RULE = "<hr />"
TYPE_BREAK_LINE = "<br />"

TYPE_LIST = "list"
TYPE_LIST_Ol = "<ol>"
TYPE_LIST_UL = "<ul>"
TYPE_TABLE = "<table>"
TYPE_PARAGRAPH = "<p>"
TYPE_BLOCK_QUOTE = "<blockquote>"

TYPE_SYMMETRY_BLOCK = "symmetry_block"
TYPE_BLUE_TAG = "<div class = \"note blue-note alert-type-%s\" role=\"alert\">"
TYPE_CODE_BLOCK = "CODE_BLOCK"
# INLINE TYPE ----------------------------------------------------------------------------------------------------------
TYPE_TABLE_TR = "<tr>"
TYPE_TABLE_TH = "<th>"
TYPE_TABLE_TD = "<td>"
TYPE_LIST_LI = "<li>"
# ----------------------
TYPE_LINK = "<a href=\"%s\" title=\"%s\">%s</a>"
TYPE_IMAGE = "<img src=\"%s\" alt=\"%s\" title=\"%s\">"
TYPE_AUDIO = "<audio controls>\n" \
             "  <source src=\"%s\" type=\"audio/%s\" alt=\"%s\" title=\"%s\">\n" \
             "Your browser does not support the audio element.\n" \
             "</audio>"
TYPE_VIDEO = "<video width=\"320\" controls>\n" \
             "  <source src=\"%s\" type=\"video/%s\" alt=\"%s\" title=\"%s\">\n" \
             "Your browser does not support the video tag.\n" \
             "</video>"
# 以上不同
TYPE_ITALIC_BOLD = "<b><i>"
TYPE_ITALIC = "<i>"
TYPE_BOLD = "<b>"
TYPE_CODE = "<code>"
TYPE_DELETE = "<del>"
TYPE_SUB = "<sub>"

TYPE_CITATION = "citation"

TYPE_SYMMETRY_INLINE = "symmetry_inline"

# <video width="320" height="240" controls>
#   <source src="movie.mp4" type="video/mp4">
#   <source src="movie.ogg" type="video/ogg">
# Your browser does not support the video tag.
# </video>

# <audio controls>
#   <source src="horse.ogg" type="audio/ogg">
#   <source src="horse.mp3" type="audio/mpeg">
# Your browser does not support the audio element.
# </audio>