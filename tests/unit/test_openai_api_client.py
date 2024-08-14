import unittest
from unittest.mock import patch, MagicMock
from bot.openai_client import OpenAIClient
from bot.config_manager import ConfigManager
from openai.error import OpenAIError

class TestOpenAIClient(unittest.TestCase):
    """Test suite for the OpenAIClient class."""

    def setUp(self):
        """Set up the test environment by mocking ConfigManager and initializing OpenAIClient."""
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get.side_effect = lambda key, default=None: {
            "openai_api_key": "test-api-key",
            "openai_engine": "davinci"
        }.get(key, default)
        
        self.client = OpenAIClient(self.mock_config_manager)
    
    @patch('openai.Completion.create')
    def test_complete_success(self, mock_create):
        """Test successful completion generation."""
        mock_create.return_value.choices = [MagicMock(text="Test completion")]
        result = self.client.complete("Test prompt")
        
        # Assert that the completion was generated as expected
        mock_create.assert_called_once()
        self.assertEqual(result, "Test completion")
    
    @patch('openai.Completion.create', side_effect=OpenAIError("API Error"))
    def test_complete_failure(self, mock_create):
        """Test handling of an API failure."""
        with self.assertRaises(OpenAIError):
            self.client.complete("Test prompt")

    @patch('openai.Completion.create', side_effect=TimeoutError("Timeout"))
    def test_complete_retry(self, mock_create):
        """Test retry logic on timeout."""
        with self.assertRaises(TimeoutError):
            self.client.complete("Test prompt", retries=1)
        
        # Ensure the retry logic respects the retries parameter
        self.assertEqual(mock_create.call_count, 1)

    @patch('openai.Completion.create')
    def test_complete_empty_prompt(self, mock_create):
        """Test completion with an empty prompt."""
        mock_create.return_value.choices = [MagicMock(text="")]
        result = self.client.complete("")
        self.assertEqual(result, "")
    
    def test_complete_invalid_max_tokens(self):
        """Test handling of invalid max_tokens parameter."""
        with self.assertRaises(ValueError):
            self.client.complete("Test prompt", max_tokens=5000)  # Exceeding the limit

    def test_complete_invalid_temperature(self):
        """Test handling of invalid temperature parameter."""
        with self.assertRaises(ValueError):
            self.client.complete("Test prompt", temperature=2.0)  # Temperature out of bounds

if __name__ == '__main__':
    unittest.main()
