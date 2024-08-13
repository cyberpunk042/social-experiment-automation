import logging
import asyncio
import random
from bot.openai_client import OpenAIClient
from bot.user_preferences import UserPreferences
from bot.social_media.instagram_api import InstagramIntegration
from bot.social_media.twitter import TwitterIntegration
from bot.config_manager import ConfigManager
from bot.response_generator import ResponseGenerator

class Bot:
    def __init__(self, interactive=False):
        """
        Initialize the Bot class, setting up integrations and services.

        This constructor sets up the necessary integrations and services required
        for the bot to function, including the option for interactive mode.
        """
        self.config = ConfigManager().load_config()
        self.openai_client = OpenAIClient(self.config["openai_api_key"])
        self.user_preferences = UserPreferences()
        self.instagram = InstagramIntegration(self.config["instagram"])
        self.twitter = TwitterIntegration(self.config["twitter"])
        self.response_generator = ResponseGenerator(self.openai_client)
        self.interactive = interactive  # Set the interactive mode

    def confirm_action(self, action_description):
        if not self.interactive:
            return True
        confirmation = input(f"Do you want to proceed with the following action: {action_description}? (yes/no): ")
        return confirmation.lower() in ['yes', 'y']

    async def create_post(self, platform):
        """
        Create a new post on the specified social media platform.

        Args:
            platform (str): The social media platform to post on.
        """
        if platform == 'twitter':
            if self.confirm_action("creating a post on Twitter"):
                await self.twitter.create_post("This is a test post.")
        elif platform == 'instagram':
            if self.confirm_action("creating a post on Instagram"):
                await self.instagram.create_post("This is a test post.")

    async def reply_to_comments(self, platform):
        """
        Reply to comments on the specified social media platform.

        Args:
            platform (str): The social media platform to reply on.
        """
        if platform == 'twitter':
            if self.confirm_action("replying to comments on Twitter"):
                await self.twitter.reply_to_comments()
        elif platform == 'instagram':
            if self.confirm_action("replying to comments on Instagram"):
                await self.instagram.reply_to_comments()

    async def like_posts(self, platform):
        """
        Like posts on the specified social media platform.

        Args:
            platform (str): The social media platform where posts will be liked.
        """
        if platform == 'twitter':
            if self.confirm_action("liking posts on Twitter"):
                await self.twitter.like_posts()
        elif platform == 'instagram':
            if self.confirm_action("liking posts on Instagram"):
                await self.instagram.like_posts()

    async def follow_users(self, platform):
        """
        Follow users on the specified social media platform.

        Args:
            platform (str): The social media platform where users will be followed.
        """
        if platform == 'twitter':
            if self.confirm_action("following users on Twitter"):
                await self.twitter.follow_users()
        elif platform == 'instagram':
            if self.confirm_action("following users on Instagram"):
                await self.instagram.follow_users()

    async def unfollow_users(self, platform):
        """
        Unfollow users on the specified social media platform.

        Args:
            platform (str): The social media platform where users will be unfollowed.
        """
        if platform == 'twitter':
            if self.confirm_action("unfollowing users on Twitter"):
                await self.twitter.unfollow_users()
        elif platform == 'instagram':
            if self.confirm_action("unfollowing users on Instagram"):
                await self.instagram.unfollow_users()

    async def _generate_content_with_retries(self, max_retries=3):
        """
        Generate content using the response generator with retry logic.

        Args:
            max_retries (int): The maximum number of retries allowed in case of failure.

        Returns:
            str: The generated content or an error message if all retries fail.
        """
        for attempt in range(max_retries):
            try:
                content = await self.response_generator.generate_response()
                return content
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
        return "Failed to generate content after multiple attempts."

    async def _post_content_with_retries(self, platform, content, max_retries=3):
        """
        Post content to a social media platform with retry logic.

        Args:
            platform (str): The social media platform where content will be posted.
            content (str): The content to post.
            max_retries (int): The maximum number of retries allowed in case of failure.
        """
        for attempt in range(max_retries):
            try:
                if platform == 'twitter':
                    if self.confirm_action(f"posting content to Twitter: {content}"):
                        await self.twitter.create_post(content)
                        return
                elif platform == 'instagram':
                    if self.confirm_action(f"posting content to Instagram: {content}"):
                        await self.instagram.create_post(content)
                        return
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
        logging.error("Failed to post content after multiple attempts.")

    async def run(self, platform, action):
        """
        Execute the bot's action with proper content generation and posting.

        Args:
            platform (str): The social media platform to interact with.
            action (str): The action to perform (e.g., 'create_post').
        """
        if action == 'create_post':
            content = await self._generate_content_with_retries()
            await self._post_content_with_retries(platform, content)
        elif action == 'reply_to_comments':
            await self.reply_to_comments(platform)
        elif action == 'like_posts':
            await self.like_posts(platform)
        elif action == 'follow_users':
            await self.follow_users(platform)
        elif action == 'unfollow_users':
            await self.unfollow_users(platform)