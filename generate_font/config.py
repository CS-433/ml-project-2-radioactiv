################ TEMPLATE CREATION VARIABLES ##################################################################################
# CONSTANTS
BOX_FONT_SIZE = 50  # Size of the text in the small box
SMALL_BOX_SIZE = 100  # Size of the small box
LARGE_BOX_SIZE = 300  # Size of the large square box
PADDING1 = 20
BOX_ROW_HEIGHT = LARGE_BOX_SIZE + PADDING1  # Height of each row
BOX_COL_NUM = 5  # Number of characters per row

ROWS_BY_PAGE = 10
CHAR_BY_PAGE = BOX_COL_NUM * ROWS_BY_PAGE

ROW_HEIGHT = LARGE_BOX_SIZE + PADDING1  # Total height of each row
COL_WIDTH = SMALL_BOX_SIZE + LARGE_BOX_SIZE + PADDING1  # Total width of each column

TEMPLATE_WIDTH = COL_WIDTH * BOX_COL_NUM
TEMPLATE_HEIGHT = ROW_HEIGHT * ROWS_BY_PAGE

# PATHS
UNICODE_CSV = "math_font/Unicode_to_Character_Mapping.csv"  # Total characters per page
TEMPLATE_FONT_PATH = "fonts/latinmodern-math.otf"
TEMPLATES_OUT_DIR = "character_templates"  # Directory to save templates


################ GLYPH EXTRACTION VARIABLES ##################################################################################

# Gray border color and width
BORDER_COLOR = (128, 128, 128)
BORDER_WIDTH = 2
# Directories
FILLED_TEMPLATES_DIR = "filled_templates"  # Directory containing template images
EXTENSION = ".pdf"
GLYPHS_OUT_DIR = "extracted_glyphs"  # Directory to save extracted glyphs


################ EMPTY FONT BASE VARIABLES ##################################################################################

FONT_NAME = "ML4Science-Math"
AUTHOR = "ML4Science"

################ EMPTY FONT BASE VARIABLES ##################################################################################

TEMP_FONT_PATH = "temp_out/ML4Science-Math.otf"