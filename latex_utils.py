import os
from os_utils import run_command, check_file_exists
from PIL import Image, ImageFilter
import numpy as np
import random
import re

def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    os.makedirs(folder_name, exist_ok=True)

def create_tex_file(tex_content, filename="document.tex"):
    """Create a .tex file with the given content."""
    base_dir = "generated_data"
    tex_dir = os.path.join(base_dir, "tex")
    create_folder(tex_dir) 
    tex_path = os.path.join(tex_dir, filename)
    with open(tex_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_content)
    return tex_path

def compile_tex_to_pdf(tex_path):
    """Compile a TeX file into a PDF and store the PDF in the 'pdf' subfolder."""
    base_dir = "generated_data"
    pdf_dir = os.path.join(base_dir, "pdf")
    create_folder(pdf_dir) 
    
    tex_dir = os.path.dirname(tex_path)
    tex_filename = os.path.basename(tex_path)
    pdf_filename = os.path.splitext(tex_filename)[0] + ".pdf"    
    pdf_path_temp = os.path.join(tex_dir, pdf_filename)
    pdf_path_final = os.path.join(pdf_dir, pdf_filename)
    
    run_command(f"xelatex -interaction=nonstopmode -output-directory={tex_dir} {tex_path}")

    if not check_file_exists(pdf_path_temp):
        return None
    
    # Delete the existing file at the destination if it exists
    if os.path.exists(pdf_path_final):
        os.remove(pdf_path_final)

    # Move the PDF to the designated folder
    os.rename(pdf_path_temp, pdf_path_final)
    return pdf_path_final

def convert_pdf_to_png(pdf_path, dpi=500):
    """Convert a PDF to PNG format and store the PNG in the 'png' subfolder."""
    base_dir = "generated_data"
    png_dir = os.path.join(base_dir, "png")
    create_folder(png_dir) 

    pdf_filename = os.path.basename(pdf_path)
    png_filename = os.path.splitext(pdf_filename)[0] + ".png" 
    output_path = os.path.join(png_dir, png_filename)

    # Convert the PDF to PNG using pdftoppm
    run_command(f"pdftoppm -r {dpi} {pdf_path} -png -singlefile {output_path[:-4]}")

    return output_path

def delete_aux_files(tex_dir="generated_data/tex"):
    """Delete all auxiliary files in the specified directory."""
    aux_extensions = [".aux", ".log", ".xdv", ".pdf"]
    
    # Iterate over all files in the directory
    for file in os.listdir(tex_dir):
        # Check if the file has an auxiliary extension
        if any(file.endswith(ext) for ext in aux_extensions):
            file_to_delete = os.path.join(tex_dir, file)
            os.remove(file_to_delete)

def crop_pdf(pdf_path, output_pdf=None):
    """Crop a PDF file to remove unnecessary white margins."""
    if not output_pdf:
        # Default cropped output path in the same directory
        output_pdf = pdf_path.replace(".pdf", "-cropped.pdf")
    
    print("Cropping the PDF...")
    run_command(f"pdfcrop {pdf_path} {output_pdf}")
    return output_pdf

def convert_tex_to_pdf(input_dir="generated_data/tex"):
    """Convert all TeX files in the 'tex' subfolder to PDF files."""
    print("Converting TeX files to PDF...")
    tex_files = [f for f in os.listdir(input_dir) if f.endswith(".tex")]

    try:
        for tex_file in tex_files:
            tex_path = os.path.join(input_dir, tex_file)
            compile_tex_to_pdf(tex_path)  # Ensure this raises an exception on failure
    finally:
        delete_aux_files()

def convert_pdf_to_pngs(input_dir="generated_data/pdf"):
    """Convert all PDF files in the 'pdf' subfolder to PNG files."""
    print("Converting PDF files to PNG...")
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]

    for pdf_file in pdf_files:
        convert_pdf_to_png(pdf_file)

def add_headers_to_tex(tex_path, headers):
    """
    Add multiple headers to a TeX file, creating a new file for each header.
    """
    with open(tex_path, "r", encoding="utf-8") as tex_file:
        tex_content = tex_file.read()

    if not tex_content.lstrip().startswith(r"\begin{document}"):
        return
    
    for idx, header in enumerate(headers):
        new_tex_content = header + tex_content
        
        # Generate a new filename based on the index
        new_tex_path = f"{tex_path.rsplit('.', 1)[0]}_{idx + 1}.tex"
        
        with open(new_tex_path, "w", encoding="utf-8") as new_tex_file:
            new_tex_file.write(new_tex_content)
    
    os.remove(tex_path)

def add_headers(tex_dir="generated_data/tex", headers=["\\documentclass{article}\n"]):
    """
    Add headers to all TeX files in the 'tex' subfolder.
    """
    tex_files = [f for f in os.listdir(tex_dir) if f.endswith(".tex")]

    for tex_file in tex_files:
        tex_path = os.path.join(tex_dir, tex_file)
        add_headers_to_tex(tex_path, headers)

def add_mistakes(tex_dir="generated_data/tex"):
    # Get all .tex files in the specified directory
    print("Adding mistakes to TeX files...")
    tex_files = [f for f in os.listdir(tex_dir) if f.endswith(".tex")]
    
    for tex_file in tex_files:
        tex_path = os.path.join(tex_dir, tex_file)
        
        with open(tex_path, "r", encoding="utf-8") as file:
            tex_content = file.read()
        
        content_lines = tex_content.splitlines()
        document_start = next((i for i, line in enumerate(content_lines) if r"\begin{document}" in line), None)
        document_end = next((i for i, line in enumerate(content_lines) if r"\end{document}" in line), None)

        # Ensure \begin{document} and \end{document} exist
        if document_start is None or document_end is None or document_start >= document_end:
            continue
        
        # Get all words between \begin{document} and \end{document}
        text_content = "\n".join(content_lines[document_start + 1:document_end])
        words = re.findall(r'\b\w+\b', text_content)  # Extract all words

        selected_word = random.choice(words)
        
        all_word_positions = list(re.finditer(r'\b\w+\b', text_content))

        random_position = random.choice(all_word_positions)

        start, end = random_position.span()
        modified_text = (
            text_content[:start] +
            rf" \strike{{{selected_word}}} " +
            text_content[start:]
        )
        updated_content_lines = content_lines[:document_start + 1] + \
                                modified_text.splitlines() + \
                                content_lines[document_end:]
        
        with open(tex_path, "w", encoding="utf-8") as file:
            file.write("\n".join(updated_content_lines))
                       
def create_headers(fonts, pagecolors, textcolors):
    """
    Generate a list of LaTeX headers based on fonts, page colors, and text colors.

    Args:
        fonts (list of str): List of font names.
        pagecolors (list of str): List of page background colors.
        textcolors (list of str): List of text colors.

    Returns:
        list of str: A list of LaTeX headers as strings.
    """
    grids = ["", r"""\usepackage{tikz}
\usepackage{eso-pic}
\AddToShipoutPictureBG{
\begin{tikzpicture}[remember picture, overlay]
    \draw[step=5mm, black!20, thin] (current bounding box.south west) grid (current bounding box.north east);
\end{tikzpicture}
}"""]

    headers = []
    for grid in grids:
        for font in fonts:
            for pagecolor in pagecolors:
                for textcolor in textcolors:
                    if pagecolor == textcolor:
                        continue
                    header = r"""\documentclass[varwidth=true, border=10mm]{standalone}
\usepackage{tikz}
\usetikzlibrary{calc}
\newcommand{\strike}[1]{
    \begin{tikzpicture}[baseline=(text.base)]
        \node[inner sep=1pt] (text) {#1};
        \draw[line width=0.8pt] 
            ($(text.west)+(0mm,0.1mm)$) .. controls 
            ($(text.west)+(1.5mm,0.4mm)$) and
            ($(text.center)+(-3mm,-0.1mm)$) ..
            ($(text.center)+(-2mm,0.3mm)$) .. controls
            ($(text.center)+(-1mm,0.1mm)$) and
            ($(text.center)+(1mm,0.4mm)$) ..
            ($(text.center)+(2mm,0.2mm)$) .. controls
            ($(text.center)+(3mm,0.5mm)$) and
            ($(text.east)+(-2mm,0mm)$) ..
            ($(text.east)+(0mm,0.2mm)$);
        \draw[line width=0.8pt] 
            ($(text.west)+(0.2mm,-0.3mm)$) .. controls 
            ($(text.west)+(2mm,-0.1mm)$) and
            ($(text.center)+(-3.5mm,-0.5mm)$) ..
            ($(text.center)+(-1.5mm,-0.2mm)$) .. controls
            ($(text.center)+(0mm,-0.4mm)$) and
            ($(text.center)+(1.5mm,-0.1mm)$) ..
            ($(text.center)+(2.5mm,-0.3mm)$) .. controls
            ($(text.center)+(3.5mm,-0.5mm)$) and
            ($(text.east)+(-1.5mm,-0.2mm)$) ..
            ($(text.east)+(-0.1mm,-0.3mm)$);
    \end{tikzpicture}
}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{mathspec}
\usepackage{xcolor} 
\setmainfont{%s}
\setmathsfont(Digits,Latin){%s}
\pagecolor{%s}
\color{%s}
%s
""" % (font, font, pagecolor, textcolor, grid)
                    headers.append(header)
    return headers

def add_noise_and_blur(folder="generated_data/png", noise_level=100, blur_radius=2):
    print("Adding noise and blur...")
    if not os.path.exists(folder):
        return
    
    png_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    if not png_files:
        return

    for png_file in png_files:
        file_path = os.path.join(folder, png_file)
        base_name, ext = os.path.splitext(png_file)
        
        # Open and convert image to RGB
        img = Image.open(file_path).convert("RGB")
        
        # Create noisy version
        noise = np.random.randint(-noise_level, noise_level, (img.height, img.width, 3), dtype=np.int16)
        noisy_img = np.clip(np.array(img) + noise, 0, 255).astype(np.uint8)
        noisy_img = Image.fromarray(noisy_img)
        
        # Save noisy version
        noisy_file_path = os.path.join(folder, f"{base_name}_noisy{ext}")
        noisy_img.save(noisy_file_path)
        
        # Create and save blurred original
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        blurred_file_path = os.path.join(folder, f"{base_name}_blurred{ext}")
        blurred_img.save(blurred_file_path)
        
        # Create and save blurred noisy version
        blurred_noisy_img = noisy_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        blurred_noisy_file_path = os.path.join(folder, f"{base_name}_noisy_blurred{ext}")
        blurred_noisy_img.save(blurred_noisy_file_path)