import requests
import logging
from bot.config_manager import ConfigManager

class InstagramIntegration:
    BASE_URL = "https://api.instagram.com/v1"

    def __init__(self, config_manager):
        """
        Initialize the InstagramIntegration using the configuration manager to retrieve the API key.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("instagram_api_key")
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        self.logger = logging.getLogger(__name__)
        self.logger.info("InstagramIntegration initialized with provided API key.")

    def get_posts(self, hashtag):
        """
        Retrieve posts associated with a specific hashtag.

        :param hashtag: The hashtag to search for posts.
        :return: A list of posts associated with the hashtag.
        """
        url = f"{self.BASE_URL}/tags/{hashtag}/media/recent"
        self.logger.info(f"Fetching posts for hashtag: {hashtag}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            posts = response.json().get('data', [])
            self.logger.info(f"Retrieved {len(posts)} posts for hashtag: {hashtag}")
            return posts
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching posts for hashtag {hashtag}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error during post retrieval for hashtag {hashtag}: {e}")
            return []

    def post_response(self, post_id, response_text):
        """
        Post a response to a specific Instagram post.

        :param post_id: The ID of the post to respond to.
        :param response_text: The text of the response to post.
        :return: The result of the post operation.
        """
        url = f"{self.BASE_URL}/media/{post_id}/comments"
        self.logger.info(f"Posting response to post ID: {post_id}")
        try:
            response = self.session.post(url, data={'text': response_text})
            response.raise_for_status()
            self.logger.info(f"Successfully posted response to post ID: {post_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error posting response to post ID {post_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during response posting for post ID {post_id}: {e}")
            return None
