import openai
import logging
from bot.config_manager import ConfigManager
from time import sleep

class OpenAIClient:
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the OpenAIClient using the configuration manager to retrieve the API key and engine.
        
        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("openai_api_key")
        openai.api_key = self.api_key
        self.engine = config_manager.get("openai_engine", "davinci")
        self.logger = logging.getLogger(__name__)
        self.logger.info("OpenAIClient initialized with provided API key and engine.")

    def complete(self, prompt, max_tokens=150, temperature=0.7, n=1, retries=3, timeout=10):
        """
        Generate a completion for the given prompt using the OpenAI API.

        :param prompt: The text prompt to generate a response for.
        :param max_tokens: The maximum number of tokens in the generated response.
        :param temperature: The sampling temperature to use, higher values mean more random completions.
        :param n: The number of completions to generate.
        :param retries: The number of times to retry the request in case of a transient error.
        :param timeout: Timeout in seconds for the API call.
        :return: The generated text completion.
        """
        self.logger.info(f"Generating completion for prompt: {prompt[:50]}...")

        # Validate parameters
        if not prompt or max_tokens <= 0 or temperature < 0 or temperature > 1 or n <= 0:
            self.logger.error("Invalid parameters for completion generation.")
            return "Invalid input parameters."

        attempt = 0
        while attempt < retries:
            try:
                response = openai.Completion.create(
                    engine=self.engine,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n,
                    timeout=timeout
                )
                completion_text = response.choices[0].text.strip()
                self.logger.info(f"Generated completion: {completion_text[:50]}...")
                return completion_text

            except openai.error.OpenAIError as e:
                self.logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if isinstance(e, openai.error.RateLimitError):
                    sleep(2 ** attempt)  # Exponential backoff for rate limit errors
                else:
                    break  # Do not retry for non-transient errors

            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                break

            attempt += 1
            self.logger.info(f"Retrying... (attempt {attempt + 1})")

        return "I'm sorry, I can't generate a response right now."
