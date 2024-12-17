import os
from os_utils import run_command, check_file_exists
from PIL import Image, ImageFilter
import numpy as np
import random
import re

def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    os.makedirs(folder_name, exist_ok=True)

def compile_tex_to_pdf(tex_path, output_path=None):
    """Compile a TeX file into a PDF and store it in the specified output path."""
    if output_path is None:
        base_dir = "generated_data"
        output_path = os.path.join(base_dir, "pdf")
    
    create_folder(output_path)

    tex_filename = os.path.basename(tex_path)
    pdf_filename = os.path.splitext(tex_filename)[0] + ".pdf"
    pdf_path_final = os.path.join(output_path, pdf_filename)

    run_command(f"xelatex -interaction=nonstopmode -output-directory={output_path} {tex_path}")

    if not check_file_exists(os.path.join(output_path, pdf_filename)):
        return None

    # Ensure the PDF is in the correct folder
    return pdf_path_final

def convert_pdf_to_png(pdf_path, dpi=500):
    """Convert a PDF to PNG format while preserving the original directory structure."""
    base_dir = os.path.dirname(pdf_path)
    create_folder(base_dir) 

    pdf_filename = os.path.basename(pdf_path)
    png_filename = os.path.splitext(pdf_filename)[0] + ".png" 
    output_path = os.path.join(base_dir, png_filename)

    # Convert the PDF to PNG using pdftoppm
    run_command(f"pdftoppm -r {dpi} {pdf_path} -png -singlefile {output_path[:-4]}")

    return output_path

def delete_aux_files(tex_dir):
    """Delete all auxiliary files in the specified directory."""
    aux_extensions = [".aux", ".log", ".xdv"]
    
    # Iterate over all files in the directory
    for file in os.listdir(tex_dir):
        # Check if the file has an auxiliary extension
        if any(file.endswith(ext) for ext in aux_extensions):
            file_to_delete = os.path.join(tex_dir, file)
            os.remove(file_to_delete)

def convert_tex_to_pdf(input_dir="data/latex", ouptur_dir="data/generated"):
    """Convert all TeX files in the 'tex' subfolder to PDF files."""
    print("Converting TeX files to PDF...")
    folders = get_subfolders(input_dir)
    for folder in folders:
        tex_path = os.path.join(input_dir, folder)
        tex_files = [f for f in os.listdir(tex_path) if f.endswith(".tex") and f != "content.tex"]
        output_path = os.path.join(ouptur_dir, folder)
        for tex_file in tex_files:
            input_path = os.path.join(tex_path, tex_file)
            compile_tex_to_pdf(input_path, output_path)  # Ensure this raises an exception on failure
            delete_aux_files(output_path)

def convert_pdf_to_pngs(input_dir="generated_data/pdf"):
    """Convert all PDF files in the 'pdf' subfolder to PNG files."""
    print("Converting PDF files to PNG...")
    folders = get_subfolders(input_dir)
    for folder in folders:
        input_directory = os.path.join(input_dir, folder)
        pdf_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith(".pdf")]

        for pdf_file in pdf_files:
            convert_pdf_to_png(pdf_file)

def add_headers_to_tex(tex_path, headers, paths):
    """
    Add multiple headers to a TeX file, creating a new file for each header.
    """
    with open(tex_path, "r", encoding="utf-8") as tex_file:
        tex_content = tex_file.read()

    tex_content = add_irregularities(tex_content)
    if not tex_content.lstrip().startswith(r"\begin{document}"):
        return
    with open(tex_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_content)
        
    for idx, header in enumerate(headers):
        new_tex_content = header + tex_content
        
        # Generate a new filename based on the index
        new_tex_path = f"{tex_path.rsplit('.', 1)[0]}_{paths[idx]}.tex"
        
        with open(new_tex_path, "w", encoding="utf-8") as new_tex_file:
            new_tex_file.write(new_tex_content)
    
def clean_tex_headers(tex_dir="data/latex"):
    print("Cleaning TeX headers...")
    folders = get_subfolders(tex_dir)
    for folder in folders:
        current_folder_path = os.path.join(tex_dir, folder)
        tex_files = [f for f in os.listdir(current_folder_path) if f.endswith(".tex") and f != "content.tex"]
        for tex_file in tex_files:
            tex_path = os.path.join(current_folder_path, tex_file)
            os.remove(tex_path)

def delete_pdfs(pdf_dir="data/generated"):
    print("Deleting PDF files...")
    folders = get_subfolders(pdf_dir)
    for folder in folders:
        current_folder_path = os.path.join(pdf_dir, folder)
        pdf_files = [f for f in os.listdir(current_folder_path) if f.endswith(".pdf")]
        for pdf in pdf_files:
            pdf_path = os.path.join(current_folder_path, pdf)
            os.remove(pdf_path)

def add_headers(tex_dir="data/latex", headers=["\\documentclass{article}\n"], paths=["default"]):
    """
    Add headers to all TeX files in the 'tex' subfolder.
    """
    folders = get_subfolders(tex_dir)
    for folder in folders:
        tex_directory = os.path.join(tex_dir, folder)
        tex_files = [f for f in os.listdir(tex_directory) if f.endswith(".tex")]

        for tex_file in tex_files:
            tex_path = os.path.join(tex_directory, tex_file)
            add_headers_to_tex(tex_path, headers, paths)
             
def get_subfolders(folder):
    subfolders = [d for d in os.walk(folder)][0][1]
    return subfolders

def create_headers(fonts, pagecolors = ["white"], textcolors = ["black"]):
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
    irregularities = r"""
\newcommand{\irregularword}[1]{%
  \pgfmathsetmacro{\yshift}{(random()-0.5)*3} % Random y-shift between -3pt and 3pt
  \pgfmathsetmacro{\rotation}{(random()-0.5)*10} % Random rotation between -5° and 5°
  \tikz[baseline]{
    \node[inner sep=0pt, outer sep=0pt, anchor=base, yshift=\yshift pt, rotate=\rotation] (text) {\strut #1};
  }%
}

\usepackage{xparse}
\ExplSyntaxOn
\NewDocumentCommand{\processtext}{+m}{
  \seq_set_split:Nnn \l_tmpa_seq { ~ } { #1 }
  \seq_map_inline:Nn \l_tmpa_seq { \irregularword{##1} }
}
\ExplSyntaxOff"""
    headers = []
    paths = []
    for grid in grids:
        for font in fonts:
            font_code = get_font_template(font)
            for pagecolor in pagecolors:
                for textcolor in textcolors:
                    if pagecolor == textcolor:
                        continue
                    grid_path = "grid" if grid else "nogrid"
                    path = "_".join([textcolor + "text", pagecolor + "page", font, grid_path])
                    paths.append(path)
                    strike_code = get_strike_design()
                    header = r"""\documentclass[varwidth=true, border=10mm]{standalone}
\usepackage{tikz}
\usetikzlibrary{calc}
%s
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{mathspec}
\usepackage{xcolor} 
%s
\pagecolor{%s}
\color{%s}
%s
%s
""" % (strike_code, font_code, pagecolor, textcolor, grid, irregularities)
                    headers.append(header)
    return (headers, paths)

def add_noise_and_blur(directory="data/generated", noise_level=100, blur_radius=2):
    print("Adding noise and blur...")
    if not os.path.exists(directory):
        return
    folders = get_subfolders(directory)
    for folder in folders:
        folder = os.path.join(directory, folder)
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

def get_font_template(font_name: str):
  """Generate LaTeX font configuration for a specified font, including special handling for 'ML4Science'."""
  
  font_template = r"""\setmainfont{font_name}[
    Extension=.otf,
    UprightFont=*,
    FallbackFonts={% 
        {font=Times New Roman}    
    }
]
\setmathsfont(Digits,Latin){font_name}
""".replace("font_name", font_name)
  


  if font_name == "ML4Science":
      font_code =r"""\setmainfont{ML4Science}[
    Extension=.otf,
    UprightFont=*,
    FallbackFonts={% 
        {font=Times New Roman}    
    }
]
\setmathsfont(Digits,Latin){ML4Science}
\DeclareSymbolFont{operators}{\encodingdefault}{\rmdefault}{m}{n}
\SetSymbolFont{operators}{normal}{\encodingdefault}{\rmdefault}{m}{n}
\DeclareTextSymbol{\textapostrophe}{T1}{39}
\catcode`'=\active
\def'{\text{\fontspec{ML4Science}\symbol{"27}}}
\DeclareMathSymbol{=}{\mathrel}{operators}{"3D}
\DeclareMathSymbol{-}{\mathbin}{operators}{"2D}
\DeclareMathSymbol{/}{\mathord}{operators}{"2F}  
\DeclareMathSymbol{+}{\mathbin}{operators}{"2B}
\DeclareMathSymbol{<}{\mathrel}{operators}{"3C}
\DeclareMathSymbol{>}{\mathrel}{operators}{"3E}
\DeclareMathSymbol{\leq}{\mathrel}{operators}{"3C}
\DeclareMathSymbol{\geq}{\mathrel}{operators}{"3E}
\renewcommand{\subset}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2282}}}}
\renewcommand{\supset}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2283}}}}
\renewcommand{\in}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2208}}}}
\renewcommand{\approx}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2248}}}}
\renewcommand{\forall}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2200}}}}
\DeclareMathSymbol{\pm}{\mathbin}{operators}{"B1}
\renewcommand{\Rightarrow}{\mathrel{\text{\fontspec{ML4Science}\symbol{"2192}}}}
\let\implies\Rightarrow
\renewcommand{\infty}{\text{\fontspec{ML4Science}∞}}
\renewcommand{\cdot}{\mathbin{\text{\fontspec{ML4Science}\symbol{"2219}}}}
\renewcommand{\int}{\mathop{\text{\fontspec{ML4Science}\symbol{"222B}}}\displaylimits}
\makeatletter
\renewcommand{\frac}[2]{%
  \sbox\z@{$\displaystyle\begin{array}{c}#1\\#2\end{array}$}% 
  \mathop{%
    \kern 0.4em
    \hbox to \wd\z@{\text{\fontspec{ML4Science}}\leaders\hbox{\symbol{"2014}}\hfill}%
  }\limits^{\ensuremath{\displaystyle #1}}_{\ensuremath{\displaystyle #2}}% 
}
\makeatother
\makeatletter
\newcommand{\scaledsqrt}[1]{%
  \sbox\z@{$#1$}%
  \raisebox{\dimexpr-\dp\z@}{%   
    \resizebox{!}{\dimexpr\ht\z@+\dp\z@+2pt}{%
      \text{\fontspec{ML4Science}√}%
    }%
  }%
}
\newcommand{\sqrtoverline}[1]{%
  \vbox{%
    \sbox\z@{$#1$}%  
    \kern-\dimexpr\ht\z@ + \dp\z@ + 1em\relax% 
    \hbox to \dimexpr\wd\z@ + 0.41em\relax{% 
        \leaders\hbox{\text{\fontspec{ML4Science}\symbol{"2015}}}\hfill%
    }%
    \kern\dimexpr\ht\z@ - 1.28em\relax%  
    \box\z@
  }%
}
\renewcommand{\sqrt}[1]{%
    \mathopen{\scaledsqrt{#1}}%
    \sqrtoverline{#1}%
}
"""
  else:
    font_code = r"""\setmainfont{font_name}
\setmathsfont(Digits,Latin){font_name}
""".replace("font_name", font_name)

  return font_code

def get_strike_design():
    """Get random humanoid design for the strike-through effect."""
    strikes = [r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
}""", r"""
\newcommand{\strikeMistake}[1]{
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
"""]
    # choose random element from strikes
    strike_code = random.choice(strikes)
    return strike_code

def add_irregularities(tex_content):
    lines = tex_content.split('\n')
    modified_lines = []
    skip_processing_bracket = False
    skip_processing_dollar = False
    
    for line in lines:
        if line.strip() == '':
            modified_lines.append(line)
        elif '\\[' in line:
            skip_processing_bracket = True
            modified_lines.append(line)
        elif '\\]' in line:
            skip_processing_bracket = False
            modified_lines.append(line)
        elif '$$' in line:
            skip_processing_dollar = not skip_processing_dollar
            modified_lines.append(line)
        elif skip_processing_bracket or skip_processing_dollar:
            modified_lines.append(line)
        elif '\\' in line or '[' in line or ']' in line or '$' in line or '{' in line or '}' in line or '_' in line or '#' in line:
            modified_lines.append(line)
        else:
            modified_line = r'\processtext{' + line + '}'
            modified_lines.append(modified_line)
    
    modified_tex_content = '\n'.join(modified_lines)
    return modified_tex_content
