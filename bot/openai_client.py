# bot/openai_client.py
import openai
import logging

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.logger = logging.getLogger(__name__)

    def complete(self, prompt, max_tokens=150, temperature=0.7, n=1):
        try:
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                n=n
            )
            return [choice.text.strip() for choice in response.choices]
        except openai.error.OpenAIError as e:
            self.logger.error(f"An error occurred with OpenAI service: {e}")
            return None
