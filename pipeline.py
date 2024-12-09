import os
import random

from prompts import get_math_exercise_prompt

from utils import get_tex_template, generate_pdf_from_tex
from model_communicator import ModelCommunicator
from dotenv import load_dotenv


def pipeline(k=10, api_key=None, base_dir="example_data"):
    model_communicator = ModelCommunicator(
        api_key=api_key, base_url="https://fmapi.swissai.cscs.ch"
    )
    # create directories
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if not os.path.exists(os.path.join(base_dir, "tex_files")):
        os.makedirs(os.path.join(base_dir, "tex_files"))
    if not os.path.exists(os.path.join(base_dir, "generated")):
        os.makedirs(os.path.join(base_dir, "generated"))
    if not os.path.exists(os.path.join(base_dir, "tex_content")):
        os.makedirs(os.path.join(base_dir, "tex_content"))

    tex_files_dir = os.path.join(base_dir, "tex_files")
    generated_dir = os.path.join(base_dir, "generated")
    content_dir = os.path.join(base_dir, "tex_content")
    # generate data
    # create a sequence of strings "english, french, german, italian" and a sequence of numbers 1, 2, 3, 4, 5 random and a sequence of booleans True, False all of length 10 and then zip them
    languages = random.choices(["English", "French", "German", "Italian"], k=k)
    numbers = random.choices([1, 2, 3, 4, 5], k=k)
    booleans = random.choices([True, False], k=k)

    # Zip them together
    sequence = zip(languages, numbers, booleans)

    # Iterate over the sequence
    for i, (lang, num, flag) in enumerate(sequence):
        print(f"Generating PDF {i+1}/{k}...")
        prompt = get_math_exercise_prompt(
            language=lang, complexity=num, correct=flag
        )
        response = model_communicator.communicate_with_model(prompt)
        print("Response:")
        print(response)
        # save response to a tex file in the tex_content_dir/i
        if i < 10:
            i = f"0{i}"
        if not os.path.exists(os.path.join(content_dir, f"{i}")):
            os.makedirs(os.path.join(content_dir, f"{i}"))
        path = os.path.join(content_dir, f"{i}", f"exercise_{lang}_{num}_{flag}.txt")
        if response:
            with open(path, "w") as f:
                f.write(response)
            generate_pdf_from_tex(response, f"exercise_{lang}_{num}_{flag}", tex_files_dir + f"/{i}", out_dir=generated_dir + f"/{i}", verbose=True)


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")
    pipeline(api_key=api_key, base_dir="ex02")




