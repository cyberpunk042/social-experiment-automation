import unittest
from unittest.mock import MagicMock, patch
from bot.social_media.instagram_api import InstagramIntegration
from bot.config_manager import ConfigManager
from requests.exceptions import RequestException

class TestInstagramIntegration(unittest.TestCase):
    """Test suite for the InstagramIntegration class."""

    def setUp(self):
        """Set up the test environment by mocking ConfigManager and initializing InstagramIntegration."""
        # Mocking the ConfigManager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get.side_effect = lambda key, default=None: {
            "instagram_api_key": "test-api-key",
            "instagram_access_token": "test-access-token"
        }.get(key, default)
        
        self.instagram_integration = InstagramIntegration(self.mock_config_manager)

    def test_initialization_graph_api(self):
        """Test initialization using the Graph API."""
        self.assertEqual(self.instagram_integration.base_url, "https://graph.instagram.com/")
        self.assertEqual(self.instagram_integration.access_token, "test-access-token")
        self.assertIn('Authorization', self.instagram_integration.session.headers)
        self.assertEqual(self.instagram_integration.session.headers['Authorization'], 'Bearer test-access-token')

    def test_initialization_basic_display_api(self):
        """Test initialization using the Basic Display API."""
        instagram_integration = InstagramIntegration(self.mock_config_manager, use_graph_api=False)
        self.assertEqual(instagram_integration.base_url, "https://api.instagram.com/v1")
        self.assertEqual(instagram_integration.access_token, None)
        self.assertIn('Authorization', instagram_integration.session.headers)
        self.assertEqual(instagram_integration.session.headers['Authorization'], 'Bearer test-api-key')

    @patch('requests.Session.post')
    def test_post_image_success(self, mock_post):
        """Test successful image posting to Instagram."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "test-post-id"}

        result = self.instagram_integration.post_image("http://example.com/image.jpg", "Test caption")
        
        # Assert that the POST request was made to the correct URL with the correct data
        mock_post.assert_called_once()
        self.assertIn("test-post-id", result["id"])

    @patch('requests.Session.post', side_effect=RequestException("Failed to post image"))
    def test_post_image_failure(self, mock_post):
        """Test failure scenario when posting an image to Instagram."""
        with self.assertRaises(Exception) as context:
            self.instagram_integration.post_image("http://example.com/image.jpg", "Test caption")
        
        self.assertIn("Failed to post image", str(context.exception))
        
    @patch('requests.Session.post')
    def test_post_image_empty_caption(self, mock_post):
        """Test posting an image with an empty caption."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "test-post-id"}

        result = self.instagram_integration.post_image("http://example.com/image.jpg", "")
        mock_post.assert_called_once()
        self.assertEqual(result["id"], "test-post-id")

    @patch('requests.Session.get')
    def test_get_posts_success(self, mock_get):
        """Test successful retrieval of posts by hashtag."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [{"id": "post1"}, {"id": "post2"}]}

        result = self.instagram_integration.get_posts("testhashtag")
        
        # Assert the correct API endpoint was called
        mock_get.assert_called_once()
        self.assertEqual(len(result), 2)

    @patch('requests.Session.get', side_effect=RequestException("Failed to retrieve posts"))
    def test_get_posts_failure(self, mock_get):
        """Test failure scenario when retrieving posts by hashtag."""
        with self.assertRaises(Exception) as context:
            self.instagram_integration.get_posts("testhashtag")
        self.assertIn("Failed to retrieve posts", str(context.exception))

    @patch('requests.Session.get')
    def test_get_posts_empty_hashtag(self, mock_get):
        """Test retrieving posts with an empty hashtag."""
        with self.assertRaises(ValueError):
            self.instagram_integration.get_posts("")

if __name__ == '__main__':
    unittest.main()
