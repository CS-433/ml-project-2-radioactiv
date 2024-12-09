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


def convert_pdf_to_png(pdf_path, output_png="document.png", base_dir="generated_data"):
    """Convert a PDF to PNG format and store the PNG in the 'png' subfolder."""
    png_dir = os.path.join(base_dir, "png")
    create_folder(png_dir)  # Ensure the folder exists

    output_path = os.path.join(png_dir, output_png)
    print("Converting PDF to PNG...")
    run_command(f"pdftoppm {pdf_path} -png -singlefile {output_path[:-4]}")
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


def get_tex_template(
    content: str, mainfont: str = "JaneAusten", mathsfont: str = "JaneAusten"
) -> str:
    """
    Generate a LaTeX template with specified font settings and content using string.Template.

    :param content: The LaTeX content to include in the document
    :param mainfont: The main font to use for the document
    :param mathsfont: The math font to use for equations
    :return: A formatted LaTeX string
    """
    template = Template(
        r"""
\documentclass{article}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{mathspec}
\usepackage[paperwidth=6in,margin=0.1in]{geometry}

\setmainfont{$mainfont}
\setmathsfont(Digits,Latin){$mathsfont}

\begin{document}
$content
\end{document}
"""
    )
    return template.substitute(mainfont=mainfont, mathsfont=mathsfont, content=content)


def generate_pdf_from_tex(
        content: str,
        output_filename: str,
        tex_files_dir: str = "tex_files",
        out_dir: str = "output_files",
        mainfont: str = "Times New Roman",
        mathsfont: str = "Times New Roman",
        verbose: bool = False,
) -> str:
    """
    Generates a PDF from LaTeX content using xelatex.

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
    tex_code = get_tex_template(content, mainfont, mathsfont)
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
