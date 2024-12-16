import os
import random

from prompts import get_math_exercise_prompt

from utils import get_tex_template, generate_pdf_from_tex, convert_pdf_to_png
from model_communicator import ModelCommunicator
from dotenv import load_dotenv

possible_languages = ["English", "French", "German", "Italian"]
possible_difficulties = [1, 2, 3, 4, 5]
possible_text_colors = ["red", "blue", "green", "yellow", 'black', 'white']
possible_background_colors = ["white", "black", "gray"]

model_base_url = "https://fmapi.swissai.cscs.ch"


def pipeline(k=10, api_key=None, base_dir="example_data"):
    model_communicator = ModelCommunicator(
        api_key=api_key, base_url=model_base_url
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
    # create a sequence of strings "english, french, german, italian" and other random parameters
    # this can later be done systematically
    languages = random.choices(possible_languages, k=k)
    numbers = random.choices(possible_difficulties, k=k)
    booleans = random.choices([True, False], k=k)
    text_colors = random.choices(possible_text_colors, k=k)
    background_colors = random.choices(possible_background_colors, k=k)
    hasGrids = random.choices([True, False], k=k)
    hasStrikes = random.choices([True, False], k=k)

    # make sure we dont have the same text and background color
    for i in range(k):
        if text_colors[i] == background_colors[i]:
            new_possible_text_colors = [color for color in possible_text_colors if color != text_colors[i]]
            text_colors[i] = random.choice(new_possible_text_colors)
    # Zip them together
    sequence = zip(languages, numbers, booleans, text_colors, background_colors, hasGrids, hasStrikes)

    # Iterate over the sequence
    for i, (lang, num, flag, text_color, background_color, hasGrid, hasStrike) in enumerate(sequence):
        print(f"Generating PDF {i+1}/{k}...")
        prompt = get_math_exercise_prompt(
            language=lang, complexity=num, correct=flag, strike=hasStrike
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
            filename = f"exercise_{lang}_{num}_{flag}_{text_color}_{background_color}_{'grid' if hasGrids else ''}_{'strike' if hasStrikes else ''}"
            with open(path, "w") as f:
                f.write(response)
            #TODO: try out with custom font
            tex_code = get_tex_template(response, mainfont='Times New Roman', mathsfont='Times New Roman', text_color=text_color, background_color=background_color, grid=hasGrid)
            generate_pdf_from_tex(filename, tex_files_dir + f"/{i}", out_dir=generated_dir + f"/{i}", verbose=True, tex_code=tex_code)
            #convert_pdf_to_png(generated_dir + f"/{i}/{filename}.pdf", f"{filename}.png", generated_dir + f"/{i}")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")
    pipeline(api_key=api_key, base_dir="example05")




