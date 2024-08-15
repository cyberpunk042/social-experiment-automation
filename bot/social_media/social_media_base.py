from abc import ABC, abstractmethod

class SocialMediaIntegration(ABC):
    """
    Abstract base class for social media integrations.
    Defines the common interface for all social media platforms.
    """

    @abstractmethod
    def get_posts(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve posts associated with a specific hashtag.
        This method should be implemented by each platform-specific integration.

        :param hashtag: The hashtag to search for posts.
        :param retries: Number of retries in case of failures.
        :param backoff_factor: Factor for increasing delay between retries.
        :return: A list of posts associated with the hashtag.
        """
        pass

    @abstractmethod
    def post_image(self, image_url, caption):
        """
        Post an image with a caption to the social media platform.
        This method should be implemented by each platform-specific integration.

        :param image_url: The URL of the image to post.
        :param caption: The caption to accompany the image.
        :return: The result of the post operation, including the post URL.
        """
        pass

    @abstractmethod
    def post_comment(self, media_id, comment_text):
        """
        Post a comment on a specific media item.
        This method should be implemented by each platform-specific integration.

        :param media_id: The ID of the media (post) to comment on.
        :param comment_text: The text of the comment to post.
        :return: The result of the comment operation.
        """
        pass

    @abstractmethod
    def reply_to_comment(self, comment_id, reply_text):
        """
        Reply to a comment on a specific media item.
        This method should be implemented by each platform-specific integration.

        :param comment_id: The ID of the comment to reply to.
        :param reply_text: The text of the reply to post.
        :return: The result of the reply operation.
        """
        pass

    @abstractmethod
    def follow_users(self, amount, tags):
        """
        Follow users based on specified tags.
        This method should be implemented by each platform-specific integration.

        :param amount: Number of users to follow.
        :param tags: List of tags to use for finding users to follow.
        :return: The result of the follow operation.
        """
        pass

    @abstractmethod
    def unfollow_users(self, amount):
        """
        Unfollow a specified number of users.
        This method should be implemented by each platform-specific integration.

        :param amount: Number of users to unfollow.
        :return: The result of the unfollow operation.
        """
        pass

    @abstractmethod
    def fetch_post_content(self, media_id):
        """
        Fetch the content of a specific post using its media_id.

        Args:
            media_id (str): The ID of the media post to fetch the content for.

        Returns:
            dict: The content of the post.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    def fetch_comments_list(self, media_id):
        """
        Fetch the list of comments for a specific post using its media_id.

        Args:
            media_id (str): The ID of the media post to fetch comments for.

        Returns:
            list: A list of comments on the post.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")