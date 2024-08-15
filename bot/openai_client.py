import os
import openai
from openai import OpenAI
import logging
from user_preferences import UserPreferences
from config_manager import ConfigManager
from time import sleep
from requests.exceptions import Timeout, RequestException

class OpenAIClient:
    def __init__(self, config_manager: ConfigManager, user_preferences: UserPreferences):
        self.api_key = config_manager.get("openai_api_key")
        if not self.api_key:
            raise ValueError("API key not found. Please ensure it is set in the environment or .env file.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = config_manager.get("openai_engine", "gpt-3.5-turbo")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OpenAIClient initialized with API key: {self.api_key[:5]}...")
        self.user_preferences = user_preferences

    def complete(self, prompt, max_tokens=150, temperature=0.7, retries=3, timeout=10):
        self.logger.info(f"Generating completion for prompt: {prompt[:50]}...")

        # Retry logic
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Correctly accessing the content of the response
                return response.choices[0].message.content.strip()
            except (Timeout, RequestException) as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                sleep(2)
            except Exception as e:
                self.logger.error(f"Failed to generate completion: {e}")
                raise

        raise Exception("Max retries exceeded. Failed to generate completion.")


    def generate_image(self, caption, n=1, size="1024x1024", retries=3, timeout=30):
        """
        Generate an image based on the provided caption using DALL-E via OpenAI API.

        :param caption: The text caption to generate an image for.
        :param n: The number of images to generate.
        :param size: The size of the generated images (e.g., "1024x1024").
        :param retries: The number of times to retry the request in case of a transient error.
        :param timeout: Timeout in seconds for the API call.
        :return: A URL to the generated image.
        :raises Exception: If the image generation fails after all retries.
        """
        self.logger.info(f"Generating image for caption: {caption[:50]}...")

        preferences = self.user_preferences.get_preferences()
        
        # Handle missing preferences by providing defaults
        style = preferences.get('style', 'natural')
        quality = preferences.get('quality', 'standard')
        
        for attempt in range(retries):
            try:
                response = self.client.images.generate(
                    prompt=caption,
                    model="dall-e-3",  # Adjust as needed based on the models available
                    n=n,
                    quality=quality,
                    response_format="url",
                    size=size,
                    style=style,
                    timeout=timeout
                )
                self.logger.info("Image generated successfully.")
                return response.data[0].url

            except (Timeout, RequestException) as e:
                self.logger.warning(f"Request failed with error: {e}. Retrying {retries - attempt - 1} more times...")
                sleep(2)

            except openai.APIConnectionError as e:
                self.logger.error("Failed to connect to the OpenAI API.")
                sleep(60)
                continue

            except openai.RateLimitError as e:
                self.logger.error("Rate limit exceeded. Pausing before retrying...")
                sleep(60)
                continue

            except openai.APIError as e:
                self.logger.error(f"OpenAI API error: {e}.")
                raise

        self.logger.error("Failed to generate image after multiple attempts.")
        raise Exception("Failed to generate image after multiple attempts.")
