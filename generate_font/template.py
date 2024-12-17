from PIL import Image, ImageDraw, ImageFont
import csv
from config import *
import os


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


def get_char_chunks(character_data: dict, characters_per_page):
    character_chunks = []
    current_chunk = []
    total_characters = 0
    # Iterate through the characters in character_data
    count = 0
    for char in character_data.keys():
        current_chunk.append(char)
        count += 1
        if count == characters_per_page:
            character_chunks.append(current_chunk)
            current_chunk = []
            total_characters += count
            count = 0

    # Append the remaining characters (if any)
    if current_chunk:
        total_characters += count
        character_chunks.append(current_chunk)

    # Check if all characters were processed
    expected_total = len(character_data)
    assert expected_total == total_characters, "Not all characters were processed!"
    return character_chunks


def create_template(
    output_directory,
    small_box_font,
    font_size,
    character_chunks,
    columns,
    small_box_size,
    large_box_size,
    rows_per_image,
    row_height,
):

    # create output_directory
    os.makedirs(output_directory, exist_ok=True)

    # Load the font
    try:
        font = ImageFont.truetype(small_box_font, font_size)
    except IOError:
        print(f"Failed to load font at {small_box_font}. Ensure the path is correct.")
        raise

    # Create template images
    for page_idx, chunk in enumerate(character_chunks):
        image_width = (
            columns * (small_box_size + large_box_size + 20) + 20
        )  # Total width of the template
        image_height = rows_per_image * row_height  # Total height for 10 rows

        # Create a blank image
        image = Image.new("RGB", (image_width, image_height), "white")
        draw = ImageDraw.Draw(image)

        # Draw the layout
        for i, char in enumerate(chunk):
            row = i // columns
            col = i % columns

            x_offset = col * (small_box_size + large_box_size + 20)
            y_offset = row * row_height + 10

            # Small box (character box)
            small_box_coords = (
                x_offset,
                y_offset,
                x_offset + small_box_size,
                y_offset + small_box_size,
            )
            draw.rectangle(small_box_coords, outline="gray", width=2)

            # Draw character in the small box
            bbox = font.getbbox(char)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = small_box_coords[0] + (small_box_size - text_width) // 2
            text_y = small_box_coords[1] + (small_box_size - text_height) // 2
            draw.text((text_x, text_y), char, fill="black", font=font)

            # Large box (drawing box)
            large_box_coords = (
                x_offset + small_box_size + 20,
                y_offset,
                x_offset + small_box_size + 20 + large_box_size,
                y_offset + large_box_size,
            )
            draw.rectangle(large_box_coords, outline="gray", width=2)

        # Save the image
        output_path = os.path.join(
            output_directory, f"template_page_{page_idx + 1}.png"
        )
        image.save(output_path, format="PNG", optimize=True)
        output_path = os.path.join(
            output_directory, f"template_page_{page_idx + 1}.pdf"
        )
        image.save(output_path, format="PDF", resolution=100.0)
        print(f"Saved template: {output_path}")


if __name__ == "__main__":

    character_data = get_character_data(UNICODE_CSV)
    char_chunks = get_char_chunks(character_data, CHAR_BY_PAGE)
    create_template(
        TEMPLATES_OUT_DIR,
        TEMPLATE_FONT_PATH,
        BOX_FONT_SIZE,
        char_chunks,
        BOX_COL_NUM,
        SMALL_BOX_SIZE,
        LARGE_BOX_SIZE,
        ROWS_BY_PAGE,
        BOX_ROW_HEIGHT,
    )
