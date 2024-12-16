import openai

def clean_answer_format(answer):
    """
    Extracts and returns the content between LaTeX delimiters \begin{document} and \end{document}.

    :param answer: A string that may contain LaTeX delimiters.
    :return: The extracted content if delimiters are present, otherwise the original string.
    """
    # Define the keywords
    begin_keyword = r'\begin{document}'
    end_keyword = r'\end{document}'

    # Check if the string contains '\begin{document}'
    if begin_keyword in answer:
        # Find the start index after '\begin{document}'
        start_index = answer.find(begin_keyword) + len(begin_keyword)
        content = answer[start_index:].strip()

        # If '\end{document}' is present, remove it
        if end_keyword in content:
            end_index = content.find(end_keyword)
            content = content[:end_index].strip()

        return content
    else:
        return answer

class ModelCommunicator:
    def __init__(self, api_key, base_url="https://fmapi.swissai.cscs.ch"):
        """
        Initializes the ModelCommunicator instance.

        :param api_key: API key for the model
        :param base_url: API base URL
        """
        self.client = openai.Client(api_key=api_key, base_url=base_url)

    def communicate_with_model(
        self, prompt, model="meta-llama/Meta-Llama-3.1-70B-Instruct"
    ):
        """
        Handles communication with the LLaMA model.

        :param prompt: The input prompt for the model
        :param model: The name of the model to use (default is LLaMA-3.1-70B-Instruct)
        :return: The generated response from the model
        """
        try:
            # Send the request to the model
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )

            # Collect response chunks
            answer = ""
            print("Response:")
            print(response)
            for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            else:
                # Clean the answer format
                answer = clean_answer_format(answer)
                print("cleaned answer:")
                print(answer)
                return answer
        except openai.OpenAIError as e:
            print(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error during model communication: {str(e)}")

        return None
