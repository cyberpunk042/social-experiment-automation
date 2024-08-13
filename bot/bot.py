import logging
from bot.openai_client import OpenAIClient
from bot.user_preferences import UserPreferences
from bot.social_media.instagram_api import InstagramAPI
from bot.social_media.twitter import TwitterAPI
from bot.config_manager import ConfigManager
import random

class Bot:
    def __init__(self):
        """
        Initialize the Bot class, setting up configuration, clients, and platform APIs.
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.openai_client = OpenAIClient(self.config_manager)
        self.user_preferences = UserPreferences()
        self.platforms = {
            'instagram': InstagramAPI(self.config_manager),
            'twitter': TwitterAPI(self.config_manager)
        }

    def generate_and_post(self, platform, post_content):
        """
        Generate a post using OpenAI and publish it on the specified platform.

        :param platform: The platform to publish the post on ('instagram' or 'twitter').
        :param post_content: The content to seed the OpenAI prompt with.
        """
        if platform not in self.platforms:
            self.logger.error(f"Unsupported platform: {platform}")
            return

        try:
            self.logger.info(f"Generating post for {platform}")
            generated_content = self.openai_client.complete(post_content)
            self.platforms[platform].create_post(generated_content)
            self.logger.info(f"Post successfully created on {platform}")
        except Exception as e:
            self.logger.error(f"Failed to generate and post content on {platform}: {e}")

    def reply_to_random_comment(self, platform):
        """
        Reply to a random comment on the specified platform using a personalized LLM chain.

        :param platform: The platform to interact with ('instagram' or 'twitter').
        """
        if platform not in self.platforms:
            self.logger.error(f"Unsupported platform: {platform}")
            return

        try:
            self.logger.info(f"Replying to random comment on {platform}")
            comments = self.platforms[platform].get_recent_comments()
            if not comments:
                self.logger.info(f"No comments available to reply to on {platform}")
                return

            comment_to_reply = self._select_random_comment(comments)
            if comment_to_reply:
                reply = self._generate_personalized_reply(comment_to_reply)
                self.platforms[platform].reply_to_comment(comment_to_reply['id'], reply)
                self.logger.info(f"Reply successfully posted on {platform}")
            else:
                self.logger.info(f"No valid comment found to reply to on {platform}")
        except Exception as e:
            self.logger.error(f"Failed to reply to comment on {platform}: {e}")

    def _select_random_comment(self, comments):
        """
        Select a random comment from a list of comments.

        :param comments: A list of comments.
        :return: A randomly selected comment.
        """
        if comments:
            return random.choice(comments)
        self.logger.warning("No comments provided for selection")
        return None

    def _generate_personalized_reply(self, comment):
        """
        Generate a personalized reply to a comment using OpenAI and user preferences.

        :param comment: The comment to reply to.
        :return: A generated reply.
        """
        try:
            user_pref = self.user_preferences.get_preferences(comment['user_id'])
            prompt = f"Based on the user's preferences: {user_pref}, reply to the comment: {comment['text']}"
            return self.openai_client.complete(prompt)
        except Exception as e:
            self.logger.error(f"Failed to generate personalized reply: {e}")
            return "Sorry, couldn't generate a reply."

    def schedule_post(self, platform, post_content, schedule_time):
        """
        Schedule a post to be published at a specific time.

        :param platform: The platform to publish the post on ('instagram' or 'twitter').
        :param post_content: The content to seed the OpenAI prompt with.
        :param schedule_time: The time to schedule the post.
        """
        try:
            self.logger.info(f"Scheduling post for {platform} at {schedule_time}")
            # Logic to handle scheduling could involve adding the post to a queue or using a task scheduler.
            # Placeholder logic for demonstration:
            import time
            time.sleep(schedule_time)
            self.generate_and_post(platform, post_content)
        except Exception as e:
            self.logger.error(f"Failed to schedule post for {platform}: {e}")

    def run(self, actions):
        """
        Run the bot to perform a series of actions. This function serves as the entry point for the bot's operation.

        :param actions: A list of actions to perform, where each action is a dictionary with 'action_type', 
                        'platform', and any additional parameters required for the action.
        """
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
