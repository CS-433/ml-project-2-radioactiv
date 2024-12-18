import openai
import os
from dotenv import load_dotenv
import random
from utils import ensure_raw_tex

class LatexGenerator:
    def __init__(self, api_key, languages=["English"], base_url="https://fmapi.swissai.cscs.ch", iterations=5):
        """
        Initializes the LatexGenerator instance.

        :param api_key: API key
        :param languages: List of languages to use in the LaTeX document
        :param base_url: API base URL
        :param iterations: Number of solutions to generate
        """
        self.client = openai.Client(api_key=api_key, base_url=base_url)
        self.iterations = iterations
        self.languages = languages

        self.header_template = f"""
        You should keep the simple default layout. You have to start your answer with the following structure for the LaTeX header:
        \\begin{{document}}
        """

    def generate_latex_question(self, exercise_number, answer):
        """
        Generates a LaTeX question with the specified exercise number and answer.

        :param exercise_number: The exercise number
        :param answer: The answer to the exercise
        :return: A LaTeX formatted question
        """
        return f"Answer only in latex format : give an example of a student solution to a math exercise number {exercise_number} with hard equations involving sqrt and power and a text explanation. the answer should be {answer}"

    def generate_latex(self, output_dir="data/latex"):
        """
        Generates LaTeX solutions for a series of math exercises and writes them to files.
        """
        print(f"Generating LaTeX files... \nWaiting for LLM Response...") 
        for i in range(1, self.iterations + 1):
            question = self.generate_latex_question(i, i)

            language = random.choice(self.languages)
            language_template = " Your answer has to be in " + language + " language. "

            add_mistakes = "Strike through 1 realistic word mistake (not digit) if needed in the answer using the \\strikeMistake. All what you have to do is \\strikeMistake{a mistake}. "

            request = question + language_template + add_mistakes + self.header_template

            res = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct",
                messages=[
                    {
                        "content": request,
                        "role": "user",
                    }
                ],
                stream=True,
            )

            answer = r""
            for chunk in res:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            # Extract LaTeX content starting from the first LaTeX command
            answer = ensure_raw_tex(answer)

            # Create the directory for the current iteration
            directory = f"{output_dir}/{i}"
            os.makedirs(directory, exist_ok=True)

            # Write the generated LaTeX to a file
            file_name = f'{directory}/content.tex'
            with open(file_name, 'w') as f:
                f.write(answer)

            print(f"Generated LaTeX {i}: {file_name}")

