import requests
import logging
import time
from requests_oauthlib import OAuth1
from bot.config_manager import ConfigManager

class TwitterIntegration:
    BASE_URL = "https://api.twitter.com/1.1"

    def __init__(self, config_manager):
        """
        Initialize the TwitterIntegration using the configuration manager to retrieve the API credentials.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("twitter_api_key")
        self.api_secret_key = config_manager.get("twitter_api_secret_key")
        self.access_token = config_manager.get("twitter_access_token")
        self.access_token_secret = config_manager.get("twitter_access_token_secret")
        
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

    def get_tweets(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve tweets associated with a specific hashtag with retry logic.

        :param hashtag: The hashtag to search for tweets.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of tweets associated with the hashtag.
        """
        url = f"{self.BASE_URL}/search/tweets.json"
        params = {'q': f'#{hashtag}', 'count': 100}
        self.logger.info(f"Fetching tweets for hashtag: {hashtag}")
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                tweets = response.json().get('statuses', [])
                self.logger.info(f"Retrieved {len(tweets)} tweets for hashtag: {hashtag}")
                return tweets
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error fetching tweets for hashtag {hashtag}: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during tweet retrieval for hashtag {hashtag}: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to retrieve tweets for hashtag {hashtag} after {retries} attempts.")
        return []

    def post_tweet(self, tweet_text, retries=3, backoff_factor=0.3):
        """
        Post a tweet to the authenticated user's timeline with retry logic.

        :param tweet_text: The text of the tweet to post.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: The result of the post operation.
        """
        url = f"{self.BASE_URL}/statuses/update.json"
        self.logger.info(f"Posting tweet: {tweet_text}")
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.post(url, data={"status": tweet_text})
                response.raise_for_status()
                result = response.json()
                self.logger.info(f"Tweet posted: {result}")
                return result
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error posting tweet: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during tweet posting: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to post tweet after {retries} attempts.")
        return None
