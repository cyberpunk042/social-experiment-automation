import logging
from bot.openai_client import OpenAIClient
import random

class ResponseGenerator:
    def __init__(self, openai_client: OpenAIClient, user_preferences):
        """
        Initialize the ResponseGenerator class.

        :param openai_client: The OpenAIClient instance used for generating responses.
        :param user_preferences: The UserPreferences instance used for retrieving user-specific settings.
        """
        self.openai_client = openai_client
        self.user_preferences = user_preferences
        self.logger = logging.getLogger(__name__)

    async def generate_response(self, prompt):
        """
        Generate a response based on the provided prompt.

        :param prompt: The text prompt to generate a response for.
        :return: The generated response as a string, or an error message if generation fails.
        """
        try:
            self.logger.info(f"Generating response for prompt: {prompt}")
            return await self.openai_client.complete(prompt)
        except Exception as e:
            self.logger.exception(f"Failed to generate response for prompt '{prompt}': {e}")
            return "Sorry, I couldn't generate a response."

    async def generate_personalized_reply(self, comment):
        """
        Generate a personalized reply to a comment based on user preferences.

        :param comment: The comment to reply to.
        :return: The generated reply as a string, or an error message if generation fails.
        """
        try:
            user_pref = self.user_preferences.get_preferences(comment['user_id'])
            response_style = user_pref.get("response_style", "neutral")
            interaction_type = user_pref.get("interaction_type", "neutral")

            prompt = f"Reply to '{comment['text']}' in a {response_style} style for a {interaction_type} interaction."
            self.logger.info(f"Generating personalized reply for comment: {comment['text']} with style: {response_style}")
            return await self.generate_response(prompt)
        except Exception as e:
            self.logger.exception(f"Failed to generate personalized reply for comment '{comment['text']}': {e}")
            return "Sorry, I couldn't generate a reply."

    async def select_random_comment(self, comments):
        """
        Select a random comment from the provided list of comments.

        :param comments: A list of comments.
        :return: A randomly selected comment, or None if the list is empty.
        """
        if comments:
            selected_comment = random.choice(comments)
            self.logger.info(f"Selected random comment: {selected_comment['text']}")
            return selected_comment
        self.logger.info("No comments available to select.")
        return None
