import unittest
import os
import logging
from dotenv import load_dotenv
from bot.bot import SocialBot
from bot.config_manager import ConfigManager

class IntegrationTestSocialBot(unittest.TestCase):
    """Integration test suite for SocialBot class using real Instagram API and .env variables."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment by loading .env variables, validating them, and initializing SocialBot."""
        # Load environment variables from .env file
        load_dotenv()

        # Basic validation of required environment variables
        required_vars = ['instagram_api_key', 'instagram_access_token']
        for var in required_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"Missing required environment variable: {var}")
        
        # Initialize logging for better traceability
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)

        cls.logger.info("Initializing SocialBot with real Instagram API credentials.")
        # Initialize ConfigManager and SocialBot with real environment variables
        cls.config_manager = ConfigManager()
        cls.bot = SocialBot(cls.config_manager)

    def test_create_post(self):
        """Test creating a real post on Instagram."""
        caption = "Integration test post from bot"
        self.logger.info(f"Creating post with caption: {caption}")
        result = self.bot.post_image("instagram", caption=caption)
        
        # Check if the post was successful
        self.assertEqual(result['status'], 'success')
        self.assertIn('id', result)
        self.created_post_id = result['id']
        self.logger.info(f"Post created successfully with ID: {self.created_post_id}")

    def test_comment_to_post(self):
        """Test posting a real comment on the created post."""
        # Assuming the post has already been created
        if not hasattr(self, 'created_post_id'):
            self.skipTest("Post was not created, skipping comment test.")
        
        comment_text = "This is an integration test comment."
        self.logger.info(f"Commenting on post ID {self.created_post_id} with text: {comment_text}")
        result = self.bot.post_comment("instagram", media_id=self.created_post_id, comment_text=comment_text)
        
        # Check if the comment was successful
        self.assertEqual(result['status'], 'success')
        self.assertIn('id', result)
        self.comment_id = result['id']
        self.logger.info(f"Comment posted successfully with ID: {self.comment_id}")

    def test_reply_to_comments(self):
        """Test replying to a real comment on the post."""
        # Assuming the comment has already been created
        if not hasattr(self, 'comment_id'):
            self.skipTest("Comment was not created, skipping reply test.")
        
        reply_text = "This is an integration test reply."
        self.logger.info(f"Replying to comment ID {self.comment_id} with text: {reply_text}")
        result = self.bot.reply_to_comment("instagram", comment_id=self.comment_id, reply_text=reply_text)
        
        # Check if the reply was successful
        self.assertEqual(result['status'], 'success')
        self.assertIn('id', result)
        self.logger.info(f"Reply posted successfully with ID: {result['id']}")

    @classmethod
    def tearDownClass(cls):
        """Clean up by deleting the created post after tests are done."""
        if hasattr(cls, 'created_post_id'):
            cls.logger.info(f"Cleaning up: Deleting post with ID {cls.created_post_id}.")
            try:
                # Assuming a method exists to delete a post (this should be implemented in the actual bot code)
                result = cls.bot.platforms['instagram'].delete_post(cls.created_post_id)
                cls.logger.info(f"Post deleted successfully: {result}")
            except Exception as e:
                cls.logger.error(f"Failed to delete post: {e}")

if __name__ == '__main__':
    unittest.main()
