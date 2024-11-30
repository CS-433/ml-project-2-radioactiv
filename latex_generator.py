import openai
import os

class LatexGenerator:
    def __init__(self, api_key, base_url="https://fmapi.swissai.cscs.ch", font="JaneAusten", iterations=5):
        """
        Initializes the LatexGenerator instance.

        :param api_key: API key
        :param base_url: API base URL
        :param font: The font to use in the LaTeX document
        :param iterations: Number of solutions to generate
        """
        self.client = openai.Client(api_key=api_key, base_url=base_url)
        self.font = font
        self.iterations = iterations
        self.header_template = r"""
        You have to start your answer with the following structure for the latex font :
        \documentclass{article}
        \usepackage{fontspec}
        \usepackage{amsmath}
        \usepackage{mathspec}
        \usepackage[paperwidth=6in,margin=0.1in]{geometry}

        \setmainfont{%s}
        \setmathsfont(Digits,Latin){%s}

        \begin{document}

        """ % (self.font, self.font)

    def generate_latex_question(self, exercise_number, answer):
        """
        Generates a LaTeX question with the specified exercise number and answer.

        :param exercise_number: The exercise number
        :param answer: The answer to the exercise
        :return: A LaTeX formatted question
        """
        return f"Answer only in latex format : give an example of a student solution to a math exercise number {exercise_number} with hard equations involving sqrt and power and a text explanation. the answer should be {answer}"

    def generate_latex(self):
        """
        Generates LaTeX solutions for a series of math exercises and writes them to files.
        """
        for i in range(1, self.iterations + 1):
            question = self.generate_latex_question(i, i)
            request = question + self.header_template

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
            answer = answer[answer.find('\\'):]

            directory = 'generated_data/txt'
            os.makedirs(directory, exist_ok=True)

            # Write the generated LaTeX to a file
            file_name = f'{directory}/answer_{i}.txt'
            with open(file_name, 'w') as f:
                f.write(answer)

            print(f"Generated LaTeX solution for exercise {i}: {file_name}")

if __name__ == "__main__":
    # Replace with API key
    api_key = "sk-rc-gNqk64G9aEO7nnxOEnpvmw"
    generator = LatexGenerator(api_key, font="JaneAusten", iterations=3)
    generator.generate_latex()
