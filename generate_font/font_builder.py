import os
import glyphs_extraction

if __name__ == "__main__":
    
    glyphs_extraction.main()
    os.system("fontforge -script ./generate_font/font_maker.py")