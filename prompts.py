def get_math_exercise_prompt(
    language: str = None,
    complexity: int = 3,
    correct: bool = True,
    strike: bool = False,
    word_wiggeling: bool = True,
) -> str:
    """
    Generate a prompt for a math exercise with the specified complexity.

    :param word_wiggeling: some words are not completely straight, they are jiggling a bit
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

    strike_str = (
        (
            r"""To simulate student mistakes, incorporate strikethrough text using the following commands:
                \simplestrike{simple strikes}
                \scribblestrike{scribbled words or phrases}
                \wigglestrike{wiggly lines}
                \strikebrush{brush-like style strikes}
                \mistake{mistakes}
                \linestrike{connected line strikes}
                \strike{general strike}
                
                Use these commands intermittently throughout the text to represent errors made by students. 
                Like words that are crossed out. Or attempts to correct mistakes.
                """
        )
        if strike
        else ""
    )

    complexity_str = (
        "The complexity level of the exercise is "
        + str(complexity_lv)
        + (
            " out of 5, "
            "where 0 is simple like "
            "Kindergarten level and level 5 is "
            "complex like Theoretical Quantum "
            "Physics on PHD level with very very "
            "long and complicated equations."
        )
    )

    word_irrgeularities_str = (
        (
            r"you need to use the command \processtext{content} on some sentences, "
            r"it is a latex command that introduces some "
            r"irregularities in the shape of its content, "
            r"that makes sure that the words are not in one straight line. "
            r"Make Sure that this command is only used on sentences and normal words"
            r" but not in math formulas or"
            r" math expressions, as there the command does not work!!"
            r"also the \processtext command is not compatible with the strike command!! "
            r"that means a word or sentence can only ever be contained in "
            r"one of those commands"
        )
        if word_wiggeling
        else ""
    )

    return (
        f"You are an helpful LLM that is part of generating data for a math handwriting recognition model. "
        f"You are asked to generate math exercises and solutions for our dataset. "
        f"The output you produced will be converted to handwriting"
        f"Write a math exercise  in {language} with the following requirements:\n\n1. "
        f"Include mathematical expressions and text explanations.\n\n2. {correct_str}\n\n3. "
        f"{complexity_str}\n\n"
        f"{strike_str}\n\n"
        f"{word_irrgeularities_str}\n\n"
        f"Just reply with the desired output, nothing else!!!"
    )
