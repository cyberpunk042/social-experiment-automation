import logging
from bot.social_media.instagram_integration import InstagramIntegration
from bot.response_generator import ResponseGenerator  # Assuming this is where ResponseGenerator is implemented

class InstagramBot:
    """
    InstagramBot provides a high-level interface for interacting with Instagram using the
    InstagramIntegration API and ResponseGenerator. It supports operations such as generating and
    posting images, posting comments, replying to comments, following users, and more.

    Attributes:
        instagram_api (InstagramIntegration): The Instagram API integration instance.
        response_generator (ResponseGenerator): Instance for generating responses and content.
        interactive (bool): Determines if actions require confirmation.
    """

    def __init__(self, config_manager, interactive=False):
        """
        Initialize the InstagramBot with the configuration manager and setup API integrations.

        Args:
            config_manager (ConfigManager): The configuration manager for retrieving settings.
            interactive (bool): If True, actions will require user confirmation.
        """
        self.logger = logging.getLogger(__name__)
        self.instagram_api = InstagramIntegration(config_manager)
        self.response_generator = ResponseGenerator()
        self.interactive = interactive
        self.logger.info("InstagramBot initialized.")

    def get_posts_by_hashtag(self, hashtag, retries=3, backoff_factor=0.3):
        """
        Retrieve posts associated with a specific hashtag.

        Args:
            hashtag (str): The hashtag to search for posts.
            retries (int): Number of retries in case of failures.
            backoff_factor (float): Factor for increasing delay between retries.

        Returns:
            list: A list of posts associated with the hashtag.

        Raises:
            Exception: If there is an error in retrieving posts.
        """
        try:
            posts = self.instagram_api.get_posts(hashtag, retries, backoff_factor)
            self.logger.info(f"Retrieved posts for hashtag: {hashtag}")
            return posts
        except Exception as e:
            self.logger.error(f"Failed to retrieve posts for hashtag {hashtag}: {e}")
            raise

    def create_post(self, caption=None):
        """
        Generate an image based on the provided or generated caption and create a new post on Instagram.

        Args:
            caption (str): Optional caption for the post. If not provided, it will be generated.

        Returns:
            dict: The result of the post operation.

        Raises:
            Exception: If there is an error in creating the post.
        """
        try:
            if not caption:
                caption = self.response_generator.generate_caption()

            # Generate the image based on the caption
            image_path = self.response_generator.generate_image(caption)

            if self.interactive:
                action_description = f"Creating a new post with generated image {image_path} and caption '{caption}'."
                if not self.confirm_action(action_description):
                    self.logger.info("Post creation canceled by user.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            # Post the image with the generated caption
            result = self.instagram_api.post_image(image_path, caption)
            self.logger.info(f"Created a new post with caption: {caption}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create post: {e}")
            raise

    def post_comment_on_post(self, media_id, context=None):
        """
        Post a comment on a specific Instagram post, generating the comment using context.

        Args:
            media_id (str): The ID of the media (post) to comment on.
            context (str): Context to generate the comment. If not provided, it will be auto-generated.

        Returns:
            dict: The result of the comment operation.

        Raises:
            Exception: If there is an error in posting the comment.
        """
        try:
            comment_text = self.response_generator.generate_comment(context)
            
            if self.interactive:
                action_description = f"Posting comment on media ID {media_id}: '{comment_text}'."
                if not self.confirm_action(action_description):
                    self.logger.info("Comment posting canceled by user.")
                    return {"status": "canceled", "reason": "User canceled the action."}
            
            result = self.instagram_api.post_comment(media_id, comment_text)
            self.logger.info(f"Posted comment on media ID {media_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post comment on media ID {media_id}: {e}")
            raise

    def reply_to_comment_on_post(self, comment_id, context=None):
        """
        Reply to a comment on a specific Instagram post, generating the reply using context.

        Args:
            comment_id (str): The ID of the comment to reply to.
            context (str): Context to generate the reply. If not provided, it will be auto-generated.

        Returns:
            dict: The result of the reply operation.

        Raises:
            Exception: If there is an error in replying to the comment.
        """
        try:
            reply_text = self.response_generator.generate_reply(context)
            
            if self.interactive:
                action_description = f"Replying to comment ID {comment_id} with: '{reply_text}'."
                if not self.confirm_action(action_description):
                    self.logger.info("Reply action canceled by user.")
                    return {"status": "canceled", "reason": "User canceled the action."}
            
            result = self.instagram_api.reply_to_comment(comment_id, reply_text)
            self.logger.info(f"Replied to comment ID {comment_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to reply to comment ID {comment_id}: {e}")
            raise

    def follow_users_by_tags(self, tags, amount=10):
        """
        Follow users based on specified tags.

        Args:
            tags (list): List of tags to use for finding users to follow.
            amount (int): Number of users to follow.

        Returns:
            dict: The result of the follow operation.

        Raises:
            Exception: If there is an error in following users.
        """
        try:
            if self.interactive:
                action_description = f"Following {amount} users based on tags: {tags}."
                if not self.confirm_action(action_description):
                    self.logger.info("Follow action canceled by user.")
                    return {"status": "canceled", "reason": "User canceled the action."}
            
            result = self.instagram_api.follow_users(amount=amount, tags=tags)
            self.logger.info(f"Followed users by tags: {tags}.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to follow users by tags {tags}: {e}")
            raise

    def unfollow_users(self, amount=10):
        """
        Unfollow a specified number of users.

        Args:
            amount (int): Number of users to unfollow.

        Returns:
            dict: The result of the unfollow operation.

        Raises:
            Exception: If there is an error in unfollowing users.
        """
        try:
            if self.interactive:
                action_description = f"Unfollowing {amount} users."
                if not self.confirm_action(action_description):
                    self.logger.info("Unfollow action canceled by user.")
                    return {"status": "canceled", "reason": "User canceled the action."}
            
            result = self.instagram_api.unfollow_users(amount=amount)
            self.logger.info(f"Unfollowed {amount} users.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to unfollow users: {e}")
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
