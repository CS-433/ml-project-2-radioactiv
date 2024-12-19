import os
from latex_generator import LatexGenerator
from utils import *
from dotenv import load_dotenv

# Define the directories for the LaTeX scripts and images to generate
latex_dir = "data/LaTeX"
generated_dir = "data/PNG"

# Define the parameters for the LaTeX generation
nbr_of_texfiles = 10
languages = ["English", "French", "German", "Italian"]
fonts = ["ML4Science", "JaneAusten"]
pagecolors = ["white", "paper"]
textcolors = ["black", "darkblue", "red"]

if __name__ == "__main__":
    # Load the API key from the .env file
    load_dotenv()
    api_key = os.getenv("API_KEY")

    # Generate the LaTeX scripts
    generator = LatexGenerator(api_key, languages=languages, iterations=nbr_of_texfiles)
    generator.generate_latex(latex_dir)

    # Add headers to the LaTeX scripts
    headers, paths = create_headers(fonts, pagecolors, textcolors)
    add_headers(tex_dir=latex_dir, headers=headers, paths=paths)

    # Convert the LaTeX scripts to PDFs
    convert_tex_to_pdf(input_dir=latex_dir, ouptur_dir=generated_dir)

    # Convert the PDFs to PNGs
    convert_pdf_to_pngs(input_dir=generated_dir)

    # Generate noisy and blurred images
    add_noise_and_blur(directory=generated_dir)

    # Clean up the directories
    delete_pdfs(pdf_dir=generated_dir)
    clean_tex_headers(tex_dir=latex_dir)
