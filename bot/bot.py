import logging
from bot.social_media.instagram_api import InstagramIntegration
from bot.social_media.twitter import TwitterIntegration
from bot.response_generator import ResponseGenerator
from bot.config_manager import ConfigManager

class SocialBot:
    """
    SocialBot provides a high-level interface for interacting with multiple social media platforms.
    It supports operations such as generating and posting images, posting comments, replying to comments,
    and managing followers across different platforms like Instagram and Twitter.
    """

    def __init__(self, config_manager: ConfigManager, interactive=False):
        """
        Initialize the SocialBot with configuration and set up platform integrations.

        Args:
            config_manager (ConfigManager): The configuration manager for retrieving settings.
            interactive (bool): If True, actions will require user confirmation.
        """
        self.logger = logging.getLogger(__name__)
        self.interactive = interactive
        self.platforms = {
            "instagram": InstagramIntegration(config_manager),
            "twitter": TwitterIntegration(config_manager)
        }
        self.response_generator = ResponseGenerator(config_manager)
        self.logger.info("SocialBot initialized with integrations for Instagram and Twitter.")

    def post_image(self, platform, caption=None):
        """
        Generate an image based on the provided or generated caption and create a new post on the specified platform.

        Args:
            platform (str): The platform to post the image on (e.g., 'instagram', 'twitter').
            caption (str): Optional caption for the post. If not provided, it will be generated.

        Returns:
            dict: The result of the post operation.

        Raises:
            Exception: If there is an error in creating the post or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            if not caption:
                caption = self.response_generator.generate_caption()

            # Generate the image based on the caption
            image_url = self.response_generator.generate_image(caption)

            if self.interactive:
                action_description = f"Creating a new post on {platform} with generated image and caption '{caption}'."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Post creation canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            # Post the image with the generated caption
            result = self.platforms[platform].post_image(image_url, caption)
            self.logger.info(f"Created a new post on {platform} with caption: {caption}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create post on {platform}: {e}")
            raise

    def post_comment(self, platform, media_id, context=None):
        """
        Post a comment on a specific media item on the specified platform.

        Args:
            platform (str): The platform to post the comment on (e.g., 'instagram', 'twitter').
            media_id (str): The ID of the media (post) to comment on.
            context (str): Context to generate the comment. If not provided, it will be auto-generated.

        Returns:
            dict: The result of the comment operation.

        Raises:
            Exception: If there is an error in posting the comment or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            comment_text = self.response_generator.generate_comment(context)

            if self.interactive:
                action_description = f"Posting comment on {platform} media ID {media_id}: '{comment_text}'."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Comment posting canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].post_comment(media_id, comment_text)
            self.logger.info(f"Posted comment on {platform} media ID {media_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post comment on {platform} media ID {media_id}: {e}")
            raise

    def reply_to_comment(self, platform, comment_id, context=None):
        """
        Reply to a comment on a specific media item on the specified platform.

        Args:
            platform (str): The platform to reply to the comment on (e.g., 'instagram', 'twitter').
            comment_id (str): The ID of the comment to reply to.
            context (str): Context to generate the reply. If not provided, it will be auto-generated.

        Returns:
            dict: The result of the reply operation.

        Raises:
            Exception: If there is an error in replying to the comment or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            reply_text = self.response_generator.generate_reply(context)

            if self.interactive:
                action_description = f"Replying to comment on {platform} comment ID {comment_id} with: '{reply_text}'."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Reply action canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].reply_to_comment(comment_id, reply_text)
            self.logger.info(f"Replied to comment on {platform} comment ID {comment_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to reply to comment on {platform} comment ID {comment_id}: {e}")
            raise

    def follow_users(self, platform, tags, amount=10):
        """
        Follow users based on specified tags on the specified platform.

        Args:
            platform (str): The platform to follow users on (e.g., 'instagram', 'twitter').
            tags (list): List of tags to use for finding users to follow.
            amount (int): Number of users to follow.

        Returns:
            dict: The result of the follow operation.

        Raises:
            Exception: If there is an error in following users or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            if self.interactive:
                action_description = f"Following {amount} users on {platform} based on tags: {tags}."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Follow action canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].follow_users(amount=amount, tags=tags)
            self.logger.info(f"Followed users on {platform} by tags: {tags}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to follow users on {platform} by tags {tags}: {e}")
            raise

    def unfollow_users(self, platform, amount=10):
        """
        Unfollow a specified number of users on the specified platform.

        Args:
            platform (str): The platform to unfollow users on (e.g., 'instagram', 'twitter').
            amount (int): Number of users to unfollow.

        Returns:
            dict: The result of the unfollow operation.

        Raises:
            Exception: If there is an error in unfollowing users or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            if self.interactive:
                action_description = f"Unfollowing {amount} users on {platform}."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Unfollow action canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].unfollow_users(amount=amount)
            self.logger.info(f"Unfollowed {amount} users on {platform}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to unfollow users on {platform}: {e}")
            raise

    def confirm_action(self, action_description):
        """
        Confirm an action before proceeding.

        Args:
            action_description (str): Description of the action to confirm.

        Returns:
            bool: True if the action is confirmed, False otherwise.
        """
        try:
            confirmation = input(f"Please confirm the following action: {action_description} (yes/no): ")
            if confirmation.lower() in ['yes', 'y']:
                self.logger.info(f"Action confirmed: {action_description}")
                return True
            else:
                self.logger.info(f"Action not confirmed: {action_description}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to confirm action {action_description}: {e}")
            raise
