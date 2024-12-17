# Custom Font Generator and Glyph Extraction

This project provides a complete pipeline for creating custom fonts by extracting glyphs from templates, processing them, and generating an OpenType font using FontForge. It allows for the automation of template creation, glyph extraction, and normalization processes.

The project is particularly useful for generating mathematical and symbol-rich fonts by leveraging Python scripts, image processing libraries, and FontForge automation.

This Project is part of the handwriting synthesis project and is used to generate custom fonts for the handwriting synthesis project.


## Overview

This project automates the creation of custom fonts and glyph extraction through the following pipeline:

1. **Template Generation**: Generates templates containing character grids using LaTeX and the Pillow library. These templates include small boxes for text characters and larger boxes for handwritten or graphical glyphs.

2. **Glyph Extraction**: Extracts glyphs from filled templates, processes the images (removing borders, background noise, and scaling), and converts them into vector graphics (SVG format) using Potrace.

3. **Font Creation**: Integrates the cleaned glyphs into an OpenType font file using FontForge. Characters are normalized, scaled, and aligned to ensure consistency.

This pipeline streamlines the process of converting graphical glyphs into usable fonts, with a focus on supporting a variety of Unicode characters, including:
- Latin letters (upper and lowercase)
- Greek letters
- Mathematical symbols
- Special characters

## Key Features

- **Template Generation**
    - Dynamically creates templates containing grids of characters using Pillow.
    - Supports customizable parameters, such as:
        - Font size and grid layout.
        - Small character boxes and large drawing areas for glyph input.
    - Outputs templates as **PNG** and **PDF** files for easy printing.

- **Glyph Extraction**
    - Extracts glyphs from filled templates using image processing techniques:
        - Removes borders dynamically.
        - Ensures binary (black and white) images for clean processing.
        - Upscales images to improve tracing quality.
        - Converts extracted glyphs to vector **SVG** format using Potrace.

- **Font Creation**
    - Generates a custom OpenType font file:
        - Integrates extracted glyphs into their respective Unicode slots.
        - Normalizes, scales, and aligns glyphs for visual consistency.
        - Handles mathematical symbols, Latin, and Greek characters seamlessly.
    - Automates font generation using **FontForge**.

- **Support for Complex Unicode Characters**
    - Uses a CSV mapping (`unicode_to_character_mapping.csv`) to associate Unicode values with their corresponding glyphs.
    - Supports a wide range of characters, including:
        - Latin letters (uppercase and lowercase)
        - Greek letters
        - Mathematical symbols
        - Special and accented characters

- **Highly Customizable**
    - Adjust template dimensions, font styles, grid layouts, and glyph alignment parameters via a centralized configuration file (`config.py`).

## Repository Structure

The project is organized into the following files and directories:

```plaintext
project_root/
│-- config.py                     # Centralized configuration file for template generation and glyph extraction.
│
│-- font_builder.py               # Launches the FontForge script to build the font.
│-- font_maker.py                 # Main script to process glyphs and generate the OpenType font.
│-- glyphs_extraction.py          # Extracts glyphs from filled templates and converts them into SVG files.
│-- template.py                   # Generates templates with character grids for glyph input.
│
└── fonts/                        
    └── latinmodern-math.otf      # Font file used for template generation.

## Key Files 
    1. **config.py**: Contains all configurable parameters, including template layout, font size, grid dimensions, and file paths.
    2. **template.py**: Generates character grid templates as PNG and PDF files for handwritten glyph input.
    3. **glyphs_extraction.py**: Extracts glyphs from filled templates, cleans them, and converts them to vector format using Potrace.
    4. **font_maker.py**: Processes extracted SVG glyphs and integrates them into an OpenType font file.
    5. **font_builder.py**: Entry point to trigger the FontForge script for font creation.
    6. **Unicode_to_Character_Mapping.csv**: Defines the Unicode-to-character mapping for supported glyphs.
    
    ## Directories
    1. **fonts/**: Stores base font files used for template generation.

## Dependencies and Requirements

### System Requirements
- **Operating System**: Windows, (Linux, macOS not working).
- **System Tools**:
  - **FontForge**: For generating OpenType fonts.
  - **Potrace**: For converting bitmap images (PBM) to vector graphics (SVG).

### Python Requirements
The following Python libraries are required:

- **Pillow**: For image processing tasks like cropping, scaling, and background removal.
- **pdf2image**: To convert PDF templates into PNG images.
- **svg.path**: For parsing and manipulating SVG path data.
- **fontforge**: Python interface for FontForge to create fonts.

You can install these dependencies using the following command:

```bash
pip install pillow pdf2image svg.path fontforge
```

## Setup
follow these steps to set up and run the project:
1. install the required dependencies 
2. Ensure the following directories exist for proper execution. Missing directories will be automatically created during runtime:
    - `filled_templates/`: Place filled template images here for glyph extraction.
    - `extracted_glyphs/`: Output directory for extracted SVG glyphs.
    - `character_templates/`: Output directory for generated template grids.
    - `temp_out/`: Temporary directory for font outputs.
    - `fonts/`: Directory containing base fonts for template generation.


3. Generate Character Templates
   To create character grid templates, run the following command:

```bash
python template.py
```

This will generate templates in PNG and PDF formats and save the output in the `character_templates/` directory.

4. Extract Glyphs
   Once you fill the templates with handwritten or graphical content, extract the glyphs by running:

```bash
python glyphs_extraction.py
```

This will process the filled templates, remove borders and backgrounds, and save the extracted glyphs as SVG files in the `extracted_glyphs/` directory.

5. Create the Font
    Generate the final font using FontForge with the following command:

```bash
python font_builder.py
```
This will:
- Process the extracted glyphs from the `extracted_glyphs/` directory.
- Generate a custom OpenType font file in the `temp_out/` directory.

6. Review the Font
    Check the generated font in the `temp_out/` directory. You can install the font on your system to use it in text editors, design software, or other applications.