# bot/response_generator.py
from openai_client import OpenAIClient

class ResponseGenerator:
    def __init__(self, openai_api_key):
        self.openai_client = OpenAIClient(openai_api_key)

    def generate_response(self, prompt):
        return self.openai_client.complete(prompt)

    def post_responses(self, social_media_integration, posts):
        for post in posts:
            prompt = self.create_prompt(post)
            response = self.generate_response(prompt)
            social_media_integration.post_response(post['id'], response)

    @staticmethod
    def create_prompt(post):
        return f"Respond to the following post: {post['text']}"
