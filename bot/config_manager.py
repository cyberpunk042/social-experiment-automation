import os
import logging
import threading
from dotenv import load_dotenv

class ConfigManager:
    _instance = None
    _lock = threading.Lock()  # Lock for thread safety

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, env_file_path=".env"):
        """
        Initialize the ConfigManager class.

        This constructor loads environment variables from the specified .env file
        and initializes the configuration dictionary.

        :param env_file_path: Path to the .env file containing environment variables.
        """
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

        This method loads and validates environment variables, storing them in the config dictionary.
        Additional sources can be added if needed.
        """
        try:
            self.config.update({
                'openai_api_key': self._validate_env_var('OPENAI_API_KEY'),
                'supabase_url': self._validate_env_var('SUPABASE_URL'),
                'supabase_key': self._validate_env_var('SUPABASE_KEY'),
                'instagram_api_key': os.getenv('INSTAGRAM_API_KEY'),
                'twitter_api_key': os.getenv('TWITTER_API_KEY'),
                'twitter_api_secret_key': os.getenv('TWITTER_API_SECRET_KEY'),
                'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                'twitter_access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            })
            self.logger.info("Configuration loaded successfully.")
        except Exception as e:
            self.logger.exception(f"Error loading configuration: {e}")
            raise

    def _validate_env_var(self, var_name):
        """
        Validate that a required environment variable is set.

        :param var_name: The name of the environment variable to validate.
        :return: The value of the environment variable if valid.
        :raises ValueError: If the environment variable is missing or empty.
        """
        value = os.getenv(var_name)
        if not value:
            self.logger.error(f"Environment variable {var_name} is missing or empty.")
            raise ValueError(f"Environment variable {var_name} is missing or empty.")
        return value

    def get(self, key, default=None):
        """
        Retrieve a configuration value.

        :param key: The key of the configuration setting.
        :param default: The default value to return if the key is not found.
        :return: The configuration value.
        """
        return self.config.get(key, default)

    def reload(self):
        """
        Reload the configuration settings.

        This method reloads the environment variables and updates the configuration dictionary.
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
