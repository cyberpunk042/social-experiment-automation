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
            # Simple rate limiting
            time.sleep(1)  # Adjust the sleep time as needed
    
    def post_response(self, post_id, response):
        url = f"{self.BASE_URL}/media/{post_id}/comments"
        try:
            response = self.session.post(url, data={'text': response})
            response.raise_for_status()
        except HTTPError as http_err:
            # Specific HTTP error handling
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            # General error handling
            print(f"An error occurred: {err}")
