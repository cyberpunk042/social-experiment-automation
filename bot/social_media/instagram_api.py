import requests
import logging
import time

class InstagramIntegration:
    def __init__(self, config_manager, use_graph_api=True):
        '''
        Initialize the InstagramIntegration using the configuration manager to retrieve the API key.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        :param use_graph_api: Boolean flag to determine whether to use the Graph API or Basic Display API.
        '''
        self.use_graph_api = use_graph_api
        self.api_key = config_manager.get("instagram_api_key")
        self.base_url = "https://graph.instagram.com/" if use_graph_api else "https://api.instagram.com/v1"
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_key}' if not use_graph_api else ''})
        self.logger = logging.getLogger(__name__)
        self.logger.info("InstagramIntegration initialized with provided API key.")

    def get_posts(self, hashtag, retries=3, backoff_factor=0.3):
        '''
        Retrieve posts associated with a specific hashtag with retry logic.

        :param hashtag: The hashtag to search for posts.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of posts associated with the hashtag.
        '''
        url = f"{self.base_url}/tags/{hashtag}/media/recent" if not self.use_graph_api else f"{self.base_url}/{hashtag}/media/recent"
        self.logger.info(f"Fetching posts for hashtag: {hashtag}")
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.get(url, params={'access_token': self.api_key} if self.use_graph_api else None)
                response.raise_for_status()
                posts = response.json().get('data', [])
                self.logger.info(f"Retrieved {len(posts)} posts for hashtag: {hashtag}")
                return posts
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error fetching posts for hashtag {hashtag}: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during post retrieval for hashtag {hashtag}: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to retrieve posts for hashtag {hashtag} after {retries} attempts.")
        return []

    def post_response(self, post_id, response_text, retries=3, backoff_factor=0.3):
        '''
        Post a response to a specific Instagram post with retry logic.

        :param post_id: The ID of the post to respond to.
        :param response_text: The text of the response to post.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: The result of the post operation.
        '''
        url = f"{self.base_url}/media/{post_id}/comments" if not self.use_graph_api else f"{self.base_url}/{post_id}/comments"
        self.logger.info(f"Posting response to post ID: {post_id}")
        attempt = 0
        while attempt < retries:
            try:
                data = {"text": response_text} if not self.use_graph_api else {"message": response_text}
                response = self.session.post(url, data=data, params={'access_token': self.api_key} if self.use_graph_api else None)
                response.raise_for_status()
                result = response.json()
                self.logger.info(f"Response posted to post ID {post_id}: {result}")
                return result
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error posting response to post ID {post_id}: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during response posting for post ID {post_id}: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to post response to post ID {post_id} after {retries} attempts.")
        return None

    def post_comment(self, media_id, comment_text):
        '''
        Post a comment on a specific Instagram media (post).

        :param media_id: The ID of the media (post) to comment on.
        :param comment_text: The text of the comment to post.
        :return: The result of the comment operation.
        '''
        url = f"{self.base_url}{media_id}/comments" if self.use_graph_api else f"{self.base_url}/media/{media_id}/comments"
        data = {"text": comment_text} if not self.use_graph_api else {"message": comment_text}
        params = {'access_token': self.api_key} if self.use_graph_api else None
        try:
            response = self.session.post(url, data=data, params=params)
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Comment posted on media ID {media_id}: {comment_text}")
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post comment on media ID {media_id}: {e}")
            return {"status": "failed", "reason": str(e)}

    def reply_to_comment(self, comment_id, reply_text):
        '''
        Reply to a specific comment on an Instagram media (post).

        :param comment_id: The ID of the comment to reply to.
        :param reply_text: The text of the reply.
        :return: The result of the reply operation.
        '''
        url = f"{self.base_url}{comment_id}/replies" if self.use_graph_api else f"{self.base_url}/media/{comment_id}/comments"
        data = {"text": reply_text} if not self.use_graph_api else {"message": reply_text}
        params = {'access_token': self.api_key} if self.use_graph_api else None
        try:
            response = self.session.post(url, data=data, params=params)
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Reply posted to comment ID {comment_id}: {reply_text}")
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to reply to comment ID {comment_id}: {e}")
            return {"status": "failed", "reason": str(e)}
