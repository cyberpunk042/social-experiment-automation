import time
import logging

class Bot:
    def __init__(self, social_media_integrations, openai_client, user_profiles):
        self.social_media_integrations = social_media_integrations
        self.openai_client = openai_client
        self.user_profiles = user_profiles
        self.logger = logging.getLogger(__name__)

    def generate_response(self, post_content, user_id, context=None):
        user_profile = self.user_profiles.get(user_id)
        prompt = f"Generate a response based on the user's profile: {user_profile}. Post content: {post_content}"
        if context:
            prompt += f" Context: {context}"
        try:
            start_time = time.time()
            response = self.openai_client.complete(prompt)
            end_time = time.time()
            self.logger.info(f"Response generated in {end_time - start_time:.2f} seconds.")
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
                    response = self.generate_response(post['content'], post['user_id'], context)
                    integration.post_response(post['id'], response)
                end_time = time.time()
                self.logger.info(f"Processed {len(posts)} posts in {end_time - start_time:.2f} seconds.")
            except Exception as e:
                self.logger.error(f"Error running bot for {identifier}: {e}")
