import cv2
import numpy as np
import svgwrite
from pdf2image import convert_from_path
from skimage.morphology import skeletonize
from wand.image import Image as WandImage
import random
from PIL import Image

# Step 1: Extract images from PDF
def extract_images_from_pdf(pdf_path, zoom_factor=1.2):
    pages = convert_from_path(pdf_path)
    zoomed_pages = []

    for page in pages:
        # Get original image dimensions
        width, height = page.size
        
        # Resize the image to apply zoom
        zoomed_page = page.resize((int(width * zoom_factor), int(height * zoom_factor)), Image.LANCZOS)
        
        zoomed_pages.append(zoomed_page)
    
    return zoomed_pages
# Step 2: Preprocess images (grayscale and thresholding)
def preprocess_image(image):
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY_INV)
    return thresholded

# Step 3: Skeletonize the handwriting
def skeletonize_image(binary_image):
    binary_image = binary_image > 0  # Convert to binary format
    skeleton = skeletonize(binary_image)
    return skeleton

# Step 4: Extract strokes from the skeletonized image
def extract_strokes(skeleton):
    contours, _ = cv2.findContours(skeleton.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    strokes = []
    for contour in contours:
        stroke = [(point[0][0], point[0][1]) for point in contour]
        strokes.append(stroke)
    return strokes

# Step 5.1: Apply jitter effect to strokes
def apply_jitter(strokes, jitter_range=(-2, 2)):
    jittered_strokes = []
    for stroke in strokes:
        jittered_stroke = []
        for point in stroke:
            jitter_x = point[0] + random.uniform(jitter_range[0], jitter_range[1])
            jitter_y = point[1] + random.uniform(jitter_range[0], jitter_range[1])
            jittered_stroke.append((jitter_x, jitter_y))
        jittered_strokes.append(jittered_stroke)
    return jittered_strokes

# Step 5.2: Apply tilt effect to strokes
def apply_tilt(strokes, tilt_angle=5):
    tilt_matrix = np.array([[1, np.tan(np.deg2rad(tilt_angle))], [0, 1]])
    tilted_strokes = []
    for stroke in strokes:
        tilted_stroke = []
        for point in stroke:
            transformed_point = np.dot(tilt_matrix, np.array([point[0], point[1]]))
            tilted_stroke.append((transformed_point[0], transformed_point[1]))
        tilted_strokes.append(tilted_stroke)
    return tilted_strokes

# Step 5.3: Apply pen lift effect to strokes
def apply_pen_lifts(strokes, lift_probability=0.05):
    final_strokes = []
    for stroke in strokes:
        transformed_stroke = []
        for point in stroke:
            if random.random() > lift_probability:
                transformed_stroke.append(point)
        final_strokes.append(transformed_stroke)
    return final_strokes

# Step 5: Apply all transformations to make the strokes more realistic
def apply_handwritten_transformations(strokes, jitter_range=(0, 1), tilt_angle=5, lift_probability=0.05):
    jittered_strokes = apply_jitter(strokes, jitter_range)
    tilted_strokes = apply_tilt(jittered_strokes, tilt_angle)
    final_strokes = apply_pen_lifts(tilted_strokes, lift_probability)
    return final_strokes

# Step 6: Render strokes into an SVG file
def render_strokes_to_svg(strokes, svg_path):
    dwg = svgwrite.Drawing(svg_path, profile='tiny')
    for stroke in strokes:
        if len(stroke) > 1:  # Only consider strokes with multiple points
            path_data = f"M{stroke[0][0]},{stroke[0][1]}"  # Move to the first point
            for point in stroke[1:]:
                path_data += f" L{point[0]},{point[1]}"  # Draw line to each subsequent point
            stroke_width = random.uniform(0.8, 1.5)  # Vary the stroke width for a more natural look
            dwg.add(dwg.path(d=path_data, stroke='black', fill='none', stroke_width=stroke_width))
    dwg.save()

# Step 7: Convert SVG to PNG
def convert_svg_to_png(svg_path, png_path):
    # Using Wand to convert SVG to PNG
    with WandImage(filename=svg_path) as img:
        img.format = 'png'
        img.save(filename=png_path)

# Main function to execute the entire pipeline
def handwrite(pdf_path, svg_output_path, png_output_path):
    # Step 1: Extract images from the PDF
    pages = extract_images_from_pdf(pdf_path)
    
    # Assuming we only work with the first page for simplicity
    first_page = pages[0]
    
    # Step 2: Preprocess the image
    thresholded_image = preprocess_image(first_page)
    
    # Step 3: Skeletonize the image
    skeleton = skeletonize_image(thresholded_image)
    
    # Step 4: Extract strokes from the skeletonized image
    strokes = extract_strokes(skeleton)
    
    # Step 5: Apply transformations to make the strokes more realistic
    transformed_strokes = apply_handwritten_transformations(strokes, jitter_range=(0, 1), tilt_angle=5, lift_probability=0.05)
    
    # Step 6: Render the strokes into an SVG file
    render_strokes_to_svg(transformed_strokes, svg_output_path)
    
    # Step 7: Convert the SVG file to a PNG file
    convert_svg_to_png(svg_output_path, png_output_path)

# Example usage
if __name__ == "__main__":
    pdf_path = './generated_data/pdf/document.pdf'  # Path to your PDF file
    svg_output_path = 'handwriting_strokes.svg'  # Output SVG file path
    png_output_path = 'handwriting_strokes_1.png'  # Output PNG file path
    handwrite(pdf_path, svg_output_path, png_output_path)