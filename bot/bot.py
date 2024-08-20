import logging
from openai_client import OpenAIClient
from user_preferences import UserPreferences
from database_client import DatabaseClient
from social_media.instagram_api import InstagramIntegration
from social_media.twitter import TwitterIntegration
from social_media.facebook_api import FacebookIntegration
from response_generator import ResponseGenerator
from config_manager import ConfigManager

class SocialBot:
    """
    SocialBot provides a high-level interface for interacting with multiple social media platforms.
    It supports operations such as generating and posting images, posting comments, replying to comments,
    and managing followers across different platforms like Instagram and Twitter.
    """

    def __init__(self, config_manager: ConfigManager, openai_client: OpenAIClient, database_client: DatabaseClient, user_preferences: UserPreferences, interactive=False):
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
            "twitter": TwitterIntegration(config_manager),
            "facebook": FacebookIntegration(config_manager)
        }
        self.database_client = database_client
        self.user_preferences = user_preferences
        self.response_generator = ResponseGenerator(openai_client, database_client, user_preferences)
        self.logger.info("SocialBot initialized with integrations for Instagram and Twitter.")

    def post_image(self, platform, caption_text=None, schedule_time=None):
        """
        Generate an image based on the provided or generated caption and create a new post on the specified platform.

        Args:
            platform (str): The platform to post the image on (e.g., 'instagram', 'twitter').
            caption_text (str): Optional caption text for the post. If not provided, it will be generated.
            schedule_time (int): Optional Unix timestamp representing when to schedule the post. Default is None.

        Returns:
            dict: The result of the post operation.

        Raises:
            Exception: If there is an error in creating the post or the platform is unsupported.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            if not caption_text:
                # Retrieve captions from the database
                captions = self.database_client.get_data("captions")
                generated_captions = self.database_client.get_data("generated_captions")
                if not captions:
                    self.logger.error("No captions found in the database.")
                    raise Exception("No captions found in the database.")
                self.logger.info(f"{len(captions)} captions found in the database.")

                # Select a base caption based on user preferences
                try:
                    caption = self.user_preferences.select_preferred_caption(captions, generated_captions)
                    caption_text = caption.get('caption_text')
                except ValueError as e:
                    self.logger.error(f"No suitable captions found: {e}")
                    raise Exception("Error retrieving or personalizing caption: No suitable captions found.")
            
            generated_caption = self.response_generator.generate_caption(caption_text)
            
            # Generate the image based on the caption text
            image_url = self.response_generator.generate_image(generated_caption)

            if caption.get("id"):
                # Save the generated caption to the database and link it to the existing caption record
                self.database_client.add_generated_caption(generated_caption, caption_text, image_url, caption.get("id"))

            if self.interactive:
                action_description = f"Creating a new post on {platform} with generated image and caption '{generated_caption}'."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Post creation canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            # Post the image with the generated caption
            if schedule_time:
                result = self.platforms[platform].post_image(image_url, generated_caption, schedule_time=schedule_time)
                self.logger.info(f"Scheduled a new post on {platform} with caption: {generated_caption} at {time.ctime(schedule_time)}")
            else:
                result = self.platforms[platform].post_image(image_url, generated_caption)
                self.logger.info(f"Created a new post on {platform} with caption: {generated_caption}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to create post on {platform}: {e}")
            raise


    def post_comment(self, platform, media_id, comment_text=None):
        """
        Post a comment on the specified post on a given platform.

        Args:
            platform (str): The platform to post the comment on (e.g., 'instagram', 'twitter').
            media_id (str): The ID of the post to comment on.
            comment_text (str, optional): The text of the comment. If None, it will be generated.

        Returns:
            dict: The result of the comment operation.

        Raises:
            ValueError: If the specified platform is not supported.
            Exception: If there is an error in posting the comment.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            # Fetch the post content
            post_content = self.platforms[platform].fetch_post_content(media_id)
            
            # Ensure we have a well-defined context for generating comments
            context = {
                'post_text': post_content.get('text', ''),
                'media_url': post_content.get('media_url', '')
            }
            
            # Log the context being used
            self.logger.info(f"Using context for comment generation: {context}")

            # Generate a personalized comment if not provided
            if not comment_text:
                comment_text = self.response_generator.generate_personalized_comment(context, platform)
                self.logger.debug(f"Generated comment: {comment_text}")

            if self.interactive:
                action_description = f"Posting comment on {platform} post {media_id} with text: {comment_text}."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Post comment action canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].post_comment(media_id=media_id, comment_text=comment_text)
            self.logger.info(f"Posted comment on {platform} post {media_id} with text: {comment_text}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post comment on {platform} post {media_id}: {e}", exc_info=True)
            raise

    def reply_to_comments(self, platform, media_id, reply_text=None):
        """
        Reply to comments on the specified post on a given platform.

        Args:
            platform (str): The platform to reply to the comments on (e.g., 'instagram', 'twitter').
            media_id (str): The ID of the post with the comments.
            reply_text (str, optional): The text of the reply. If None, it will be generated.

        Returns:
            dict: The result of the reply operation.

        Raises:
            ValueError: If the specified platform is not supported.
            Exception: If there is an error in replying to the comments.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")

        try:
            # Fetch list of comments
            comments_list = self.platforms[platform].fetch_comments_list(media_id)
            
            # Fetch the post content to include it in the context
            post_content = self.platforms[platform].fetch_post_content(media_id) 

            for comment in comments_list:
                comment_id = comment.get('id')
                comment_text = comment.get('text')
                
                # Ensure we have a well-defined context for generating replies
                context = {
                    'post_text': post_content.get('text', ''),
                    'comment_text': comment_text,
                    'media_url': post_content.get('media_url', '')
                }
                
                # Log the context being used
                self.logger.info(f"Using context for reply generation: {context}")

                # Generate a personalized reply if not provided
                if not reply_text:
                    reply_text = self.response_generator.generate_personalized_reply(context, platform)
                    self.logger.debug(f"Generated reply: {reply_text}")

                if self.interactive:
                    action_description = f"Replying to comment {comment_id} on {platform} post {media_id} with text: {reply_text}."
                    if not self.confirm_action(action_description):
                        self.logger.info(f"Reply action canceled by user on {platform}.")
                        continue

                result = self.platforms[platform].reply_to_comment(media_id=media_id, comment_id=comment_id, reply_text=reply_text)
                self.logger.info(f"Replied to comment {comment_id} on {platform} post {media_id} with text: {reply_text}")
            return {"status": "success"}
        except Exception as e:
            self.logger.error(f"Failed to reply to comments on {platform} post {media_id}: {e}", exc_info=True)
            raise

    def follow_users(self, platform, users):
        """
        Follow users on the specified platform.

        Args:
            platform (str): The platform to follow users on (e.g., 'instagram', 'twitter').
            users (list of str): A list of user IDs to follow.

        Returns:
            dict: The result of the follow operation.

        Raises:
            ValueError: If the specified platform is not supported.
            Exception: If there is an error in following users.
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} is not supported.")
        
        try:
            if self.interactive:
                action_description = f"Following users on {platform}: {', '.join(users)}."
                if not self.confirm_action(action_description):
                    self.logger.info(f"Follow action canceled by user on {platform}.")
                    return {"status": "canceled", "reason": "User canceled the action."}

            result = self.platforms[platform].follow_users(users=users)
            self.logger.info(f"Followed users on {platform}: {', '.join(users)}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to follow users on {platform}: {e}", exc_info=True)
            raise

    def unfollow_users(self, platform, amount):
        """
        Unfollow users on the specified platform.

        Args:
            platform (str): The platform to unfollow users on (e.g., 'instagram', 'twitter').
            amount (int): Number of users to unfollow.

        Returns:
            dict: The result of the unfollow operation.

        Raises:
            ValueError: If the specified platform is not supported.
            Exception: If there is an error in unfollowing users.
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
            self.logger.error(f"Failed to unfollow users on {platform}: {e}", exc_info=True)
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
            self.logger.error(f"Failed to confirm action {action_description}: {e}", exc_info=True)
            raise