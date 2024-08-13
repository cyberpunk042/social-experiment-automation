# bot/bot.py

import logging
from bot.openai_client import OpenAIClient
from bot.user_preferences import UserPreferences
from bot.social_media.instagram_api import InstagramIntegration
from bot.social_media.twitter import TwitterIntegration
from bot.config_manager import ConfigManager
import random

class Bot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.openai_client = OpenAIClient(self.config_manager)
        self.user_preferences = UserPreferences(self.config_manager)
        self.platforms = {
            'instagram': InstagramIntegration(self.config_manager),
            'twitter': TwitterIntegration(self.config_manager)
        }

    def generate_and_post(self, platform, post_content):
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
        if comments:
            return random.choice(comments)
        self.logger.warning("No comments provided for selection")
        return None

    def _generate_personalized_reply(self, comment):
        try:
            user_pref = self.user_preferences.get_preferences(comment['user_id'])
            prompt = f"Based on the user's preferences: {user_pref}, reply to the comment: {comment['text']}"
            return self.openai_client.complete(prompt)
        except Exception as e:
            self.logger.error(f"Failed to generate personalized reply: {e}")
            return "Sorry, couldn't generate a reply."

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
