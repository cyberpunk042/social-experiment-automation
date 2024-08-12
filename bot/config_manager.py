from dotenv import load_dotenv
import os

class ConfigManager:
    """Manages the configuration settings for the bot."""

    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        self.instagram_api_key = os.getenv('INSTAGRAM_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # Ensure that the API keys are present
        if not self.instagram_api_key or not self.openai_api_key:
            raise ValueError("API keys for Instagram or OpenAI are missing in the .env file.")

    # Add any additional configuration methods here
