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

    def generate_response_options(self, post_content, user_id, context=None, num_options=3):
        user_profile = self.user_profiles.get(user_id)
        user_preference = self.user_preferences.get(user_id)
        tone = user_preference.get('preferred_tone', 'neutral')
        responses = []
        
        for _ in range(num_options):
            prompt = f"Using a {tone} tone, and considering the user's profile: {user_profile}, generate a response to this post: {post_content}"
            if context:
                prompt += f" Context: {context}"
            try:
                response = self.openai_client.complete(prompt)
                responses.append(response)
            except Exception as e:
                self.logger.error(f"Error generating response: {e}")
        
        return responses

    def select_best_response(self, responses, post_content):
        evaluation_prompt = (
            "You are an expert in communication. Below are several potential responses to the following post:\n\n"
            f"Post content: {post_content}\n\n"
            "Responses:\n"
        )
        for idx, response in enumerate(responses, 1):
            evaluation_prompt += f"{idx}. {response}\n"

        evaluation_prompt += (
            "\nChoose the response that best matches the tone and context, and explain why it is the best choice."
        )

        try:
            evaluation_result = self.openai_client.complete(evaluation_prompt)
            selected_response_index = self._extract_selected_response(evaluation_result)
            return responses[selected_response_index - 1]  # Adjusting for 1-based index
        except Exception as e:
            self.logger.error(f"Error selecting best response: {e}")
            return responses[0] if responses else "I'm sorry, I can't generate a response right now."

    def _extract_selected_response(self, evaluation_result):
        import re
        match = re.search(r'Response (\d+)', evaluation_result)
        return int(match.group(1)) if match else 1  # Default to the first response

    def generate_response(self, post_content, user_id, context=None):
        responses = self.generate_response_options(post_content, user_id, context)
        return self.select_best_response(responses, post_content)

    def run(self, identifier, context=None):
        for integration in self.social_media_integrations:
            try:
                posts = integration.get_posts(identifier)
                for post in posts:
                    response = self.generate_response(post['content'], post['user_id'], context)
                    integration.post_response(post['id'], response)
            except Exception as e:
                self.logger.error(f"Error running bot for {identifier}: {e}")


    def analyze_sentiment(self, post_content):
        blob = TextBlob(post_content)
        return blob.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)


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

    def process_posts(self, integration, identifier, context):
        start_time = time.time()
        posts = integration.get_posts(identifier)
        for post in posts:
            response = self.generate_response(post['content'], post['user_id'], context)
            integration.post_response(post['id'], response)
        end_time = time.time()
        self.logger.info(f"Processed {len(posts)} posts in {end_time - start_time:.2f} seconds.")
