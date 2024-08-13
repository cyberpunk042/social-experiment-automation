# bot/instagram_integration.py
from bot.social_media.base import SocialMediaIntegrationBase
import requests
from requests.exceptions import HTTPError
import logging
import time

class InstagramIntegration(SocialMediaIntegrationBase):
    BASE_URL = "https://api.instagram.com/v1"

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        self.logger = logging.getLogger(__name__)

    def get_posts(self, hashtag):
        url = f"{self.BASE_URL}/tags/{hashtag}/media/recent"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched posts for hashtag: {hashtag}")
            return response.json()['data']
        except HTTPError as http_err:
            self.logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.logger.error(f"An error occurred: {err}")
        finally:
            time.sleep(1)  # Rate limiting

    def post_response(self, post_id, response):
        url = f"{self.BASE_URL}/media/{post_id}/comments"
        try:
            response = self.session.post(url, data={'text': response})
            response.raise_for_status()
            self.logger.info(f"Successfully posted a comment on post {post_id}.")
        except HTTPError as http_err:
            self.logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.logger.error(f"An error occurred: {err}")
