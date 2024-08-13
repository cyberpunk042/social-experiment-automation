import requests
import logging
from requests_oauthlib import OAuth1
from config_manager import ConfigManager

class TwitterIntegration:
    BASE_URL = "https://api.twitter.com/1.1"

    def __init__(self, config_manager):
        """
        Initialize the TwitterIntegration using the configuration manager to retrieve the API credentials.
        
        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("twitter", "api_key")
        self.api_secret_key = config_manager.get("twitter", "api_secret_key")
        self.access_token = config_manager.get("twitter", "access_token")
        self.access_token_secret = config_manager.get("twitter", "access_token_secret")
        
        self.session = self._create_session()
        self.logger = logging.getLogger(__name__)
        self.logger.info("TwitterIntegration initialized with provided credentials.")

    def _create_session(self):
        """
        Create and return a session with OAuth1 authentication for Twitter API.
        
        :return: A requests.Session object configured with OAuth1 authentication.
        """
        auth = OAuth1(self.api_key, self.api_secret_key, self.access_token, self.access_token_secret)
        session = requests.Session()
        session.auth = auth
        return session

    def get_tweets(self, hashtag):
        """
        Retrieve tweets associated with a specific hashtag.
        
        :param hashtag: The hashtag to search for tweets.
        :return: A list of tweets associated with the hashtag.
        """
        url = f"{self.BASE_URL}/search/tweets.json"
        params = {'q': f'#{hashtag}', 'count': 100}
        self.logger.info(f"Fetching tweets for hashtag: {hashtag}")
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            tweets = response.json().get('statuses', [])
            self.logger.info(f"Retrieved {len(tweets)} tweets for hashtag: {hashtag}")
            return tweets
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching tweets for hashtag {hashtag}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error during tweet retrieval: {e}")
            return []

    def post_tweet(self, tweet_text):
        """
        Post a tweet to the authenticated user's timeline.
        
        :param tweet_text: The text of the tweet to post.
        :return: The result of the tweet post operation.
        """
        url = f"{self.BASE_URL}/statuses/update.json"
        self.logger.info(f"Posting tweet: {tweet_text[:50]}...")  # Log the start of tweet posting
        try:
            response = self.session.post(url, data={'status': tweet_text})
            response.raise_for_status()
            self.logger.info(f"Successfully posted tweet: {tweet_text[:50]}...")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error posting tweet: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during tweet posting: {e}")
            return None
