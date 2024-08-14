import openai
import logging
from config_manager import ConfigManager
from time import sleep
from requests.exceptions import Timeout, RequestException

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
        :raises Exception: If the completion fails after all retries.
        """
        # Parameter validation
        if not 1 <= max_tokens <= 2048:
            raise ValueError("max_tokens must be between 1 and 2048.")
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0.")
        
        self.logger.info(f"Generating completion for prompt: {prompt[:50]}...")

        # Retry logic
        for attempt in range(retries):
            try:
                response = openai.Completion.create(
                    engine=self.engine,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n,
                    timeout=timeout
                )
                self.logger.info("Completion generated successfully.")
                return response.choices[0].text.strip()

            except (Timeout, RequestException) as e:
                self.logger.warning(f"Request failed with error: {e}. Retrying {retries - attempt - 1} more times...")
                sleep(2)  # Backoff before retrying

            except openai.error.RateLimitError as e:
                self.logger.error("Rate limit exceeded. Pausing before retrying...")
                sleep(60)  # Wait for a minute before retrying
                continue

            except openai.error.OpenAIError as e:
                self.logger.error(f"OpenAI API error: {e}.")
                raise

        # If all retries fail, raise an exception
        self.logger.error("Failed to generate completion after multiple attempts.")
        raise Exception("Failed to generate completion after multiple attempts.")

    def generate_image(self, prompt, n=1, size="1024x1024", retries=3, timeout=30):
        """
        Generate an image based on the provided prompt using DALL-E via OpenAI API.

        :param prompt: The text prompt to generate an image for.
        :param n: The number of images to generate.
        :param size: The size of the generated images (e.g., "1024x1024").
        :param retries: The number of times to retry the request in case of a transient error.
        :param timeout: Timeout in seconds for the API call.
        :return: A URL to the generated image.
        :raises Exception: If the image generation fails after all retries.
        """
        self.logger.info(f"Generating image for prompt: {prompt[:50]}...")

        for attempt in range(retries):
            try:
                response = openai.Image.create(
                    prompt=prompt,
                    n=n,
                    size=size,
                    timeout=timeout
                )
                self.logger.info("Image generated successfully.")
                return response['data'][0]['url']

            except (Timeout, RequestException) as e:
                self.logger.warning(f"Request failed with error: {e}. Retrying {retries - attempt - 1} more times...")
                sleep(2)

            except openai.error.RateLimitError as e:
                self.logger.error("Rate limit exceeded. Pausing before retrying...")
                sleep(60)
                continue

            except openai.error.OpenAIError as e:
                self.logger.error(f"OpenAI API error: {e}.")
                raise

        self.logger.error("Failed to generate image after multiple attempts.")
        raise Exception("Failed to generate image after multiple attempts.")
