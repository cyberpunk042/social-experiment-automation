import os
import openai
from openai import OpenAI
import logging
from user_preferences import UserPreferences
from config_manager import ConfigManager
from time import sleep
from requests.exceptions import Timeout, RequestException
import requests
import re
from datetime import datetime
from pathlib import Path

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
        Generate an image based on the provided caption using DALL-E via OpenAI API and save it locally.

        :param caption: The text caption to generate an image for.
        :param n: The number of images to generate.
        :param size: The size of the generated images (e.g., "1024x1024").
        :param retries: The number of times to retry the request in case of a transient error.
        :param timeout: Timeout in seconds for the API call.
        :return: The file path of the saved image.
        :raises Exception: If the image generation fails after all retries.
        """
        self.logger.info(f"Generating image for caption: {caption[:50]}...")

        preferences = self.user_preferences.get_preferences()
        style = preferences.get('style', 'natural')
        quality = preferences.get('quality', 'standard')

        for attempt in range(retries):
            try:
                response = self.client.images.generate(
                    prompt=caption,
                    model="dall-e-3",
                    n=n,
                    quality=quality,
                    response_format="url",
                    size=size,
                    style=style,
                    timeout=timeout
                )
                image_url = response.data[0].url
                self.logger.info("Image generated successfully.")

                # Generate a meaningful filename
                filename = self.generate_filename(caption)
                local_image_path = self.save_image_locally(image_url, filename)
                return image_url

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

    def generate_filename(self, caption):
        # Clean up the caption to use as part of the filename
        safe_caption = re.sub(r'\W+', '-', caption[:50]).lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_caption}_{timestamp}.png"
        return filename

    def save_image_locally(self, image_url, filename):
        try:
            response = requests.get(image_url)
            response.raise_for_status()

            local_file_path = Path("images") / filename
            local_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_file_path, "wb") as file:
                file.write(response.content)
            
            self.logger.info(f"Image saved locally at: {local_file_path}")
            return local_file_path

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download image: {e}")
            raise