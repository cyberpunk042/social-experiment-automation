import requests
import logging
import time
from bot.social_media.social_media_base import SocialMediaIntegration

class InstagramIntegration(SocialMediaIntegration):
    """
    InstagramIntegration handles interaction with both the Instagram Graph API and the Basic Display API,
    allowing operations such as retrieving posts, posting comments, and replying to comments.
    """

    def __init__(self, config_manager, use_graph_api=True):
        """
        Initialize the InstagramIntegration with API credentials and settings.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        :param use_graph_api: Boolean flag to determine whether to use the Graph API or Basic Display API.
        """
        super().__init__()
        self.use_graph_api = use_graph_api
        self.api_key = config_manager.get("instagram_api_key")
        self.access_token = config_manager.get("instagram_access_token") if use_graph_api else None
        self.base_url = "https://graph.instagram.com/" if use_graph_api else "https://api.instagram.com/v1"
        self.session = requests.Session()

        if not use_graph_api:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        else:
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})

        self.logger = logging.getLogger(__name__)
        self.logger.info("InstagramIntegration initialized with provided API key and access token.")

    def get_posts(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve posts associated with a specific hashtag, with retry logic for handling failures.

        :param hashtag: The hashtag to search for posts.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of posts associated with the hashtag.
        """
        if self.use_graph_api:
            hashtag_id = self._get_hashtag_id(hashtag)
            if not hashtag_id:
                return []
            url = f"{self.base_url}{hashtag_id}/recent_media"
            params = {'user_id': self._get_user_id(), 'access_token': self.access_token}
        else:
            url = f"{self.base_url}/tags/{hashtag}/media/recent"
            params = None

        self.logger.info(f"Fetching posts for hashtag: {hashtag}")
        return self._execute_get_request(url, params, retries, backoff_factor)

    def post_image(self, image_url, caption):
        """
        Post an image to Instagram with a caption.

        :param image_url: The URL of the image to post.
        :param caption: The caption to accompany the image.
        :return: The result of the post operation, including the post URL.
        """
        # Image posting is only supported via the Graph API.
        if not self.use_graph_api:
            raise NotImplementedError("Image posting is only supported with the Graph API.")

        try:
            # Upload the image (Step 1)
            upload_url = f"{self.base_url}me/media"
            upload_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.access_token
            }
            upload_response = self.session.post(upload_url, data=upload_data)
            upload_response.raise_for_status()
            media_id = upload_response.json().get('id')

            # Publish the image (Step 2)
            publish_url = f"{self.base_url}me/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': self.access_token
            }
            publish_response = self.session.post(publish_url, data=publish_data)
            publish_response.raise_for_status()

            post_id = publish_response.json().get('id')
            post_url = f"https://www.instagram.com/p/{post_id}/"
            self.logger.info(f"Image posted successfully: {post_url}")
            return {"status": "success", "url": post_url}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post image on Instagram: {e}")
            return {"status": "error", "message": str(e)}

    def post_comment(self, media_id, comment_text):
        """
        Post a comment on a specific Instagram media (post).

        :param media_id: The ID of the media (post) to comment on.
        :param comment_text: The text of the comment to post.
        :return: The result of the comment operation.
        """
        if self.use_graph_api:
            url = f"{self.base_url}{media_id}/comments"
            data = {"message": comment_text, 'access_token': self.access_token}
        else:
            url = f"{self.base_url}/media/{media_id}/comments"
            data = {"text": comment_text}

        self.logger.info(f"Posting comment on media ID: {media_id}")
        return self._execute_post_request(url, data)

    def reply_to_comment(self, comment_id, reply_text):
        """
        Reply to a specific comment on an Instagram media (post).

        :param comment_id: The ID of the comment to reply to.
        :param reply_text: The text of the reply.
        :return: The result of the reply operation.
        """
        if self.use_graph_api:
            url = f"{self.base_url}{comment_id}/replies"
            data = {"message": reply_text, 'access_token': self.access_token}
        else:
            url = f"{self.base_url}/media/{comment_id}/comments"
            data = {"text": reply_text}

        self.logger.info(f"Posting reply to comment ID: {comment_id}")
        return self._execute_post_request(url, data)

    def follow_users(self, amount, tags):
        """
        Follow users on Instagram based on specified tags.

        :param amount: Number of users to follow.
        :param tags: List of tags to use for finding users to follow.
        :return: The result of the follow operation.

        Raises:
            NotImplementedError: If Instagram API does not support this operation.
        """
        # Instagram API has restrictions on automated follows.
        raise NotImplementedError("Instagram API does not support automated follows through this integration.")

    def unfollow_users(self, amount):
        """
        Unfollow users on Instagram.

        :param amount: Number of users to unfollow.
        :return: The result of the unfollow operation.

        Raises:
            NotImplementedError: If Instagram API does not support this operation.
        """
        # Instagram API has restrictions on automated unfollows.
        raise NotImplementedError("Instagram API does not support automated unfollows through this integration.")

    def _get_user_id(self):
        """
        Retrieve the user ID for the authenticated user using the Graph API.
        This method is required for certain Graph API operations.

        :return: The user ID, or None if retrieval fails.
        """
        if not self.use_graph_api:
            raise NotImplementedError("User ID retrieval is only supported with the Graph API.")

        url = f"{self.base_url}me"
        params = {'access_token': self.access_token}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            user_id = response.json().get('id')
            self.logger.info(f"User ID retrieved successfully: {user_id}")
            return user_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve user ID: {e}")
            return None

    def _get_hashtag_id(self, hashtag):
        """
        Retrieve the hashtag ID for a specific hashtag using the Graph API.
        This ID is necessary for fetching media related to a hashtag.

        :param hashtag: The hashtag to search for.
        :return: The hashtag ID, or None if retrieval fails.
        """
        if not self.use_graph_api:
            raise NotImplementedError("Hashtag ID retrieval is only supported with the Graph API.")

        url = f"{self.base_url}ig_hashtag_search"
        params = {'user_id': self._get_user_id(), 'q': hashtag, 'access_token': self.access_token}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            hashtag_id = response.json().get('data')[0].get('id')
            self.logger.info(f"Hashtag ID retrieved successfully for {hashtag}: {hashtag_id}")
            return hashtag_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve hashtag ID for {hashtag}: {e}")
            return None

    def _execute_get_request(self, url, params, retries, backoff_factor):
        """
        Execute a GET request with retry logic.

        :param url: The URL to send the GET request to.
        :param params: The parameters to include in the request.
        :param retries: The number of retries in case of failure.
        :param backoff_factor: The factor for increasing the delay between retries.
        :return: The response data as a dictionary, or an empty list on failure.
        """
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json().get('data', [])
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error during GET request: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during GET request: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to execute GET request after {retries} attempts.")
        return []

    def _execute_post_request(self, url, data, retries=3, backoff_factor=0.3):
        """
        Execute a POST request with retry logic.

        :param url: The URL to send the POST request to.
        :param data: The data to include in the request.
        :param retries: The number of retries in case of failure.
        :param backoff_factor: The factor for increasing the delay between retries.
        :return: The response data as a dictionary, or None on failure.
        """
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.post(url, data=data)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:  # Rate limit error
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error during POST request: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during POST request: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to execute POST request after {retries} attempts.")
        return None
