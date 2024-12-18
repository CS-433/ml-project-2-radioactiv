import os
from PIL import Image
import subprocess
import xml.etree.ElementTree as ET
from svg.path import parse_path
from svg.path import Path, Line, CubicBezier, QuadraticBezier, Arc
import re
from pdf2image import convert_from_path
from config import *


# Function to remove borders dynamically
def remove_gray_borders(image, border_color=BORDER_COLOR, border_width=BORDER_WIDTH):
    """
    Removes gray borders from an image.
    :param image: Input image (Pillow Image object).
    :param border_color: The RGB color of the border to remove.
    :param border_width: The width of the border to remove.
    :return: Cropped image without borders.
    """
    # Convert image to RGB if it's not
    image = image.convert("RGB")

    # Get the dimensions of the image
    width, height = image.size

    # Define cropping box (skip the border)
    left = border_width
    top = border_width
    right = width - border_width
    bottom = height - border_width

    # Crop the image to exclude borders
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image


def clean_potrace_svg(input_svg_path, output_svg_path):
    # Parse the SVG file
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Define the SVG namespace
    namespace = {"svg": "http://www.w3.org/2000/svg"}

    # Remove <metadata> and unnecessary tags
    for tag in root.findall("svg:metadata", namespace):
        root.remove(tag)

    # Remove <g> tag and apply its transformations to the <path>
    for g_tag in root.findall("svg:g", namespace):
        transform = g_tag.attrib.get("transform", "")
        for path in g_tag.findall("svg:path", namespace):
            path.attrib.pop("stroke", None)  # Remove unnecessary attributes
            path.attrib.pop("fill", None)
            if transform:
                path.attrib["transform"] = transform
            root.append(path)  # Move the <path> to the root level
        root.remove(g_tag)

    # Save the cleaned SVG
    tree.write(output_svg_path, encoding="utf-8", xml_declaration=True)
    print(f"Cleaned SVG saved to {output_svg_path}")


def apply_transform_to_path(d_attr, translate=(0, 0), scale=(1, 1)):
    """
    Apply translate and scale transformations to the path data (d attribute).
    """
    path = parse_path(d_attr)
    transformed_path = Path()

    for segment in path:
        start = complex(
            segment.start.real * scale[0] + translate[0],
            segment.start.imag * scale[1] + translate[1],
        )
        end = complex(
            segment.end.real * scale[0] + translate[0],
            segment.end.imag * scale[1] + translate[1],
        )

        if isinstance(segment, (Line,)):
            transformed_path.append(Line(start=start, end=end))
        elif isinstance(segment, (CubicBezier, QuadraticBezier)):
            control1 = complex(
                segment.control1.real * scale[0] + translate[0],
                segment.control1.imag * scale[1] + translate[1],
            )
            if isinstance(segment, CubicBezier):
                control2 = complex(
                    segment.control2.real * scale[0] + translate[0],
                    segment.control2.imag * scale[1] + translate[1],
                )
                transformed_path.append(CubicBezier(start, control1, control2, end))
            else:
                transformed_path.append(QuadraticBezier(start, control1, end))
        elif isinstance(segment, Arc):
            # Scale radii and angles for Arc segments
            radius = (
                segment.radius[0] * scale[0],
                segment.radius[1] * scale[1],
            )
            transformed_path.append(
                Arc(
                    start=start,
                    radius=radius,
                    rotation=segment.rotation,
                    arc=segment.arc,
                    sweep=segment.sweep,
                    end=end,
                )
            )
        else:
            # Other path types can be appended as-is
            transformed_path.append(segment)

    return transformed_path.d()


def flatten_svg_transform(input_svg, output_svg):
    """
    Flatten the <g> transformations in the SVG file and apply them to the <path>.
    """
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(input_svg)
    root = tree.getroot()

    namespace = {"svg": "http://www.w3.org/2000/svg"}

    for g_tag in root.findall("svg:g", namespace):
        transform = g_tag.attrib.get("transform", "")
        translate = (0, 0)
        scale = (1, 1)

        # Parse translate and scale from transform attribute
        if "translate" in transform:
            translate_values = re.search(r"translate\(([^)]+)\)", transform).group(1)
            translate = tuple(map(float, translate_values.split(",")))
        if "scale" in transform:
            scale_values = re.search(r"scale\(([^)]+)\)", transform).group(1)
            scale = (
                tuple(map(float, scale_values.split(",")))
                if "," in scale_values
                else (float(scale_values), float(scale_values))
            )

        # Apply transformations to each <path> within <g>
        for path in g_tag.findall("svg:path", namespace):
            d_attr = path.attrib.get("d", "")
            if d_attr:
                # Apply transformations
                path.attrib["d"] = apply_transform_to_path(d_attr, translate, scale)

            # Remove any unnecessary attributes
            path.attrib.pop("fill", None)
            path.attrib.pop("stroke", None)

            # Move path to root
            root.append(path)

        # Remove the <g> tag after processing
        root.remove(g_tag)

    # Save the cleaned SVG
    tree.write(output_svg, encoding="utf-8", xml_declaration=True)
    print(f"Flattened SVG saved to {output_svg}")


def create_out_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)



def get_sorted_templates(template_dir, extension):

    if extension == ".pdf":

        pdf_files = sorted(
            [f for f in os.listdir(template_dir) if f.endswith(extension)],
            key=lambda x: int(
                x.split("_")[-1].split(".")[0]
            ),  # Sort numerically by page
        )

        for pdf_file in pdf_files:
            template_path = os.path.join(template_dir, pdf_file)
            images = convert_from_path(template_path)
            template_path = os.path.join(template_dir, pdf_file)
            template_path = template_path.replace(".pdf", ".png")
            images[0].save(template_path)
            print(f"Saved {pdf_file} as image")

    # Iterate over sorted template files
    template_files = sorted(
        [f for f in os.listdir(template_dir) if f.endswith(".png")],
        key=lambda x: int(x.split("_")[-1].split(".")[0]),  # Sort numerically by page
    )

    return template_files

def preprocess_png(img):
    """
    Preprocess a PNG file to ensure it is binary (black and white).
    """
    img = img.convert("L")  # Convert to grayscale
    binary = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize
    return img

def upscale_image(img,scale_factor=4):
    """
    Upscale the image to improve tracing quality.
    """
    new_size = (img.width * scale_factor, img.height * scale_factor)
    img = img.resize(new_size, Image.LANCZOS)  # Use high-quality scaling
    return img

def remove_background(in_img):
    """
    Removes the white background from an image and makes it transparent.
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the output image.
    """
    # Open the image
    img = in_img.convert("RGBA")  # Ensure image has an alpha channel

    # Load pixel data
    data = img.getdata()
    new_data = []

    for item in data:
        # Check if the pixel is white (you can adjust tolerance here)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            # Replace white with transparency
            new_data.append((255, 255, 255, 0))  # Fully transparent pixel
        else:
            new_data.append(item)

    # Update the image data
    img.putdata(new_data)
    return img

def check_image_bounds(image_path):
    img = Image.open(image_path).convert("L")  # Convert to grayscale
    bbox = img.getbbox()  # Get bounding box of non-zero regions
    if not bbox:
        print(f"Warning: The image at {image_path} has no content!")
    else:
        print(f"The bounding box for {image_path} is {bbox}")

def normalize_image(input_path, output_path, size=(1024, 1024)):
    """
    Normalize the image by resizing and centering it.
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the output image.
        size (tuple): Target size for the image (width, height).
    """
    img = Image.open(input_path).convert("RGBA")

    # Create a blank transparent canvas
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))

    # Resize the glyph proportionally
    img.thumbnail(size, Image.Resampling.LANCZOS)

    # Center the image on the canvas
    x_offset = (size[0] - img.width) // 2
    y_offset = (size[1] - img.height) // 2
    canvas.paste(img, (x_offset, y_offset), img)

    canvas.save(output_path)
    print(f"Normalized image saved to {output_path}")

def extract_glyphs(
    template_dir, template_files, border_color, border_width, output_dir
):
    
    # Constants for grid layout
    columns = BOX_COL_NUM
    rows_per_image = ROWS_BY_PAGE
    small_box_size = SMALL_BOX_SIZE
    large_box_size = LARGE_BOX_SIZE
    row_height = ROW_HEIGHT
    column_width = COL_WIDTH

    # Fixed dimensions for the templates
    template_width = column_width * columns
    template_height = row_height * rows_per_image

    create_out_dir(output_dir)

    idx = 0
    for template_file in template_files:
        print(template_file)
        template_path = os.path.join(template_dir, template_file)

        # Open the template image
        image = Image.open(template_path)
        if image.size != (template_width, template_height):
            # Scale the image to match the fixed dimensions
            image = image.resize(
                (template_width, template_height), Image.Resampling.LANCZOS
            )

        # Process each row and column
        for row in range(rows_per_image):
            for col in range(columns):
                # Calculate the position of the large drawing box
                x_offset = col *column_width + small_box_size + 10
                y_offset = row * row_height
                box_coords = (
                    x_offset,
                    y_offset,
                    x_offset + large_box_size,
                    y_offset + large_box_size,
                )

                # Crop the large box
                glyph_image = image.crop(box_coords)

                # Remove borders dynamically
                glyph_image = remove_gray_borders(
                    glyph_image, border_color, border_width+10
                )

                # Save the cropped glyph image
                glyph_name = f"glyph_{idx}"
                glyph_path = os.path.join(output_dir, glyph_name + ".pbm")
                glyph_image.save(glyph_path)

                svg_path = os.path.join(output_dir, glyph_name + ".svg")

                try:
                    subprocess.run(
                        ["potrace", glyph_path, "-s", "-o", svg_path], check=True
                    )

                    print(f"Converted {glyph_path} to {svg_path}")

                    # Delete the .pbm file after successful conversion
                    os.remove(glyph_path)
                    print(f"Deleted {glyph_path}")

                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")
                    print(f"STDOUT: {e.stdout}")
                    print(f"STDERR: {e.stderr}")
                except FileNotFoundError:
                    print(
                        "Error: 'potrace' command not found. Ensure potrace is installed and in your PATH."
                    )

                
                print(f"Saved glyph to {svg_path}")

                idx += 1

def main():

    filled_templates = get_sorted_templates(FILLED_TEMPLATES_DIR, EXTENSION)
    extract_glyphs(
        FILLED_TEMPLATES_DIR,
        filled_templates,
        BORDER_COLOR,
        BORDER_WIDTH,
        GLYPHS_OUT_DIR,
    )

if __name__ == "__main__":

    main()
