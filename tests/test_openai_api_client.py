import unittest
from unittest.mock import patch, MagicMock
from bot.openai_client import OpenAIClient
from bot.config_manager import ConfigManager
from openai.error import OpenAIError

class TestOpenAIClient(unittest.TestCase):
    
    def setUp(self):
        # Mocking the ConfigManager to provide consistent test data
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get.side_effect = lambda key, default=None: {
            "openai_api_key": "test-api-key",
            "openai_engine": "davinci"
        }.get(key, default)
        
        self.client = OpenAIClient(self.mock_config_manager)
    
    @patch('openai.Completion.create')
    def test_complete_success(self, mock_create):
        # Simulate a successful completion
        mock_create.return_value.choices = [MagicMock(text="Test completion")]
        result = self.client.complete("Test prompt")
        self.assertEqual(result, "Test completion")
    
    @patch('openai.Completion.create', side_effect=OpenAIError("API Error"))
    def test_complete_failure(self, mock_create):
        # Simulate an API failure
        with self.assertRaises(OpenAIError):
            self.client.complete("Test prompt")

    @patch('openai.Completion.create', side_effect=TimeoutError("Timeout"))
    def test_complete_retry(self, mock_create):
        # Simulate a timeout with retries
        with self.assertRaises(TimeoutError):
            self.client.complete("Test prompt", retries=1)
        self.assertEqual(mock_create.call_count, 1)  # Only one attempt because retries=1

if __name__ == '__main__':
    unittest.main()
