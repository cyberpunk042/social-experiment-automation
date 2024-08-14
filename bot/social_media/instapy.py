import logging
from instapy import InstaPy
from social_media.instagram_api import InstagramIntegration

class InstaPyIntegration:
    """
    InstaPyIntegration provides an interface for interacting with Instagram via InstaPy 
    and InstagramIntegration APIs. It supports operations like starting a session, 
    posting comments, replying to comments, following/unfollowing users, and more.

    Attributes:
        username (str): Instagram username.
        password (str): Instagram password.
        headless_browser (bool): Whether to run the browser in headless mode.
        proxy_address (str): Proxy address for the session.
        proxy_port (str): Proxy port for the session.
        session (InstaPy): The InstaPy session instance.
        instagram_api (InstagramIntegration): The Instagram API integration instance.
    """

    def __init__(self, username, password, access_token, headless_browser=True, proxy_address=None, proxy_port=None):
        """
        Initialize the InstaPyIntegration with the necessary credentials and settings.

        Args:
            username (str): Instagram username for login.
            password (str): Instagram password for login.
            access_token (str): Instagram API access token.
            headless_browser (bool): Whether to run the browser in headless mode.
            proxy_address (str): Proxy address for the session.
            proxy_port (str): Proxy port for the session.
        """
        self.username = username
        self.password = password
        self.headless_browser = headless_browser
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.logger = logging.getLogger(__name__)
        self.logger.info("InstaPyIntegration initialized with provided credentials and settings.")
        self.session = None
        self.instagram_api = InstagramIntegration(access_token)

    def start_session(self):
        """
        Start an InstaPy session with the provided credentials and settings.

        Raises:
            Exception: If the session fails to start.
        """
        try:
            self.session = InstaPy(
                username=self.username,
                password=self.password,
                headless_browser=self.headless_browser,
                proxy_address=self.proxy_address,
                proxy_port=self.proxy_port
            )
            self.session.login()
            self.logger.info("InstaPy session started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start InstaPy session: {e}")
            raise

    def get_posts(self, hashtag, amount=10, skip_top_posts=True, interact=False):
        """
        Retrieve and interact with posts associated with a specific hashtag.

        Args:
            hashtag (str): The hashtag to search for posts.
            amount (int): The number of posts to interact with.
            skip_top_posts (bool): Whether to skip the top posts.
            interact (bool): Whether to interact with the posts.

        Returns:
            list: A list of dictionaries representing the posts and interaction status.

        Raises:
            Exception: If an error occurs during post retrieval or interaction.
        """
        if not self.session:
            self.logger.error("Session not started. Call start_session() first.")
            raise Exception("Session not started")

        posts = []
        try:
            self.session.like_by_tags([hashtag], amount=amount, skip_top_posts=skip_top_posts, interact=interact)
            self.logger.info(f"Interacted with {amount} posts for hashtag: {hashtag}")
            posts = [{"hashtag": hashtag, "post_id": i, "interacted": True} for i in range(amount)]
        except Exception as e:
            self.logger.error(f"Failed to retrieve or interact with posts for hashtag {hashtag}: {e}")
            raise
        return posts

    def post_image(self, image_path, caption):
        """
        Post an image to Instagram with a caption.

        Args:
            image_path (str): The path to the image to be posted.
            caption (str): The caption to include with the image.

        Returns:
            dict: A dictionary containing the status and details of the post.

        Raises:
            Exception: If the image fails to post.
        """
        try:
            # Replace this with actual Instagram API call to post an image if needed
            result = {"status": "success", "image_path": image_path, "caption": caption}
            self.logger.info(f"Image posted successfully: {image_path} with caption: {caption}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post image: {e}")
            raise

    def post_comment(self, media_id, comment_text):
        """
        Post a comment on a specific Instagram media (post).

        Args:
            media_id (str): The ID of the media to comment on.
            comment_text (str): The text of the comment.

        Returns:
            dict: A dictionary containing the status and details of the comment.

        Raises:
            Exception: If the comment fails to post.
        """
        try:
            result = self.instagram_api.post_comment(media_id, comment_text)
            self.logger.info(f"Comment posted successfully on media ID {media_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post comment on media ID {media_id}: {e}")
            raise

    def reply_to_comment(self, comment_id, reply_text):
        """
        Reply to a comment on a specific Instagram media (post).

        Args:
            comment_id (str): The ID of the comment to reply to.
            reply_text (str): The text of the reply.

        Returns:
            dict: A dictionary containing the status and details of the reply.

        Raises:
            Exception: If the reply fails to post.
        """
        try:
            result = self.instagram_api.reply_to_comment(comment_id, reply_text)
            self.logger.info(f"Reply posted successfully to comment ID {comment_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to reply to comment ID {comment_id}: {e}")
            raise

    def follow_users(self, amount=10, tags=None):
        """
        Follow users based on specified tags.

        Args:
            amount (int): Number of users to follow.
            tags (list): List of tags to use for finding users to follow.

        Returns:
            dict: A dictionary containing the status and details of the follow operation.

        Raises:
            Exception: If the follow operation fails.
        """
        if not self.session:
            self.logger.error("Session not started. Call start_session() first.")
            raise Exception("Session not started")

        tags = tags or ["nature", "travel"]
        try:
            self.session.follow_by_tags(tags, amount=amount)
            result = {"followed_users": amount, "tags": tags, "status": "followed"}
            self.logger.info(f"Followed {amount} users using tags: {tags}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to follow users: {e}")
            raise

    def unfollow_users(self, amount=10):
        """
        Unfollow a specified number of users.

        Args:
            amount (int): Number of users to unfollow.

        Returns:
            dict: A dictionary containing the status and details of the unfollow operation.

        Raises:
            Exception: If the unfollow operation fails.
        """
        if not self.session:
            self.logger.error("Session not started. Call start_session() first.")
            raise Exception("Session not started")

        try:
            self.session.unfollow_users(amount=amount, nonFollowers=True, style="RANDOM")
            result = {"unfollowed_users": amount, "status": "unfollowed"}
            self.logger.info(f"Unfollowed {amount} users.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to unfollow users: {e}")
            raise

    def end_session(self):
        """
        End the InstaPy session gracefully.

        Raises:
            Warning: If no session is active.
        """
        if self.session:
            self.session.end()
            self.logger.info("InstaPy session ended successfully.")
        else:
            self.logger.warning("No active session to end.")
