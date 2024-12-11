import os
from latex_generator import LatexGenerator
from latex_utils import *
from stroke_extraction import handwrite
from dotenv import load_dotenv

def transform_handwriting(input_dir="generated_data/pdf"):
    """Transform all PDF files in the 'pdf' subfolder to handwritten SVG and PNG files."""
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        handwrite(pdf_file, "./generated_data/svg/handwriting_strokes.svg", "./generated_data/png/handwriting_strokes_1.png")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")

    generator = LatexGenerator(api_key, iterations=2)
    generator.generate_latex()

    fonts = ["JaneAusten"]
    pagecolors = ["white"]
    textcolors = ["black"]
    add_mistakes("generated_data/tex")

    headers = create_headers(fonts, pagecolors, textcolors)

    add_headers("generated_data/tex", headers)
    convert_tex_to_pdf("generated_data/tex")
    convert_pdf_to_pngs("generated_data/pdf")
    # transform_handwriting("generated_data/pdf")
