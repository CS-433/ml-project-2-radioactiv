from latex_utils import create_tex_file, compile_tex_to_pdf, convert_pdf_to_png, delete_aux_files

tex_content = r"""
\documentclass{article}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{mathspec}
\usepackage[paperheight=5in,paperwidth=6in,margin=0.1in]{geometry}

\setmainfont{JaneAusten}
\setmathsfont(Digits,Latin){JaneAusten}

\begin{document}
\large Testing the Jane Austen font with mathematics

Here is some text in Jane Austen font, followed by a mathematical equation:

Let's try a simpler equation first:

\[ a + b = c \]

And a slightly more complex one:

\[ y = 2x + 5 \]

Some text math: $E = mc^2$

And here is more text with numbers and letters:

ABCDEFGHIJKLMNOPQRSTUVWXYZ\\
abcdefghijklmnopqrstuvwxyz\\
\[ 
y = \frac{\sqrt{x^3 + 4x^2}}{2x + 5} + \sqrt{\frac{3x^2 + 7}{x + 1}}
\]
1234567890 
\end{document}
"""

def main():
    print("Starting the LaTeX to PNG conversion process...")
    
    # Step 1: Create the .tex file
    tex_path = create_tex_file(tex_content)
    print(f"TeX file created: {tex_path}")
    
    # Step 2: Compile the .tex file to a PDF
    pdf_path = compile_tex_to_pdf(tex_path)
    if not pdf_path:
        print("Failed to compile TeX to PDF.")
        return
    print(f"PDF created: {pdf_path}")
    
    # Step 3: Convert the PDF to PNG
    png_path = convert_pdf_to_png(pdf_path)
    print(f"PNG created successfully: {png_path}")
    
    # Step 4: Clean up auxiliary files
    print("Cleaning up auxiliary files...")
    delete_aux_files(tex_path)
    print("Cleanup complete. Process finished successfully.")

if __name__ == "__main__":
    main()
