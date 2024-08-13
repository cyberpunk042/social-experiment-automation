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
    def __init__(self):
        """
        Initialize the Bot class, setting up integrations and services.

        This constructor initializes the configuration manager, OpenAI client, user preferences,
        response generator, and platform-specific integrations for Instagram and Twitter.
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.openai_client = OpenAIClient(self.config_manager)
        self.user_preferences = UserPreferences(self.config_manager)
        self.response_generator = ResponseGenerator(self.openai_client, self.user_preferences)
        self.platforms = {
            'instagram': InstagramIntegration(self.config_manager),
            'twitter': TwitterIntegration(self.config_manager)
        }

    async def generate_and_post(self, platform, post_content):
        """
        Generate content and post it to the specified social media platform.

        :param platform: The name of the platform (e.g., 'instagram', 'twitter').
        :param post_content: The initial content or prompt for generating the post.
        """
        if platform not in self.platforms:
            self.logger.error(f"Unsupported platform: {platform}")
            return
        
        try:
            self.logger.info(f"Generating post for {platform}")
            user_prefs = self.user_preferences.get_preferences(platform)
            content_tone = user_prefs.get("content_tone", "neutral")
            generated_content = await self._generate_content_with_retries(post_content, content_tone)
            
            await self._post_content_with_retries(platform, generated_content)

        except Exception as e:
            self.logger.error(f"Failed to generate and post content for {platform}: {e}")

    async def _generate_content_with_retries(self, post_content, content_tone, retries=3):
        """
        Attempt to generate content with retries in case of failures.

        :param post_content: The initial content or prompt for generating the post.
        :param content_tone: The tone to be used in the generated content.
        :param retries: The number of retries in case of failure.
        :return: The generated content as a string.
        :raises: Exception if all attempts to generate content fail.
        """
        for attempt in range(retries):
            try:
                generated_content = self.openai_client.complete(f"{post_content} in a {content_tone} tone")
                self.logger.info("Content generated successfully.")
                return generated_content

            except Exception as e:
                self.logger.warning(f"Content generation failed on attempt {attempt + 1}/{retries}: {e}. Retrying...")
                await asyncio.sleep(2)

        raise Exception("Failed to generate content after multiple attempts.")

    async def _post_content_with_retries(self, platform, content, retries=3):
        """
        Attempt to post content with retries in case of failures.

        :param platform: The name of the platform (e.g., 'instagram', 'twitter').
        :param content: The content to be posted.
        :param retries: The number of retries in case of failure.
        :raises: Exception if all attempts to post content fail.
        """
        platform_integration = self.platforms[platform]

        for attempt in range(retries):
            try:
                await platform_integration.post_content(content)
                self.logger.info(f"Content posted successfully on {platform}.")
                return

            except Exception as e:
                self.logger.warning(f"Posting content on {platform} failed on attempt {attempt + 1}/{retries}: {e}. Retrying...")
                await asyncio.sleep(2)

        raise Exception(f"Failed to post content on {platform} after multiple attempts.")

    async def reply_to_random_comment(self, platform, comments):
        """
        Select a random comment and reply to it on the specified social media platform.

        :param platform: The name of the platform (e.g., 'instagram', 'twitter').
        :param comments: A list of comments from which a random comment will be selected.
        """
        if platform not in self.platforms:
            self.logger.error(f"Unsupported platform: {platform}")
            return
        
        try:
            comment = await self.response_generator.select_random_comment(comments)
            if comment:
                reply = await self.response_generator.generate_personalized_reply(comment)
                platform_integration = self.platforms[platform]
                await platform_integration.reply_to_comment(comment, reply)
                self.logger.info(f"Replied to comment on {platform}: {reply}")
            else:
                self.logger.info("No comments available to reply to.")
        except Exception as e:
            self.logger.error(f"Failed to reply to a comment on {platform}: {e}")

    def schedule_post(self, platform, post_content, schedule_time):
        try:
            self.logger.info(f"Scheduling post for {platform} at {schedule_time}")
            import time
            time.sleep(schedule_time)
            self.generate_and_post(platform, post_content)
        except Exception as e:
            self.logger.error(f"Failed to schedule post for {platform}: {e}")

    def run(self, actions):
        for action in actions:
            action_type = action.get('action_type')
            platform = action.get('platform')
            if action_type == 'generate_and_post':
                post_content = action.get('post_content')
                self.generate_and_post(platform, post_content)
            elif action_type == 'reply_to_random_comment':
                self.reply_to_random_comment(platform)
            elif action_type == 'schedule_post':
                post_content = action.get('post_content')
                schedule_time = action.get('schedule_time')
                self.schedule_post(platform, post_content, schedule_time)
            else:
                self.logger.error(f"Unsupported action type: {action_type}")
