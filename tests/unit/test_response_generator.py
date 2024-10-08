import unittest
from unittest.mock import MagicMock, patch
from bot.response_generator import ResponseGenerator
from bot.openai_client import OpenAIClient
from bot.database_client import DatabaseClient
from bot.user_preferences import UserPreferences

class TestResponseGenerator(unittest.TestCase):
    """Test suite for the ResponseGenerator class."""

    def setUp(self):
        """Set up the test environment by mocking dependencies and initializing ResponseGenerator."""
        # Mocking dependencies
        self.mock_openai_client = MagicMock(spec=OpenAIClient)
        self.mock_database_client = MagicMock(spec=DatabaseClient)
        self.mock_user_preferences = MagicMock(spec=UserPreferences)
        
        # Initializing ResponseGenerator with mocked dependencies
        self.response_generator = ResponseGenerator(
            self.mock_openai_client,
            self.mock_database_client,
            self.mock_user_preferences
        )

    def test_generate_caption_success(self):
        """Test successful caption generation with valid data."""
        # Mocking database response and user preferences
        self.mock_database_client.get_data.return_value = ["Sample caption"]
        self.mock_user_preferences.select_preferred_caption.return_value = "Sample caption"
        self.mock_user_preferences.response_style = "informal"
        self.mock_user_preferences.content_tone = "friendly"

        self.mock_openai_client.complete.return_value = "Personalized caption"

        result = self.response_generator.generate_caption()
        self.assertEqual(result, "Personalized caption")

    def test_generate_caption_no_captions(self):
        """Test handling when no captions are found in the database."""
        # Simulating a situation where no captions are available
        self.mock_database_client.get_data.return_value = []

        with self.assertRaises(Exception) as context:
            self.response_generator.generate_caption()

        self.assertIn("No captions found", str(context.exception))

    def test_generate_caption_empty_database_response(self):
        """Test handling of an empty response from the database."""
        self.mock_database_client.get_data.return_value = []

        with self.assertRaises(Exception) as context:
            self.response_generator.generate_caption()

        self.assertIn("No captions found", str(context.exception))

    def test_generate_caption_missing_user_preferences(self):
        """Test handling when user preferences are not set."""
        self.mock_database_client.get_data.return_value = ["Sample caption"]
        self.mock_user_preferences.select_preferred_caption.return_value = "Sample caption"
        self.mock_user_preferences.response_style = None  # Missing preferences
        self.mock_user_preferences.content_tone = None

        with self.assertRaises(Exception) as context:
            self.response_generator.generate_caption()

        self.assertIn("Error retrieving or personalizing caption", str(context.exception))

    @patch('bot.openai_client.OpenAIClient.generate_image')
    def test_generate_image_success(self, mock_generate_image):
        """Test successful image generation with valid preferences."""
        self.mock_user_preferences.get_image_preferences.return_value = {
            "style": "minimalist",
            "color_scheme": "monochrome"
        }
        mock_generate_image.return_value = "http://example.com/generated_image.png"

        result = self.response_generator.generate_image("Sample caption")
        self.assertEqual(result, "http://example.com/generated_image.png")

    @patch('bot.openai_client.OpenAIClient.generate_image', side_effect=Exception("Image generation failed"))
    def test_generate_image_failure(self, mock_generate_image):
        """Test handling of image generation failure."""
        self.mock_user_preferences.get_image_preferences.return_value = {
            "style": "minimalist",
            "color_scheme": "monochrome"
        }

        with self.assertRaises(Exception) as context:
            self.response_generator.generate_image("Sample caption")

        self.assertIn("Image generation failed", str(context.exception))

    def test_generate_image_missing_preferences(self):
        """Test handling when image preferences are missing."""
        self.mock_user_preferences.get_image_preferences.return_value = {}

        with self.assertRaises(Exception) as context:
            self.response_generator.generate_image("Sample caption")

        self.assertIn("Image generation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
