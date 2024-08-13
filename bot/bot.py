import logging
from bot.openai_client import OpenAIClient
from bot.user_preferences import UserPreferences
from bot.social_media.instagram_api import InstagramIntegration
from bot.social_media.twitter import TwitterIntegration
from bot.config_manager import ConfigManager
from bot.response_generator import ResponseGenerator
import random

class Bot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.openai_client = OpenAIClient(self.config_manager)
        self.user_preferences = UserPreferences(self.config_manager)
        self.response_generator = ResponseGenerator(self.openai_client, self.user_preferences)
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
            user_prefs = self.user_preferences.get_preferences(platform)  # Fetch and validate preferences
            content_tone = user_prefs.get("content_tone")
            content_frequency = user_prefs.get("content_frequency")
            generated_content = self.openai_client.complete(f"{post_content} in a {content_tone} tone")

            # Adjust posting frequency based on user preference
            if content_frequency == "daily":
                self.logger.info(f"Post frequency set to daily for {platform}.")
            elif content_frequency == "weekly":
                self.logger.info(f"Post frequency set to weekly for {platform}.")
            elif content_frequency == "monthly":
                self.logger.info(f"Post frequency set to monthly for {platform}.")
            else:
                self.logger.info(f"Post frequency set to default (daily) for {platform}.")

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
            self.user_preferences.refresh_preferences(platform)  # Refresh preferences before generating a reply
            comment_to_reply = self.response_generator.select_random_comment(comments)
            if comment_to_reply:
                user_prefs = self.user_preferences.get_preferences(platform)
                interaction_type = user_prefs.get("interaction_type")
                response_style = user_prefs.get("response_style")

                # Generate the reply based on interaction type and response style
                if interaction_type == "proactive":
                    reply = self.response_generator.generate_response(f"Proactively replying to {comment_to_reply['text']} in a {response_style} style.")
                elif interaction_type == "reactive":
                    reply = self.response_generator.generate_response(f"Reactively replying to {comment_to_reply['text']} in a {response_style} style.")
                else:
                    reply = self.response_generator.generate_response(f"Replying to {comment_to_reply['text']} in a neutral style.")

                self.platforms[platform].reply_to_comment(comment_to_reply['id'], reply)
                self.logger.info(f"Reply successfully posted on {platform}")
            else:
                self.logger.info(f"No valid comment found to reply to on {platform}")
        except Exception as e:
            self.logger.error(f"Failed to reply to comment on {platform}: {e}")

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
