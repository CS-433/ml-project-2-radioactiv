import os
import subprocess

import openai
from string import Template

from os_utils import run_command, check_file_exists


def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    os.makedirs(folder_name, exist_ok=True)




def create_tex_file(tex_content, filename="document.tex_content", base_dir="generated_data"):
    """Create a .tex_content file with the given content."""

    tex_dir = os.path.join(base_dir, "tex_content")
    create_folder(tex_dir)  # Ensure the folder exists
    tex_path = os.path.join(tex_dir, filename)
    with open(tex_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_content)
    return tex_path


def compile_texfile_to_pdf(tex_path, base_dir="generated_data"):
    """Compile a TeX file into a PDF and store the PDF in the 'pdf' subfolder."""
    pdf_dir = os.path.join(base_dir, "pdf")
    create_folder(pdf_dir)  # Ensure the folder exists

    tex_dir = os.path.dirname(tex_path)
    pdf_filename = "document.pdf"
    pdf_path_temp = os.path.join(tex_dir, pdf_filename)
    pdf_path_final = os.path.join(pdf_dir, pdf_filename)

    print("Compiling TeX to PDF...")
    run_command(
        f"xelatex -interaction=nonstopmode -no-pdf -output-directory={tex_dir} {tex_path}"
    )
    run_command(
        f"xelatex -interaction=nonstopmode -output-directory={tex_dir} {tex_path}"
    )

    if not check_file_exists(pdf_path_temp):
        print("PDF was not created successfully.")
        return None

    # Delete the existing file at the destination if it exists
    if os.path.exists(pdf_path_final):
        os.remove(pdf_path_final)

    # Move the PDF to the designated folder
    os.rename(pdf_path_temp, pdf_path_final)
    return pdf_path_final


def convert_pdf_to_png(pdf_path, output_png_name="document.png", out_dir="generated_data"):

    create_folder(out_dir)  # Ensure the folder exists

    # if output does not have png extension, add it
    if not output_png_name.endswith(".png"):
        output_png_name += ".png"

    output_path = os.path.join(out_dir, output_png_name)
    print("Converting PDF to PNG...")
    try:
        run_command(f"pdftoppm {pdf_path} -png -singlefile {output_path[:-4]}")
    except Exception as e:
        print(f"Error converting PDF to PNG: {e}")
        return None
    return output_path


def delete_aux_files(tex_path):
    """Delete auxiliary files generated during LaTeX compilation."""
    aux_extensions = [".aux", ".log", ".xdv"]
    tex_dir = os.path.dirname(tex_path)
    tex_filename = os.path.splitext(os.path.basename(tex_path))[0]

    for ext in aux_extensions:
        file_to_delete = os.path.join(tex_dir, tex_filename + ext)
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
            print(f"Deleted: {file_to_delete}")


def crop_pdf(pdf_path, output_pdf=None):
    """Crop a PDF file to remove unnecessary white margins."""
    if not output_pdf:
        # Default cropped output path in the same directory
        output_pdf = pdf_path.replace(".pdf", "-cropped.pdf")

    print("Cropping the PDF...")
    run_command(f"pdfcrop {pdf_path} {output_pdf}")
    return output_pdf

def get_tex_template_with_custom_font():
    pass


def get_tex_template(
        content: str,
        mainfont: str = "Times New Roman",
        mathsfont: str = "Times New Roman",
        text_color: str = "black",
        background_color: str = "white",
        grid: bool = False
) -> str:
    """
    Generate a LaTeX template with specified font settings, colors, grid, strike functionality, and content using string.Template.

    :param content: The LaTeX content to include in the document
    :param mainfont: The main font to use for the document
    :param mathsfont: The math font to use for equations
    :param text_color: The color to use for the text
    :param background_color: The color to use for the page background
    :param grid: If True, includes a grid overlay on the page
    :return: A formatted LaTeX string
    """

    # LaTeX code for the grid, only added if grid=True
    grid_code = r"""
    \usepackage{tikz}
    \usepackage{eso-pic}
    \AddToShipoutPictureBG{
    \begin{tikzpicture}[remember picture, overlay]
        \draw[step=5mm, black!20, thin] 
            (current bounding box.south west) 
            grid 
            (current bounding box.north east);
    \end{tikzpicture}
    }
    """ if grid else ""

    # LaTeX code for the strike-through functionality
    strike_code = r"""
    \newcommand{\simplestrike}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};
            \draw[line width=0.6pt] 
                ($(text.west)+(0mm,0.2mm)$) 
                .. controls ($(text.west)+(0.5cm,0.5mm)$) and ($(text.center)+(-2mm,0.7mm)$) ..
                ($(text.center)+(-1mm,-0.2mm)$) 
                .. controls ($(text.center)+(1mm,0.5mm)$) and ($(text.center)+(3mm,-0.6mm)$) ..
                ($(text.center)+(2mm,-0.3mm)$) 
                .. controls ($(text.east)+(-0.5cm,0.4mm)$) and ($(text.east)+(-0.2cm,-0.5mm)$) ..
                ($(text.east)+(0mm,0.1mm)$);
        \end{tikzpicture}
    }
    \newcommand{\scribblestrike}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};        
            \draw[line width=1pt] 
                ($(text.west)+(-0.2mm,0.4mm)$) .. controls 
                ($(text.west)+(1mm,1mm)$) and 
                ($(text.center)+(-2mm,0mm)$) ..
                ($(text.center)+(0mm,1mm)$) .. controls
                ($(text.center)+(2mm,2mm)$) and 
                ($(text.east)+(-2mm,0.5mm)$) ..
                ($(text.east)+(0.2mm,1mm)$);
            \draw[line width=1pt] 
                ($(text.west)+(0mm,-0.2mm)$) .. controls 
                ($(text.west)+(1.5mm,-0.5mm)$) and 
                ($(text.center)+(-1mm,-1mm)$) ..
                ($(text.center)+(1mm,-0.5mm)$) .. controls
                ($(text.center)+(3mm,-0.7mm)$) and 
                ($(text.east)+(-1mm,-0.3mm)$) ..
                ($(text.east)+(0.5mm,-0.5mm)$);
            \draw[line width=1pt] 
                ($(text.west)+(0mm,0mm)$) .. controls 
                ($(text.west)+(1mm,0.3mm)$) and 
                ($(text.center)+(-1.5mm,-0.2mm)$) ..
                ($(text.center)+(0mm,0.2mm)$) .. controls
                ($(text.center)+(1.5mm,0.4mm)$) and 
                ($(text.east)+(-1.5mm,0.1mm)$) ..
                ($(text.east)+(0.5mm,-0.5mm)$);
        \end{tikzpicture}
    }
    \newcommand{\mistake}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};
            \draw[line width=1pt] 
                ($(text.west)+(-0.2mm,0.4mm)$) .. controls 
                ($(text.west)+(1mm,1mm)$) and 
                ($(text.center)+(-2mm,0mm)$) ..
                ($(text.center)+(0mm,0mm)$) .. controls
                ($(text.center)+(2mm,-1mm)$) and 
                ($(text.east)+(-2mm,0.5mm)$) ..
                ($(text.east)+(0.2mm,1mm)$);
            \draw[line width=1pt] 
                ($(text.west)+(0mm,-0.2mm)$) .. controls 
                ($(text.west)+(1.5mm,-0.5mm)$) and 
                ($(text.center)+(-1mm,-1mm)$) ..
                ($(text.center)+(1mm,-0.5mm)$) .. controls
                ($(text.center)+(3mm,-0.7mm)$) and 
                ($(text.east)+(-1mm,-0.3mm)$) ..
                ($(text.east)+(0.5mm,-0.5mm)$);
            \draw[line width=1pt] 
                ($(text.west)+(0mm,0mm)$) .. controls 
                ($(text.west)+(1mm,0.3mm)$) and 
                ($(text.center)+(-1.5mm,-0.2mm)$) ..
                ($(text.center)+(0mm,0.2mm)$) .. controls
                ($(text.center)+(1.5mm,0.4mm)$) and 
                ($(text.east)+(-1.5mm,0.1mm)$) ..
                ($(text.east)+(0.5mm,-0.5mm)$);
        \end{tikzpicture}
    }
    \newcommand{\wigglestrike}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};
            \draw[line width=1.2pt, rounded corners=0.5mm]
                ($(text.west)+(0mm,-0.9mm)$) -- 
                ($(text.west)+(0.2cm,0.3mm)$) -- 
                ($(text.west)+(0.4cm,-0.7mm)$) --
                ($(text.west)+(0.6cm,0.6mm)$) --
                ($(text.west)+(0.8cm,-0.5mm)$) --
                ($(text.west)+(1.0cm,0.4mm)$) --
                ($(text.west)+(1.2cm,-0.6mm)$) --
                ($(text.west)+(1.4cm,0.5mm)$) --
                ($(text.east)+(0mm,0.0mm)$);
        \end{tikzpicture}
    }
    \newcommand{\strikebrush}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};
            \draw[line width=0.9pt]
                ($(text.west)+(0mm,-0.5mm)$) --
                ($(text.north west)+(0.4cm,-0.8mm)$) --
                ($(text.west)+(0.2cm,-0.6mm)$) --
                ($(text.north west)+(0.6cm,-0.8mm)$) --
                ($(text.west)+(0.4cm,-0.5mm)$) --
                ($(text.north west)+(0.8cm,-0.7mm)$) --
                ($(text.west)+(0.6cm,-0.4mm)$) --
                ($(text.north west)+(1.0cm,-0.8mm)$) --
                ($(text.west)+(0.8cm,-0.6mm)$) --
                ($(text.north west)+(1.3cm,-0.7mm)$) --
                ($(text.west)+(1.0cm,-0.5mm)$) --
                ($(text.north west)+(1.6cm,-0.8mm)$) --
                ($(text.west)+(1.2cm,-0.4mm)$) --
                ($(text.north west)+(1.9cm,-0.7mm)$) --
                ($(text.west)+(1.4cm,-0.6mm)$) --
                ($(text.north west)+(2.2cm,-0.8mm)$) --
                ($(text.west)+(1.8cm,-0.5mm)$) --
                ($(text.east)+(0cm,+0.4mm)$);
        \end{tikzpicture}
    }
    \newcommand{\linestrike}[1]{
        \begin{tikzpicture}[baseline=(text.base)]
            \node[inner sep=1pt] (text) {#1};
            \draw[line width=0.5pt]
                ($(text.west)+(0cm,+0.1mm)$) 
                .. controls ($(text.west)+(0.2cm,+0.2mm)$) and ($(text.east)+(-0.3cm,+0.1mm)$) ..
                ($(text.east)+(-0.1cm,0mm)$) --
                ($(text.east)+(-0.11cm,-0.1mm)$) 
                .. controls ($(text.west)+(+0.1cm,-0.2mm)$) and ($(text.west)+(+0.15cm,-0.15mm)$) ..
                ($(text.west)+(+0.12cm,-0.2mm)$) --
                ($(text.west)+(+0.12cm,-0.4mm)$)
                .. controls ($(text.east)+(-0.15cm,-0.2mm)$) and ($(text.east)+(-0.1cm,-0.4mm)$) ..
                ($(text.east)+(-0.05cm,-0.3mm)$) --
                ($(text.east)+(-0.1cm,-0.5mm)$) 
                .. controls ($(text.west)+(+0.05cm,-0.6mm)$) and ($(text.west)+(+0.1cm,-0.7mm)$) ..
                ($(text.west)+(+0cm,-0.6mm)$);
        \end{tikzpicture}
    }
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
    
        """

    # LaTeX preamble template with string placeholders
    template = Template(
        r"""
\documentclass[varwidth=true, border=10mm]{standalone}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{mathspec}
\usepackage{xcolor} 
$grid_code
\usepackage{tikz}
\usetikzlibrary{calc}

$strike_code

\setmainfont{$mainfont}
\setmathsfont(Digits,Latin){$mathsfont}
\pagecolor{$background_color}
\color{$text_color}

\begin{document}
$content
\end{document}
"""
    )

    # Substitute the values for each placeholder in the LaTeX template
    return template.substitute(
        mainfont=mainfont,
        mathsfont=mathsfont,
        background_color=background_color,
        text_color=text_color,
        grid_code=grid_code,
        strike_code=strike_code,
        content=content
    )


def generate_pdf_from_tex(
        output_filename: str,
        tex_files_dir: str = "tex_files",
        out_dir: str = "output_files",
        verbose: bool = False,
        tex_code: str = "None"
) -> str:
    """
    Generates a PDF from LaTeX content using xelatex.

    :param tex_code: The full LaTeX code to compile (optional).
    :param content: The LaTeX content without the preamble and document tags.
    :param output_filename: The name of the output PDF file (without extension).
    :param tex_files_dir: Directory to store intermediate .tex files.
    :param out_dir: Directory to store output files (PDFs and logs).
    :param mainfont: Font style for the main text.
    :param mathsfont: Font style for math equations.
    :param verbose: Print detailed information about the process.
    :return: The path to the generated PDF file.
    """
    # Create the full LaTeX code using the get_tex_template function
    if verbose:
        print("Generated LaTeX code:")
        print(tex_code)

    # Ensure directories exist
    os.makedirs(tex_files_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # Define file paths
    tex_filename = os.path.join(tex_files_dir, f"{output_filename}.tex")
    pdf_filename = os.path.join(out_dir, f"{output_filename}.pdf")

    # Write the LaTeX code to the .tex file
    with open(tex_filename, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_code)

    # Compile the .tex file to a PDF
    try:
        print(f"Compiling LaTeX to PDF for: {tex_filename}...")
        result = subprocess.run(
            f"xelatex -interaction=nonstopmode -output-directory={out_dir} {tex_filename}",
            shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if verbose:
            print(result.stdout.decode())  # Print LaTeX log output if needed
        print(f"PDF successfully generated: {pdf_filename}")
    except subprocess.CalledProcessError as e:
        if os.path.exists(pdf_filename):
            print("Warnings occurred during LaTeX compilation, but the PDF was generated.")
            if verbose:
                print(e.stderr.decode())  # Print warnings
        else:
            print("Error while compiling LaTeX:")
            print(e.stderr.decode())  # Print the detailed LaTeX error log
            raise

    # Clean up auxiliary files generated during compilation
    aux_extensions = [".aux", ".log", ".out"]
    for ext in aux_extensions:
        aux_file = os.path.join(out_dir, f"{output_filename}{ext}")
        if os.path.exists(aux_file):
            os.remove(aux_file)

    return pdf_filename  # Return the path to the generated PDF file
