# Handwriting data creation
This project is our second project for the ML Course at EPFL.


## Team Members
- David Schulmeister
- Amene Gafsi
- Rosa Mayila

## Overview
This project generates synthetic "handwritten" math exercises to simulate student solutions. The output is designed for use in training machine learning models for tasks such as text detection, OCR, and automated grading. By leveraging language models, the pipeline creates LaTeX-based exercises, converts them into PDFs and PNG images, and applies realistic augmentations like noise, blur, and simulated mistakes. This approach produces data that closely resembles scanned handwritten documents while incorporating irregular formatting and errors to mimic human handwriting.
## Key Features
- **LaTeX-Based Exercise Generation:** Utilizes a language model to create math exercises with hard equations involving square roots, powers, and text explanations. Generated exercises are formatted in LaTeX.

- **Multi-Language Support:** Exercises can be generated in various languages, including English, French, German, and Italian.

- **Mistake Simulation:** Adds a realistic touch by striking through a word using a LaTeX `\strikeMistake` command to mimic student corrections.

- **Handwriting Irregularities:** Dynamically adjusts text placement with a custom `\processtext` LaTeX command to introduce word irregularities.

- **PDF and PNG Conversion:**
    - Compiles LaTeX documents into PDFs.
    - Converts PDFs into high-resolution PNG images for broader usability.

- **Image Augmentations:**
    - Adds noise and blur to PNG images to simulate real-world scanned handwriting artifacts.
    - Generates multiple versions of the same exercise with different visual distortions.

- **Flexible Design Templates:**
    - Supports various fonts (e.g., "ML4Science" and "JaneAusten").
    - Allows customization of page colors, text colors, and optional grid overlays.

## Repository Structure

## Repository Structure

**Key Files and Directories:**

- **`latex_generator.py`**  
  Handles LaTeX-based exercise generation using a language model API. It:
    - Generates exercises with equations and explanations in LaTeX.
    - Supports language variation and mistake simulation.
    - Saves generated LaTeX content to structured directories.

- **`main.py`**  
  The main script orchestrating the full pipeline. It:
    - Generates LaTeX exercises.
    - Applies headers and templates to the LaTeX files.
    - Converts LaTeX to PDFs and PDFs to PNG images.
    - Adds noise and blur to simulate scanned handwritten artifacts.

- **`utils.py`**  
  Contains utility functions to:
    - Compile LaTeX files into PDFs.
    - Convert PDFs to PNG images.
    - Add noise and blur to images.
    - Manage directories, clean auxiliary files, and generate LaTeX headers.

- **`os_utils.py`**  
  Provides helper functions to run shell commands and check file existence.

- **`data/`**  
  Directory where all generated data is stored:
    - `latex/`: Contains generated LaTeX files.
    - `generated/`: Contains compiled PDFs and PNG images with augmentations.

- **`.env`**  
  Store here the API key for the language model API.

## Dependencies and Requirements


### System Requirements
- **Programming Language:** Python 3.8+
- **System Tools:**
    - `xelatex` (for LaTeX compilation, part of TeX Live or MiKTeX)
    - `pdftoppm` (from `poppler-utils` for PDF-to-PNG conversion)
- **Python Packages:**
    - `openai` (for the language model API client)
    - `numpy` (for noise generation)
    - `Pillow` (for image processing: noise and blur)
    - `dotenv` (to load environment variables)


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

4. **Directory Structure:** Ensure the following directory structure exists:

    ```
    handwriting_data_creation/
    ├── .env
    ├── latex_generator.py
    ├── main.py
    ├── utils.py
    ├── os_utils.py
    ├── data/
    │   ├── latex/
    │   └── generated/
    └── requirements.txt
    ```

## Usage

**1. Run the Pipeline:** In the main script (e.g., `main.py` or the provided snippet in `if __name__ == "__main__":`)


**Example:**

```bash
python main.py
```
This will:
- Load the API_KEY from `.env`.
- Interact with the model to generate prompts and exercises.
- Create LaTeX documents, compile them to PDFs, and convert to PNGs.
- Add noise and blur to the generated images.

**2. Adjust Parameters:** You can customize:

    You can customize the following parameters in main.py:
    •	languages: List of supported languages (e.g., ["English", "French", "German"]).
    •	fonts: Fonts used in LaTeX documents (e.g., ["ML4Science", "JaneAusten"]).
    •	iterations: Number of exercises to generate.
    •	Augmentations: Adjust noise and blur levels in the add_noise_and_blur function.


**3. Viewing Results:** After running the pipeline, check:

    	LaTeX files will be stored under data/latex/.
	•	PDFs and augmented PNGs will be available under data/generated/.

    Each exercise will have:
    •	A clean version (PNG).
    •	Noisy and blurred versions of the PNG files.
    
    You can view the generated images in any image viewer or open the LaTeX files for further customization.
## Extending the Project


## Troubleshooting

- **Compilation Errors:** If LaTeX compilation fails, ensure that `xelatex` and the required LaTeX packages (`tikz`, `mathspec`, `fontspec`) are installed.
- **Missing Tools:** If PDF-to-PNG conversion fails, ensure `pdftoppm` from `poppler-utils` is installed.
- **API Errors:** Check that your `API_KEY` is set correctly and you have access to the model endpoint.
