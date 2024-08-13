import openai
import logging
from config_manager import ConfigManager

class OpenAIClient:
    def __init__(self, config_manager):
        """
        Initialize the OpenAIClient using the configuration manager to retrieve the API key.
        
        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("openai", "api_key")
        openai.api_key = self.api_key
        self.logger = logging.getLogger(__name__)
        self.logger.info("OpenAIClient initialized with provided API key.")

    def complete(self, prompt, max_tokens=150, temperature=0.7, n=1):
        """
        Generate a completion for the given prompt using the OpenAI API.
        
        :param prompt: The text prompt to generate a response for.
        :param max_tokens: The maximum number of tokens in the generated response.
        :param temperature: The sampling temperature to use, higher values mean more random completions.
        :param n: The number of completions to generate.
        :return: The generated text completion.
        """
        self.logger.info(f"Generating completion for prompt: {prompt[:50]}...")  # Log the start of completion generation
        try:
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                n=n
            )
            completion_text = response.choices[0].text.strip()
            self.logger.info(f"Generated completion: {completion_text[:50]}...")  # Log the generated completion
            return completion_text
        except openai.error.OpenAIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            return "I'm sorry, I can't generate a response right now."
        except Exception as e:
            self.logger.error(f"Unexpected error during completion generation: {e}")
            return "I'm sorry, I can't generate a response right now."
