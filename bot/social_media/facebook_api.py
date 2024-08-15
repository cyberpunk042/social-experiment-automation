import requests
import logging
from social_media.social_media_base import SocialMediaIntegration

class FacebookIntegration(SocialMediaIntegration):
    """
    FacebookIntegration handles interaction with the Facebook Graph API,
    allowing operations such as posting to pages, retrieving posts, posting comments, and replying to comments.
    """

    def __init__(self, config_manager):
        """
        Initialize the FacebookIntegration with API credentials and settings.

        :param config_manager: An instance of ConfigManager to retrieve configuration settings.
        """
        self.access_token = config_manager.get("facebook_access_token")
        self.page_id = config_manager.get("facebook_page_id")
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        })
        self.base_url = "https://graph.facebook.com/v12.0/"
        self.logger = logging.getLogger(__name__)
        self.logger.info("FacebookIntegration initialized with provided API credentials.")

    def get_posts(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve posts associated with a specific hashtag from the Facebook page.

        :param hashtag: The hashtag to search for posts.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of posts associated with the hashtag.
        """
        url = f"{self.base_url}{self.page_id}/feed"
        params = {'access_token': self.access_token, 'q': f"#{hashtag}"}
        self.logger.info(f"Fetching posts for hashtag: #{hashtag}")

        attempt = 0
        while attempt < retries:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                posts = response.json().get('data', [])
                self.logger.info(f"Retrieved {len(posts)} posts for hashtag: #{hashtag}")
                return posts
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:
                    self.logger.warning(f"Rate limit exceeded. Retrying after delay. Attempt {attempt + 1}")
                    time.sleep(2 ** attempt * backoff_factor)
                else:
                    self.logger.error(f"Error fetching posts for hashtag #{hashtag}: {e}")
                    time.sleep(2 ** attempt * backoff_factor)
            except Exception as e:
                self.logger.error(f"Unexpected error during post retrieval for hashtag #{hashtag}: {e}")
                time.sleep(2 ** attempt * backoff_factor)
            attempt += 1
        self.logger.error(f"Failed to retrieve posts for hashtag #{hashtag} after {retries} attempts.")
        return []

    def post_image(self, image_url, caption):
        """
        Post an image with a caption to the Facebook page.

        :param image_url: The URL of the image to include in the post.
        :param caption: The text of the post.
        :return: The result of the post operation.
        """
        url = f"{self.base_url}{self.page_id}/photos"
        data = {'url': image_url, 'caption': caption, 'access_token': self.access_token}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            post_id = response.json().get('id')
            post_url = f"https://www.facebook.com/{self.page_id}/posts/{post_id}"
            self.logger.info(f"Image posted successfully: {post_url}")
            return {"status": "success", "url": post_url}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post image on Facebook: {e}")
            return {"status": "error", "message": str(e)}

    def post_comment(self, media_id, comment_text):
        """
        Post a comment on a specific Facebook post.

        :param media_id: The ID of the post to comment on.
        :param comment_text: The text of the comment to post.
        :return: The result of the comment operation.
        """
        url = f"{self.base_url}{media_id}/comments"
        data = {'message': comment_text, 'access_token': self.access_token}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            comment_id = response.json().get('id')
            self.logger.info(f"Comment posted on post ID {media_id}.")
            return {"status": "success", "comment_id": comment_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to post comment on post ID {media_id}: {e}")
            return {"status": "error", "message": str(e)}

    def reply_to_comment(self, comment_id, reply_text):
        """
        Reply to a specific comment on a Facebook post.

        :param comment_id: The ID of the comment to reply to.
        :param reply_text: The text of the reply.
        :return: The result of the reply operation.
        """
        url = f"{self.base_url}{comment_id}/comments"
        data = {'message': reply_text, 'access_token': self.access_token}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            reply_id = response.json().get('id')
            self.logger.info(f"Reply posted to comment ID {comment_id}.")
            return {"status": "success", "reply_id": reply_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to reply to comment ID {comment_id}: {e}")
            return {"status": "error", "message": str(e)}

    def follow_users(self, amount, tags):
        """
        Follow users based on specified tags.

        :param amount: Number of users to follow.
        :param tags: List of tags to use for finding users to follow.
        :return: The result of the follow operation.

        Raises:
            NotImplementedError: If Facebook API does not support this operation.
        """
        raise NotImplementedError("Facebook API does not support following users via this integration.")

    def unfollow_users(self, amount):
        """
        Unfollow a specified number of users on Facebook.

        :param amount: Number of users to unfollow.
        :return: The result of the unfollow operation.

        Raises:
            NotImplementedError: If Facebook API does not support this operation.
        """
        raise NotImplementedError("Facebook API does not support unfollowing users via this integration.")

    def fetch_post_content(self, media_id):
        """
        Fetch the content of a specific Facebook post using its media_id.

        Args:
            media_id (str): The ID of the media post to fetch the content for.

        Returns:
            dict: The content of the post.
        """
        try:
            url = f"{self.base_url}{media_id}"
            params = {'access_token': self.access_token}

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            post_content = {
                'text': data.get('message', ''),
                'media_url': data.get('full_picture', '')
            }

            self.logger.info(f"Fetched content for post {media_id} on Facebook.")
            return post_content
        except Exception as e:
            self.logger.error(f"Failed to fetch post content for {media_id} on Facebook: {e}", exc_info=True)
            raise

    def fetch_comments_list(self, media_id):
        """
        Fetch the list of comments for a specific post using its media_id.

        Args:
            media_id (str): The ID of the media post to fetch comments for.

        Returns:
            list: A list of comments on the post.
        """
        try:
            url = f"{self.base_url}{media_id}/comments"
            params = {'access_token': self.access_token}

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            comments_list = [{'id': comment.get('id'), 'text': comment.get('message')} for comment in data.get('data', [])]

            self.logger.info(f"Fetched comments for post {media_id} on Facebook.")
            return comments_list
        except Exception as e:
            self.logger.error(f"Failed to fetch comments for {media_id} on Facebook: {e}", exc_info=True)
            raise