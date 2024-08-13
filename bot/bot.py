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

    async def _generate_content_with_retries(self, post_content, content_tone, max_retries=3):
        """
        Generate content with retries in case of failure.

        :param post_content: The initial content or prompt for generating the post.
        :param content_tone: The tone of the content to be generated.
        :param max_retries: Maximum number of retries in case of failure.
        :return: The generated content.
        """
        attempt = 0
        while attempt < max_retries:
            try:
                generated_content = await self.response_generator.generate_content(post_content, content_tone)
                self.logger.info(f"Generated content on attempt {attempt + 1}")
                return generated_content
            except Exception as e:
                attempt += 1
                self.logger.warning(f"Failed to generate content on attempt {attempt}. Error: {e}")
                if attempt == max_retries:
                    self.logger.error("Max retries reached. Failing content generation.")
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _post_content_with_retries(self, platform_integration, content, max_retries=3):
        """
        Post content with retries in case of failure.

        :param platform_integration: The platform integration object (e.g., Instagram, Twitter).
        :param content: The content to be posted.
        :param max_retries: Maximum number of retries in case of failure.
        :return: None
        """
        attempt = 0
        while attempt < max_retries:
            try:
                await platform_integration.post_content(content)
                self.logger.info(f"Posted content on attempt {attempt + 1}")
                return
            except Exception as e:
                attempt += 1
                self.logger.warning(f"Failed to post content on attempt {attempt}. Error: {e}")
                if attempt == max_retries:
                    self.logger.error("Max retries reached. Failing content posting.")
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

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
            self.logger.info(f"Starting content generation for platform: {platform}")
            user_prefs = self.user_preferences.get_preferences(platform)
            content_tone = user_prefs.get("content_tone", "neutral")
            generated_content = await self._generate_content_with_retries(post_content, content_tone)

            await self._post_content_with_retries(self.platforms[platform], generated_content)
            self.logger.info(f"Successfully posted content on {platform}: {generated_content}")
        
        except Exception as e:
            self.logger.exception(f"Failed to generate and post content on {platform}: {e}")

    async def reply_to_random_comment(self, platform):
        """
        Reply to a random comment on the specified platform.

        :param platform: The name of the platform (e.g., 'instagram', 'twitter').
        """
        if platform not in self.platforms:
            self.logger.error(f"Unsupported platform: {platform}")
            return
        
        try:
            self.logger.info(f"Fetching comments for {platform}")
            comments = await self.platforms[platform].get_recent_comments()
            
            if not comments:
                self.logger.info(f"No comments found on {platform} to reply to.")
                return
            
            comment = random.choice(comments)
            reply = await self.response_generator.generate_personalized_reply(comment)
            await self.platforms[platform].reply_to_comment(comment, reply)
            self.logger.info(f"Replied to comment on {platform}: {reply}")
        
        except Exception as e:
            self.logger.exception(f"Failed to reply to a comment on {platform}: {e}")

    def schedule_post(self, platform, post_content, schedule_time):
        """
        Schedule a post to be published on the specified platform at a later time.

        :param platform: The name of the platform (e.g., 'instagram', 'twitter').
        :param post_content: The content to be posted.
        :param schedule_time: Time delay (in seconds) before posting the content.
        """
        try:
            self.logger.info(f"Scheduling post for {platform} to be published in {schedule_time} seconds")
            asyncio.get_event_loop().call_later(
                schedule_time,
                asyncio.create_task,
                self.generate_and_post(platform, post_content)
            )
        except Exception as e:
            self.logger.exception(f"Failed to schedule post for {platform}: {e}")

    def run(self, actions):
        """
        Execute a series of actions.

        :param actions: A list of actions to perform.
        """
        for action in actions:
            try:
                action_type = action.get('action_type')
                platform = action.get('platform')

                if action_type == 'generate_and_post':
                    post_content = action.get('post_content')
                    asyncio.run(self.generate_and_post(platform, post_content))
                elif action_type == 'reply_to_random_comment':
                    asyncio.run(self.reply_to_random_comment(platform))
                elif action_type == 'schedule_post':
                    post_content = action.get('post_content')
                    schedule_time = action.get('schedule_time')
                    self.schedule_post(platform, post_content, schedule_time)
                else:
                    self.logger.error(f"Unsupported action type: {action_type}")

            except Exception as e:
                self.logger.exception(f"Failed to execute action {action}: {e}")
