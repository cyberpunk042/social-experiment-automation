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
        return self._make_api_call(url, "GET")

    def post_response(self, post_id, response):
        url = f"{self.BASE_URL}/media/{post_id}/comments"
        data = {'text': response}
        return self._make_api_call(url, "POST", data=data)

    def _make_api_call(self, url, method, data=None):
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API call error: {e}")
            time.sleep(1)  # Basic rate limit handling
            return None
