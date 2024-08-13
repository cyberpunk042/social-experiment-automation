import os
import logging
from dotenv import load_dotenv

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, env_file_path=".env"):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        load_dotenv(env_file_path)

        self.config = {}
        self._load_config()

        self._initialized = True

    def _load_config(self):
        """
        Load configuration settings from environment variables.
        This method can be extended to load from other sources if needed.
        """
        try:
            # Load standard environment variables
            self.config.update({
                'openai_api_key': os.getenv('OPENAI_API_KEY'),
                'supabase_url': os.getenv('SUPABASE_URL'),
                'supabase_key': os.getenv('SUPABASE_KEY'),
                'instagram_api_key': os.getenv('INSTAGRAM_API_KEY'),
                'twitter_api_key': os.getenv('TWITTER_API_KEY'),
                'twitter_api_secret_key': os.getenv('TWITTER_API_SECRET_KEY'),
                'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                'twitter_access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            })

            # Log which environment variables were successfully loaded
            for key, value in self.config.items():
                if value is not None:
                    self.logger.info(f"Loaded configuration for {key}")
                else:
                    self.logger.warning(f"Configuration for {key} not found, using default or empty value.")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def get(self, key, default=None):
        """
        Retrieve a configuration value.
        
        :param key: The key of the configuration setting.
        :param default: The default value to return if the key is not found.
        :return: The value of the configuration setting, or the default if not found.
        """
        return self.config.get(key, default)

    def reload(self):
        """
        Reload the configuration settings.
        Useful if environment variables or external sources change during runtime.
        """
        self._load_config()
        self.logger.info("Configuration reloaded.")

    def set(self, key, value):
        """
        Set or update a configuration value.
        
        :param key: The key of the configuration setting.
        :param value: The value to set.
        """
        self.config[key] = value
        self.logger.info(f"Configuration for {key} set to {value}.")
