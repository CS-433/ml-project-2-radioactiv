# Handwriting data creation
This project is our second project for the ML Course at EPFL.

## Overview
This project aims to generate a dataset of synthetic "handwritten" math exercises. The generated data simulates student solutions that can be later recognized and automatically graded. By producing LaTeX-based exercises, rendering them as PDFs and PNG images, and introducing noise and blur, we create a dataset that closely resembles scanned, handwritten documents. This dataset can then be used to train machine learning models for text detection, OCR, and automated grading.
## Overview
This project aims to generate a dataset of synthetic "handwritten" math exercises. The generated data simulates student solutions that can be recognized and automatically graded. By producing LaTeX-based exercises, rendering them as PDFs and PNG images, and introducing noise and blur, we create a dataset that closely resembles scanned, handwritten documents. This dataset can then be used to train machine learning models for text detection, OCR, and automated grading.

## Key Features
- **Model Interaction:** Utilizes a language model (via the `ModelCommunicator` class) to generate math exercises in different languages, complexity levels, and correctness states.
- **LaTeX Rendering:** Dynamically inserts generated math exercises into LaTeX templates to produce stylized PDFs.
- **Rich Formatting:** Simulates student mistakes and handwriting irregularities by:
    - Introducing strikethrough text to mimic crossed-out corrections.
    - Adding wiggling text via a special LaTeX command for irregular word placement.
- **Conversion to PNG and Image Augmentations:**
    - Converts the rendered PDFs into PNG images.
    - Adds noise and blur to approximate the appearance of real scanned handwriting.

## Repository Structure

**Key Files:**
- **`model_communicator.py`**  
  Handles communication with the language model API. It sends prompts and receives responses from the model. It also includes a function `clean_answer_format` to extract only the necessary LaTeX content from model responses.

- **`utils.py`**  
  Provides utility functions to handle LaTeX compilation, PDF-to-PNG conversion, cropping, and image augmentation (noise and blur). It also defines template generation for LaTeX documents.

- **`prompts.py`**  
  Contains the `get_math_exercise_prompt` function, which creates a detailed prompt to request math exercises from the language model. The prompt can include instructions for correctness, complexity, and special formatting commands (e.g., strikes and irregular text).

- **`main_script.py`** (or the provided script with the `pipeline` function)  
  The main entry point to generate a batch (`k`) of math exercises. It:
    - Randomizes parameters (language, complexity, colors, strikes, grids).
    - Requests an exercise from the model.
    - Generates a LaTeX file from the returned content.
    - Compiles it to PDF, then converts it to PNG.
    - Adds noise and blur to the PNG to simulate real handwriting scans.

## Dependencies and Requirements

- **Programming Language:** Python 3.8+
- **System Tools:**
    - `xelatex` (from TeX Live or MiKTeX) for LaTeX compilation
    - `pdfcrop` for cropping PDF margins
    - `pdftoppm` for converting PDF to PNG images (part of `poppler` tools)
- **Python Packages:**
    - `openai` (for the language model API client)
    - `numpy` (for noise generation)
    - `Pillow` (for image processing: noise and blur)
    - `dotenv` (to load environment variables)

  Additional packages might be required depending on your environment and OS.

## Setup

1. **Install System Dependencies:**
   Ensure `xelatex`, `pdfcrop`, and `pdftoppm` are installed and available in your system's PATH.

   **Example (Ubuntu/Debian):**
   ```bash
   sudo apt-get update
   sudo apt-get install texlive-full poppler-utils
2. **Install Python Dependencies**: In your Python virtual environment, run:

    ```bash
    pip install -r requirements.txt
    ```
    (If you don't have a `requirements.txt`, ensure all necessary packages listed above are installed.)

3. **Set Up API Key:** The model requires an API key for access. Create a `.env` file in your project directory:

    ```bash
    echo "API_KEY=your_api_key_here" > .env
    ```
    Replace `your_api_key_here` with your actual API key. Make sure you have permission to use the provided model endpoint.

## Usage

**1. Run the Pipeline:** In the main script (e.g., `python pipeline.py` or the provided snippet in `if __name__ == "__main__":`), the `pipeline` function is called with `k=10` by default to generate 10 exercises.


**Example:**

```bash
python pipeline.py
```
This will:
- Load the API_KEY from `.env`.
- Interact with the model to generate prompts and exercises.
- Create LaTeX documents, compile them to PDFs, and convert to PNGs.
- Add noise and blur to the generated images.
- Store the outputs under the specified `base_dir` (e.g., `example01`).

**2. Adjust Parameters:** You can customize:

- `k`: Number of exercises to generate.
- `base_dir`: The base output directory for generated files.
- `font`: The main and math fonts for the LaTeX templates.
- Other parameters such as `language`, `complexity`, `correct`, `strike` can be modified by editing code in `pipeline` or `get_math_exercise_prompt`.
- 
**3. Viewing Results:** After running the pipeline, check:

    - `tex_content/`: Contains the generated LaTeX exercise content.
    - `tex_files/`: Contains the `.tex` files used for compilation.
    - `generated/`: Contains the compiled PDFs and PNG images. You’ll find both noisy and blurred variants, simulating handwritten scans.

## Extending the Project

**Prompts and Content:** Modify `prompts.py` to request different types of math exercises, adjust complexity, language distribution, or incorporate more intricate instructions for the layout.
**Model Choice:** Update the model endpoint or API key in `ModelCommunicator` for different LLMs or model APIs.
**Post-Processing:** Enhance image augmentation methods or introduce additional processing steps to better mimic real handwriting artifacts.
**Testing:** Consider adding unit tests or integration tests to ensure reliability.

## Troubleshooting

- **Compilation Errors:** If LaTeX compilation fails, ensure that `xelatex` and the required LaTeX packages (`tikz`, `mathspec`, `fontspec`) are installed.
- **Missing Tools:** If PDF-to-PNG conversion fails, ensure `pdftoppm` from `poppler-utils` is installed.
- **API Errors:** Check that your `API_KEY` is set correctly and you have access to the model endpoint.
