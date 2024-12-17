import os
from latex_generator import LatexGenerator
from utils import *
from dotenv import load_dotenv

# TODO fontsize
# \setmainfont[Scale=2.0]{ML4Science}

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")

    latex_dir = "data/latex"
    generated_dir = "data/generated"

    languages = ["English", "French", "German", "Italian"]
    fonts = ["ML4Science", "JaneAusten"]
    pagecolors = ["white"]
    textcolors = ["black"]

    generator = LatexGenerator(api_key, languages=languages, iterations=2)
    generator.generate_latex()

    headers, paths = create_headers(fonts, pagecolors, textcolors)
    add_headers(tex_dir=latex_dir, headers=headers, paths=paths)

    convert_tex_to_pdf(input_dir=latex_dir, ouptur_dir=generated_dir)

    convert_pdf_to_pngs(input_dir=generated_dir)
    add_noise_and_blur(directory=generated_dir, noise_level=100, blur_radius=2)

    delete_pdfs(pdf_dir=generated_dir)
    clean_tex_headers(tex_dir=latex_dir)
