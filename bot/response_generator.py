
from openai_client import OpenAIClient
import random

class ResponseGenerator:
    def __init__(self, openai_client: OpenAIClient, user_preferences):
        self.openai_client = openai_client
        self.user_preferences = user_preferences

    def generate_response(self, prompt):
        return self.openai_client.complete(prompt)

    def generate_personalized_reply(self, comment):
        try:
            user_pref = self.user_preferences.get_preferences(comment['user_id'])
            prompt = f"Based on the user's preferences: {user_pref}, reply to the comment: {comment['text']}"
            return self.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Failed to generate personalized reply: {e}")
            return "Sorry, couldn't generate a reply."

    def select_random_comment(self, comments):
        if comments:
            return random.choice(comments)
        self.logger.warning("No comments provided for selection")
        return None

    def post_responses(self, social_media_integration, posts):
        for post in posts:
            prompt = self.create_prompt(post)
            response = self.generate_response(prompt)
            social_media_integration.post_response(post['id'], response)

    @staticmethod
    def create_prompt(post):
        return f"Respond to the following post: {post['text']}"
