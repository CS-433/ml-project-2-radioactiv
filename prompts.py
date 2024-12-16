def get_math_exercise_prompt(
    language: str = None, complexity: int = 3, correct: bool = True, strike: bool = False
) -> str:
    """
    Generate a prompt for a math exercise with the specified complexity.

    :param strike: Whether the exercise should include strikethrough text
    :param correct: Whether the solution should be correct or not
    :param language: The language for the exercise prompt (e.g., "German", "Italian", "French", or "English")
    :param complexity: The complexity level of the exercise (e.g., 0 for simple, higher numbers for more complex)
    :return: A string containing a prompt for a math exercise
    """
    if language is None:
        language = "either German, Italian, French, or English"

    if correct:
        correct_str = "The Solution must be correct!!!"
    else:
        correct_str = "The Solution Should not be correct!!! Include some mistakes!!!"

    complexity_lv = 0
    if complexity > 5:
        complexity_lv = 5
    elif complexity < 0:
        complexity_lv = 0
    else:
        complexity_lv = complexity

    strike_str = ("Since the the Latex Code you produce will be used to train a text detection tool for student solutions, you shouls also incorporate "
                  "certein text fragments that are striked through. This is to simulate the fact that students might have made mistakes in their solutions. "
                    "To do this, you can use the following command: \n\n"
                    "\\strike{This text will be striked through.}\n\n") if strike else ""

    complexity_str = "The complexity level of the exercise is " + str(complexity_lv)
    " out of 5, where 0 is simple like Kindergarten level and 5 is complex like Theoretical Quantum Physics. PHD level."

    return (
        f"Write a math exercise  in {language} with the following requirements:\n\n1. "
        f"Include mathematical expressions and text explanations.\n\n2. {correct_str}\n\n3. "
        f"{complexity_str}\n\n"
        f"{strike_str}\n\n"
        f"Just reply with the desired output, nothing else!"
    )
