import time
import logging
from textblob import TextBlob

class Bot:
    def __init__(self, social_media_integrations, openai_client, user_profiles, user_preferences):
        self.social_media_integrations = social_media_integrations
        self.openai_client = openai_client
        self.user_profiles = user_profiles
        self.user_preferences = user_preferences
        self.logger = logging.getLogger(__name__)

    def analyze_sentiment(self, post_content):
        blob = TextBlob(post_content)
        return blob.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)

    def generate_response(self, post_content, user_id, context=None):
        sentiment = self.analyze_sentiment(post_content)
        sentiment_description = "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"
        user_profile = self.user_profiles.get(user_id)
        user_preference = self.user_preferences.get(user_id)
        tone = user_preference.get('preferred_tone', 'neutral')
        prompt = f"Using a {tone} tone, and considering the sentiment ({sentiment_description}) and user's profile: {user_profile}, generate a response to this post: {post_content}"
        if context:
            prompt += f" Context: {context}"
        return self.execute_openai_call(prompt)

    def get_user_data(self, user_id):
        return self.user_profiles.get(user_id), self.user_preferences.get(user_id)

    def create_prompt(self, post_content, user_profile, tone, sentiment, context):
        sentiment_description = "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"
        prompt = f"Using a {tone} tone, considering sentiment ({sentiment_description}), and user's profile: {user_profile}, generate a response to this post: {post_content}"
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

    def log_event_processing(self, event_type, start_time, end_time, event_data):
        processing_time = end_time - start_time
        self.logger.info(f"Processed event '{event_type}' in {processing_time:.2f} seconds with data: {event_data}")

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

    def process_posts(self, integration, identifier, context):
        start_time = time.time()
        posts = integration.get_posts(identifier)
        for post in posts:
            response = self.generate_response(post['content'], post['user_id'], context)
            integration.post_response(post['id'], response)
        end_time = time.time()
        self.logger.info(f"Processed {len(posts)} posts in {end_time - start_time:.2f} seconds.")
