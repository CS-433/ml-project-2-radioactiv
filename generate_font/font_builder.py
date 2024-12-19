import os
import glyphs_extraction

if __name__ == "__main__":
    """
    Main script to extract glyphs and generate a font.

    This script performs two main operations:
    1. Runs the `glyphs_extraction.main()` function to process handwriting templates 
       and extract glyphs into the required format (e.g., SVG or PBM files).
    2. Executes a FontForge script (`font_maker.py`) to create a font from the 
       extracted glyphs.

    Dependencies:
    - `glyphs_extraction`: A module containing the logic for glyph extraction.
    - FontForge: Required to run the font generation script.
    """
    # Step 1: Extract glyphs from handwriting templates.
    glyphs_extraction.main()

    # Step 2: Generate the font using FontForge.
    os.system("fontforge -script ./generate_font/font_maker.py")
