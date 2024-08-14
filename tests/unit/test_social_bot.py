import unittest
from unittest.mock import MagicMock, patch
from bot.bot import SocialBot
from bot.config_manager import ConfigManager
from bot.social_media.instagram_api import InstagramIntegration
from bot.response_generator import ResponseGenerator

class TestSocialBot(unittest.TestCase):
    """Test suite for the SocialBot class."""

    def setUp(self):
        """Set up the test environment by mocking ConfigManager and initializing SocialBot."""
        # Mocking the ConfigManager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        
        # Creating the SocialBot instance with mocked dependencies
        self.social_bot = SocialBot(self.mock_config_manager)
        self.social_bot.platforms['instagram'] = MagicMock(spec=InstagramIntegration)
        self.social_bot.response_generator = MagicMock(spec=ResponseGenerator)

    def test_initialization(self):
        """Test the bot's initialization with the correct platforms and response generator."""
        self.assertIn('instagram', self.social_bot.platforms)
        self.assertIsInstance(self.social_bot.response_generator, MagicMock)

    @patch('bot.bot.SocialBot.confirm_action', return_value=True)
    def test_post_image_success(self, mock_confirm_action):
        """Test successful image posting to Instagram."""
        # Mocking the response generator to return a test caption and image URL
        self.social_bot.response_generator.generate_caption.return_value = "Test Caption"
        self.social_bot.response_generator.generate_image.return_value = "http://example.com/image.jpg"
        
        # Mocking the Instagram integration to simulate a successful post
        self.social_bot.platforms['instagram'].post_image.return_value = {"status": "success", "id": "post_id"}
        
        result = self.social_bot.post_image("instagram")
        self.assertEqual(result['status'], "success")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=False)
    def test_post_image_cancelled(self, mock_confirm_action):
        """Test handling when user cancels the image posting action."""
        result = self.social_bot.post_image("instagram")
        self.assertEqual(result['status'], "canceled")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=True)
    def test_post_comment_success(self, mock_confirm_action):
        """Test successful comment posting to Instagram."""
        self.social_bot.platforms['instagram'].post_comment.return_value = {"status": "success", "id": "comment_id"}
        
        result = self.social_bot.post_comment("instagram", "media_id")
        self.assertEqual(result['status'], "success")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=False)
    def test_post_comment_cancelled(self, mock_confirm_action):
        """Test handling when user cancels the comment posting action."""
        result = self.social_bot.post_comment("instagram", "media_id")
        self.assertEqual(result['status'], "canceled")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=True)
    def test_reply_to_comment_success(self, mock_confirm_action):
        """Test successful reply to a comment on Instagram."""
        self.social_bot.platforms['instagram'].reply_to_comment.return_value = {"status": "success", "id": "reply_id"}
        
        result = self.social_bot.reply_to_comment("instagram", "comment_id")
        self.assertEqual(result['status'], "success")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=False)
    def test_reply_to_comment_cancelled(self, mock_confirm_action):
        """Test handling when user cancels the reply action."""
        result = self.social_bot.reply_to_comment("instagram", "comment_id")
        self.assertEqual(result['status'], "canceled")
        mock_confirm_action.assert_called_once()

    @patch('bot.bot.SocialBot.confirm_action', return_value=True)
    def test_post_image_failure(self, mock_confirm_action):
        """Test failure scenario when posting an image to Instagram."""
        self.social_bot.response_generator.generate_caption.return_value = "Test Caption"
        self.social_bot.response_generator.generate_image.return_value = "http://example.com/image.jpg"
        
        # Simulating a failure in the Instagram integration
        self.social_bot.platforms['instagram'].post_image.side_effect = Exception("Failed to post image")
        
        with self.assertRaises(Exception) as context:
            self.social_bot.post_image("instagram")
        self.assertIn("Failed to post image", str(context.exception))
        mock_confirm_action.assert_called_once()

if __name__ == '__main__':
    unittest.main()
