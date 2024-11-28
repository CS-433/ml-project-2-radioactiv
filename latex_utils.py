import os
from os_utils import run_command, check_file_exists

def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    os.makedirs(folder_name, exist_ok=True)

def create_tex_file(tex_content, filename="document.tex"):
    """Create a .tex file with the given content."""
    base_dir = "generated_data"
    tex_dir = os.path.join(base_dir, "tex")
    create_folder(tex_dir)  # Ensure the folder exists
    tex_path = os.path.join(tex_dir, filename)
    with open(tex_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_content)
    return tex_path

def compile_tex_to_pdf(tex_path):
    """Compile a TeX file into a PDF and store the PDF in the 'pdf' subfolder."""
    base_dir = "generated_data"
    pdf_dir = os.path.join(base_dir, "pdf")
    create_folder(pdf_dir)  # Ensure the folder exists
    
    tex_dir = os.path.dirname(tex_path)
    pdf_filename = "document.pdf"
    pdf_path_temp = os.path.join(tex_dir, pdf_filename)
    pdf_path_final = os.path.join(pdf_dir, pdf_filename)
    
    print("Compiling TeX to PDF...")
    run_command(f"xelatex -interaction=nonstopmode -no-pdf -output-directory={tex_dir} {tex_path}")
    run_command(f"xelatex -interaction=nonstopmode -output-directory={tex_dir} {tex_path}")
    
    if not check_file_exists(pdf_path_temp):
        print("PDF was not created successfully.")
        return None
    
    # Delete the existing file at the destination if it exists
    if os.path.exists(pdf_path_final):
        os.remove(pdf_path_final)

    # Move the PDF to the designated folder
    os.rename(pdf_path_temp, pdf_path_final)
    return pdf_path_final

def convert_pdf_to_png(pdf_path, output_png="document.png"):
    """Convert a PDF to PNG format and store the PNG in the 'png' subfolder."""
    base_dir = "generated_data"
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
