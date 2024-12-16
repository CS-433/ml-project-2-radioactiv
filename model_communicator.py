import openai


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
                print("answer:")
                print(answer)
                return answer
        except openai.OpenAIError as e:
            print(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error during model communication: {str(e)}")

        return None
