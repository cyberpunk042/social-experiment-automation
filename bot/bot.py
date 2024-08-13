import time
import logging

class Bot:
    def __init__(self, social_media_integrations, openai_client, user_profiles, user_preferences):
        self.social_media_integrations = social_media_integrations
        self.openai_client = openai_client
        self.user_profiles = user_profiles
        self.user_preferences = user_preferences
        self.logger = logging.getLogger(__name__)

    def generate_response(self, post_content, user_id, context=None):
        user_profile = self.user_profiles.get(user_id)
        user_preference = self.user_preferences.get(user_id)
        tone = user_preference.get('preferred_tone', 'neutral')
        prompt = self.create_prompt(post_content, user_profile, tone, context)
        return self.execute_openai_call(prompt)

    def create_prompt(self, post_content, user_profile, tone, context):
        prompt = f"Using a {tone} tone, and considering the user's profile: {user_profile}, generate a response to this post: {post_content}"
        if context:
            prompt += f" Context: {context}"
        return prompt

    def execute_openai_call(self, prompt):
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
                self.process_posts(integration, identifier, context)
            except Exception as e:
                self.logger.error(f"Error running bot for {identifier}: {e}")

    def process_posts(self, integration, identifier, context):
        start_time = time.time()
        posts = integration.get_posts(identifier)
        for post in posts:
            response = self.generate_response(post['content'], post['user_id'], context)
            integration.post_response(post['id'], response)
        end_time = time.time()
        self.logger.info(f"Processed {len(posts)} posts in {end_time - start_time:.2f} seconds.")
