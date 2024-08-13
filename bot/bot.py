# bot/bot.py
from bot.social_media.instapy import InstaPyIntegration
import logging
import time

class Bot:
    def __init__(self, social_media_integrations, openai_client):
        self.social_media_integrations = social_media_integrations
        self.openai_client = openai_client
        self.logger = logging.getLogger(__name__)

    def generate_response(self, post_content, context=None):
        prompt = f"Generate a thoughtful response to this post: {post_content}"
        if context:
            prompt += f" Consider the following context: {context}"
        try:
            start_time = time.time()
            response = self.openai_client.complete(prompt)
            end_time = time.time()
            self.logger.info(f"Generated response in {end_time - start_time:.2f} seconds.")
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm sorry, I can't generate a response right now."

    def run(self, identifier, context=None):
        for integration in self.social_media_integrations:
            try:
                start_time = time.time()
                posts = integration.get_posts(identifier)
                for post in posts:
                    response = self.generate_response(post['content'], context)
                    integration.post_response(post['id'], response)
                end_time = time.time()
                self.logger.info(f"Processed {len(posts)} posts in {end_time - start_time:.2f} seconds.")
            except Exception as e:
                self.logger.error(f"Error running bot for {identifier}: {e}")
