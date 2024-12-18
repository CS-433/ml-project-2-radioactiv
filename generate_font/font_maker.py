import fontforge
import os
from config import *
import psMat
import unicodedata


def process_png_files(svg_dir):
    os.makedirs(svg_dir,exist_ok=True)
    return sorted(
        [f for f in os.listdir(svg_dir) if f.endswith(".svg")],
        key=lambda x: int(x.split("_")[1].split(".")[0]),
    )


def get_character_data(csv_path):
    character_data = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            next(f)
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                unicode_val, char = parts[0], parts[1]
                unicode_code = (
                    int(unicode_val[2:], 16)
                    if unicode_val.startswith(("U+", "0x"))
                    else int(unicode_val, 16)
                )

                if char == "" and unicode_code == 0x002C:
                    char = ","
                character_data[char] = {"unicode": unicode_code}
    except FileNotFoundError:
        print(f"CSV file '{csv_path}' not found.")
        exit(1)
    return character_data


def normalize_glyph_name(unicode_val):
    try:
        glyph_name = unicodedata.name(chr(unicode_val)).lower().replace(" ", "_")
    except ValueError:
        glyph_name = f"uni{unicode_val:04X}"
    return glyph_name


def normalize_data_unicode_values(character_data):
    for char, data in character_data.items():
        unicode_val = data["unicode"]
        glyph_name = normalize_glyph_name(unicode_val)
        character_data[char]["glyph_name"] = glyph_name


def classify_char(char):
    name = unicodedata.name(char, "UNKNOWN")
    category = unicodedata.category(char)

    if "LATIN" in name:
        if char.isupper():
            return f"{char} is an uppercase Latin letter."
        elif char.islower():
            return f"{char} is a lowercase Latin letter."
    elif "GREEK" in name:
        if category == "Lu":
            return f"{char} is an uppercase Greek letter."
        elif category == "Ll":
            return f"{char} is a lowercase Greek letter."
    elif category == "Sm":
        return f"{char} is a math symbol."
    else:
        return f"{char} is unclassified."


def char_has_descender(char):
    descender_latin = {"f", "g", "j", "p", "q", "y", "ÿ", "ý", "ç", "Ç", "ß"}
    descender_greek = {"γ", "η", "μ", "ξ", "φ", "χ", "ψ", "ϐ"}

    if char in descender_latin or char in descender_greek:
        return True

    char_category = unicodedata.category(char)
    if char_category in {"Ll", "Lu"}:
        char_name = unicodedata.name(char, "")
        if "WITH TAIL" in char_name or "WITH DESCENDER" in char_name:
            return True

    return False


def char_has_ascender(char):
    ascender_latin = {"b", "d", "h", "k", "l", "t"}
    ascender_greek = {"Ά", "Ή", "Ί", "Ό", "Ύ", "Ώ", "Η", "Θ", "Λ"}

    if char in ascender_latin or char in ascender_greek:
        return True

    char_category = unicodedata.category(char)
    if char_category in {"Ll", "Lu"}:
        char_name = unicodedata.name(char, "")
        if "WITH ACUTE" in char_name or "WITH DIAERESIS" in char_name:
            return True

    return False

def create_space_glyph(font, width=250):
    """
    Ensure the space glyph exists and set its width.
    Args:
        font: The fontforge font object.
        width: Desired width for the space glyph.
    """
    # Unicode for space character is 0x0020
    space_unicode = 0x0020
    space_glyph_name = "space"

    # Create or access the space glyph
    if space_glyph_name not in font:
        print("Creating space glyph...")
        space_glyph = font.createChar(space_unicode, space_glyph_name)
    else:
        print("Accessing existing space glyph...")
        space_glyph = font[space_unicode]

    # Set the width for the space glyph
    space_glyph.width = width
    print(f"Set space glyph width to {width} units.")

def create_font(
    font_name, author, unicode_map, glyph_files, glyphs_dir, output_font_path
):
    font = fontforge.font()
    font.fontname = font_name
    font.fullname = font_name
    font.familyname = font_name
    font.copyright = f"Copyright 2024, {author}"

    for idx, file in enumerate(glyph_files):
        if idx >= len(unicode_map):
            break

        char = list(unicode_map.keys())[idx]
        glyph_data = unicode_map[char]

        if not isinstance(glyph_data, dict) or "unicode" not in glyph_data:
            print(f"Skipping invalid entry for character '{char}': {glyph_data}")
            continue

        unicode_value = glyph_data["unicode"]
        glyph_path = os.path.join(glyphs_dir, file)

        if not os.path.exists(glyph_path):
            print(f"Warning: Missing SVG for character '{char}' at {glyph_path}")
            continue

        try:
            glyph = font.createChar(unicode_value, char)
            glyph.importOutlines(
                glyph_path, scale=True, simplify=True, accuracy=0.5, correctdir=True
            )

            has_ascender = char_has_ascender(char)
            has_descender = char_has_descender(char)

            classification = classify_char(char)

            # Determine the target height range based on glyph classification
            if "lowercase" in classification:
                target_max_height = 550 if has_ascender else 450
            elif "uppercase" in classification:
                target_max_height = 750 if has_ascender else 700
            elif "math symbol" in classification:
                target_max_height = 500
            else:
                target_max_height = 700

            # Scale glyph to fit within the target max height
            xmin, ymin, xmax, ymax = glyph.boundingBox()
            glyph_height = ymax - ymin

            if glyph_height > target_max_height:
                scale_factor = target_max_height / glyph_height
                glyph.transform(psMat.scale(scale_factor))
                print(
                    f"Scaled {char} by factor {scale_factor:.2f} to fit max height {target_max_height}."
                )

            # Align the glyph horizontally and vertically
            xmin, ymin, xmax, ymax = glyph.boundingBox()

            # Ensure leftmost point is close to zero
            glyph.transform(psMat.translate(-xmin + 5, 0))  # Padding of 5 units

            # Recalculate bounding box
            xmin, ymin, xmax, ymax = glyph.boundingBox()

            # Ensure glyph width does not exceed 500 units
            glyph_width = xmax - xmin
            if glyph_width > 500:
                scale_factor = 500 / glyph_width
                glyph.transform(psMat.scale(scale_factor))
                print(
                    f"Rescaled {char} by factor {scale_factor:.2f} to fit width 500 units."
                )

            # Update the glyph width
            glyph.width = int(xmax - xmin) + 5  # Add 5 units padding on both sides
            

            # Adjust vertical alignment
            xmin, ymin, xmax, ymax = glyph.boundingBox()

            if "math symbol" in classification:
                # Center mathematical symbols vertically
                vertical_center = (ymax + ymin) / 2
                glyph.transform(psMat.translate(0, 250 - vertical_center))
            elif "accent" in classification or char in {"'", "´", "`", "^"}:
                # Ensure accents and apostrophes top align at around 700
                if ymax != 600:
                    adjustment = 600 - ymax
                    glyph.transform(psMat.translate(0, adjustment))
            elif has_descender:
                # Ensure descender aligns with -10
                glyph.transform(psMat.translate(0, -ymin - 100))
            else:
                # Align bottom at 0
                glyph.transform(psMat.translate(0, -ymin))

        except Exception as e:
            print(f"Error processing character '{char}': {e}")
            continue

    # reduce space between chars
    create_space_glyph(font)
    
    font.generate(output_font_path, flags=("opentype"))
    print(f"Font file generated: {output_font_path}")


if __name__ == "__main__":

    # os.system("fontforge -script ./math_font/empty_font.py")
    character_data = get_character_data(UNICODE_CSV)
    glyph_files = process_png_files(GLYPHS_OUT_DIR)
    normalize_data_unicode_values(character_data)

    create_font(
        FONT_NAME, AUTHOR, character_data, glyph_files, GLYPHS_OUT_DIR, TEMP_FONT_PATH
    )
