import requests
import logging
from bot.social_media.social_media_base import SocialMediaIntegration

class TwitterIntegration(SocialMediaIntegration):
    """
    TwitterIntegration handles interaction with the Twitter API,
    allowing operations such as posting tweets, replying to tweets, and following users.
    """

    BASE_URL = "https://api.twitter.com/2/"

    def __init__(self, config_manager):
        """
        Initialize the TwitterIntegration with API credentials and settings.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.api_key = config_manager.get("twitter_api_key")
        self.api_secret = config_manager.get("twitter_api_secret")
        self.bearer_token = config_manager.get("twitter_bearer_token")
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        })
        self.logger = logging.getLogger(__name__)
        self.logger.info("TwitterIntegration initialized with provided API credentials.")

    def get_posts(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve tweets associated with a specific hashtag.

        :param hashtag: The hashtag to search for tweets.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of tweets associated with the hashtag.
        """
        url = f"{self.BASE_URL}tweets/search/recent"
        params = {'query': f'#{hashtag}', 'tweet.fields': 'author_id,created_at'}
        self.logger.info(f"Fetching tweets for hashtag: #{hashtag}")

        attempt = 0
        while attempt < retries:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                tweets = response.json().get('data', [])
                self.logger.info(f"Retrieved {len(tweets)} tweets for hashtag: #{hashtag}")
                return tweets
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error fetching tweets for hashtag #{hashtag}: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during tweet retrieval for hashtag #{hashtag}: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to retrieve tweets for hashtag #{hashtag} after {retries} attempts.")
        return []

    def post_image(self, image_url, caption):
        """
        Post a tweet with an image and caption.

        :param image_url: The URL of the image to include in the tweet.
        :param caption: The text of the tweet.
        :return: The result of the tweet operation, including the tweet URL.
        """
        media_id = self._upload_media(image_url)
        if not media_id:
            self.logger.error(f"Failed to upload image to Twitter.")
            return {"status": "error", "message": "Image upload failed."}

        url = f"{self.BASE_URL}tweets"
        data = {"text": caption, "media": {"media_ids": [media_id]}}

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            tweet_id = response.json().get('data', {}).get('id')
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            self.logger.info(f"Tweet posted successfully: {tweet_url}")
            return {"status": "success", "url": tweet_url}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post tweet on Twitter: {e}")
            return {"status": "error", "message": str(e)}

    def post_comment(self, tweet_id, comment_text):
        """
        Post a comment (reply) on a specific tweet.

        :param tweet_id: The ID of the tweet to comment on.
        :param comment_text: The text of the comment (reply) to post.
        :return: The result of the comment operation.
        """
        url = f"{self.BASE_URL}tweets"
        data = {"text": comment_text, "in_reply_to_status_id": tweet_id}

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            comment_id = response.json().get('data', {}).get('id')
            self.logger.info(f"Comment posted on tweet ID {tweet_id}.")
            return {"status": "success", "comment_id": comment_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post comment on tweet ID {tweet_id}: {e}")
            return {"status": "error", "message": str(e)}

    def reply_to_comment(self, comment_id, reply_text):
        """
        Reply to a specific comment on a tweet.

        :param comment_id: The ID of the comment to reply to.
        :param reply_text: The text of the reply.
        :return: The result of the reply operation.
        """
        url = f"{self.BASE_URL}tweets"
        data = {"text": reply_text, "in_reply_to_status_id": comment_id}

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            reply_id = response.json().get('data', {}).get('id')
            self.logger.info(f"Reply posted to comment ID {comment_id}.")
            return {"status": "success", "reply_id": reply_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to reply to comment ID {comment_id}: {e}")
            return {"status": "error", "message": str(e)}

    def follow_users(self, amount, tags):
        """
        Follow users on Twitter based on specified tags.

        :param amount: Number of users to follow.
        :param tags: List of tags to use for finding users to follow.
        :return: The result of the follow operation.

        Raises:
            NotImplementedError: If Twitter API does not support this operation.
        """
        # Implementing follow operations via API requires additional permissions and compliance with Twitter's policies.
        raise NotImplementedError("Twitter API does not support automated follows through this integration.")

    def unfollow_users(self, amount):
        """
        Unfollow users on Twitter.

        :param amount: Number of users to unfollow.
        :return: The result of the unfollow operation.

        Raises:
            NotImplementedError: If Twitter API does not support this operation.
        """
        # Implementing unfollow operations via API requires additional permissions and compliance with Twitter's policies.
        raise NotImplementedError("Twitter API does not support automated unfollows through this integration.")

    def _upload_media(self, image_url):
        """
        Upload media to Twitter to include in a tweet.

        :param image_url: The URL of the image to upload.
        :return: The media ID for the uploaded image, or None if the upload fails.
        """
        url = f"{self.BASE_URL}media/upload"
        files = {'media': requests.get(image_url).content}

        try:
            response = self.session.post(url, files=files)
            response.raise_for_status()
            media_id = response.json().get('media_id_string')
            self.logger.info(f"Media uploaded successfully: {media_id}")
            return media_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to upload media to Twitter: {e}")
            return None
