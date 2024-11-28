import cv2
import numpy as np
import svgwrite
from pdf2image import convert_from_path
from skimage.morphology import skeletonize
from wand.image import Image as WandImage
import random

# Step 1: Extract images from PDF
def extract_images_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    return pages

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
def apply_tilt(strokes, tilt_angle_range=(-3, 3)):
    tilted_strokes = []
    tilt_angle = random.uniform(tilt_angle_range[0], tilt_angle_range[1])
    tilt_matrix = np.array([[1, np.tan(np.deg2rad(tilt_angle))], [0, 1]])
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

# Step 5.4: Apply enhanced curve effect to make straight lines less straight
def apply_curve_effect(strokes, curve_intensity=5):
    curved_strokes = []
    for stroke in strokes:
        if len(stroke) > 2:
            # Identify straight lines by calculating the variance of the slope between consecutive points
            is_straight = True
            slopes = []
            for i in range(1, len(stroke)):
                dx = stroke[i][0] - stroke[i - 1][0]
                dy = stroke[i][1] - stroke[i - 1][1]
                if dx != 0:
                    slopes.append(dy / dx)
            if len(slopes) > 1:
                slope_variance = np.var(slopes)
                if slope_variance > 0.01:  # Threshold to determine if a line is straight
                    is_straight = False

            if is_straight:
                # Apply enhanced curve effect to relatively straight strokes
                curved_stroke = [stroke[0]]
                for i in range(1, len(stroke) - 1):
                    curve_x = stroke[i][0] + random.uniform(-curve_intensity, curve_intensity)
                    curve_y = stroke[i][1] + random.uniform(-curve_intensity, curve_intensity)
                    curved_stroke.append((curve_x, curve_y))
                curved_stroke.append(stroke[-1])
                curved_strokes.append(curved_stroke)
            else:
                curved_strokes.append(stroke)
        else:
            curved_strokes.append(stroke)
    return curved_strokes

# Step 5.5: Apply shift effect to strokes to make everything slightly misaligned
def apply_shift(strokes, shift_range=(-5, 5)):
    shifted_strokes = []
    shift_x = random.uniform(shift_range[0], shift_range[1])
    shift_y = random.uniform(shift_range[0], shift_range[1])
    for stroke in strokes:
        shifted_stroke = [(point[0] + shift_x, point[1] + shift_y) for point in stroke]
        shifted_strokes.append(shifted_stroke)
    return shifted_strokes

# Step 5.6: Reduce the length of straight lines
def reduce_straight_line_length(strokes, reduction_factor=0.8):
    reduced_strokes = []
    for stroke in strokes:
        if len(stroke) > 2:
            # Identify if the stroke is relatively straight
            is_straight = True
            slopes = []
            for i in range(1, len(stroke)):
                dx = stroke[i][0] - stroke[i - 1][0]
                dy = stroke[i][1] - stroke[i - 1][1]
                if dx != 0:
                    slopes.append(dy / dx)
            if len(slopes) > 1:
                slope_variance = np.var(slopes)
                if slope_variance > 0.01:  # Threshold to determine if a line is straight
                    is_straight = False

            if is_straight:
                # Reduce the length of the straight line
                reduced_stroke = [stroke[0]]
                for i in range(1, len(stroke) - 1):
                    reduced_x = stroke[0][0] + reduction_factor * (stroke[i][0] - stroke[0][0])
                    reduced_y = stroke[0][1] + reduction_factor * (stroke[i][1] - stroke[0][1])
                    reduced_stroke.append((reduced_x, reduced_y))
                reduced_stroke.append(stroke[-1])
                reduced_strokes.append(reduced_stroke)
            else:
                reduced_strokes.append(stroke)
        else:
            reduced_strokes.append(stroke)
    return reduced_strokes

# Step 5.7: Rotate characters slightly to simulate handwritten randomness
def apply_rotation(strokes, rotation_angle_range=(-5, 5)):
    rotated_strokes = []
    rotation_angle = random.uniform(rotation_angle_range[0], rotation_angle_range[1])
    rotation_matrix = np.array(
        [[np.cos(np.deg2rad(rotation_angle)), -np.sin(np.deg2rad(rotation_angle))],
         [np.sin(np.deg2rad(rotation_angle)), np.cos(np.deg2rad(rotation_angle))]]
    )
    for stroke in strokes:
        rotated_stroke = []
        for point in stroke:
            rotated_point = np.dot(rotation_matrix, np.array([point[0], point[1]]))
            rotated_stroke.append((rotated_point[0], rotated_point[1]))
        rotated_strokes.append(rotated_stroke)
    return rotated_strokes

# Step 5: Apply all transformations to make the strokes more realistic
def apply_handwritten_transformations(strokes, jitter_range=(-2, 2), tilt_angle_range=(-3, 3), lift_probability=0.05, curve_intensity=5, shift_range=(-5, 5), reduction_factor=0, rotation_angle_range=(-5, 5)):
    jittered_strokes = apply_jitter(strokes, jitter_range)
    tilted_strokes = apply_tilt(jittered_strokes, tilt_angle_range)
    pen_lifted_strokes = apply_pen_lifts(tilted_strokes, lift_probability)
    curved_strokes = apply_curve_effect(pen_lifted_strokes, curve_intensity)
    shifted_strokes = apply_shift(curved_strokes, shift_range)
    reduced_strokes = reduce_straight_line_length(shifted_strokes, reduction_factor)
    rotated_strokes = apply_rotation(reduced_strokes, rotation_angle_range)
    return rotated_strokes

# Step 6: Render strokes into an SVG file
def render_strokes_to_svg(strokes, svg_path):
    # Calculate bounding box to center the strokes
    all_points = [point for stroke in strokes for point in stroke]
    if all_points:
        min_x = min(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_x = max(p[0] for p in all_points)
        max_y = max(p[1] for p in all_points)
        width = max_x - min_x
        height = max_y - min_y
        dwg = svgwrite.Drawing(svg_path, profile='tiny', size=(width + 20, height + 20))
        offset_x = -min_x + 10
        offset_y = -min_y + 10
    else:
        dwg = svgwrite.Drawing(svg_path, profile='tiny')
        offset_x = 0
        offset_y = 0

    for stroke in strokes:
        if len(stroke) > 1:  # Only consider strokes with multiple points
            path_data = f"M{stroke[0][0] + offset_x},{stroke[0][1] + offset_y}"  # Move to the first point
            for point in stroke[1:]:
                path_data += f" L{point[0] + offset_x},{point[1] + offset_y}"  # Draw line to each subsequent point
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
def main(pdf_path, svg_output_path, png_output_path):
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
    transformed_strokes = apply_handwritten_transformations(strokes, jitter_range=(0, 1.5), tilt_angle_range=(-0.05, 0.05), lift_probability=0.1, curve_intensity=10, shift_range=(-2, 2))
    
    # Step 6: Render the strokes into an SVG file
    render_strokes_to_svg(transformed_strokes, svg_output_path)
    
    # Step 7: Convert the SVG file to a PNG file
    convert_svg_to_png(svg_output_path, png_output_path)

# Example usage
if __name__ == "__main__":
    pdf_path = 'test2.pdf'  # Path to your PDF file
    svg_output_path = 'handwriting_strokes.svg'  # Output SVG file path
    png_output_path = 'handwriting_strokes.png'  # Output PNG file path
    main(pdf_path, svg_output_path, png_output_path)
