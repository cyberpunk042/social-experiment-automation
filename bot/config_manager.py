from dotenv import load_dotenv
import os

import os
import logging
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, env_file_path=".env"):
        """
        Initialize the ConfigManager, loading configuration settings from a .env file.
        
        :param env_file_path: The path to the .env file. Defaults to ".env".
        """
        self.config = {}
        self.logger = logging.getLogger(__name__)
        self.load_from_env_file(env_file_path)

    def load_from_env_file(self, env_file_path):
        """
        Load configuration settings from a .env file. Configuration settings are grouped by module,
        making it clear which settings belong to which module.
        
        :param env_file_path: The path to the .env file.
        """
        self.logger.info(f"Loading configuration from .env file: {env_file_path}")
        load_dotenv(env_file_path)
        self.load_from_env()

    def load_from_env(self):
        """
        Load configuration settings from environment variables, grouping them by module based on prefixes.
        """
        self.logger.info("Loading configuration from environment variables.")
        modules = ['openai', 'twitter', 'instagram']
        for module in modules:
            self.config[module] = self._load_module_from_env(module.upper())

    def _load_module_from_env(self, module_prefix):
        """
        Load configuration settings for a specific module from environment variables.
        
        :param module_prefix: The uppercase prefix for the module, e.g., "OPENAI" or "TWITTER".
        :return: A dictionary of settings for the module.
        """
        self.logger.info(f"Loading {module_prefix} configuration from environment variables.")
        module_config = {}
        try:
            for key in os.environ:
                if key.startswith(f"{module_prefix}_"):
                    config_key = key[len(module_prefix) + 1:].lower()  # Strip the prefix and convert to lowercase
                    module_config[config_key] = os.getenv(key)
                    self.logger.debug(f"Loaded {config_key} for {module_prefix} from environment variable.")
        except Exception as e:
            self.logger.error(f"Unexpected error loading {module_prefix} configuration from environment variables: {e}")
        return module_config

    def get(self, module, key, default=None):
        """
        Retrieve a configuration value by module and key.
        
        :param module: The module name, e.g., "openai" or "twitter".
        :param key: The configuration key to retrieve.
        :param default: The default value to return if the key is not found.
        :return: The configuration value, or the default value if the key is not found.
        """
        value = self.config.get(module, {}).get(key, default)
        if value is None:
            self.logger.warning(f"Configuration key {key} for module {module} not found. Returning default value.")
        else:
            self.logger.debug(f"Retrieved value for {module}.{key}: {value}")
        return value
