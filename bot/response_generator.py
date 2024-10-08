import logging
from openai_client import OpenAIClient
from database_client import DatabaseClient
from user_preferences import UserPreferences

class ResponseGenerator:
    """
    ResponseGenerator is responsible for generating content such as captions, images,
    comments, and replies. It interacts with the database to retrieve captions,
    uses OpenAI for text generation, and considers user preferences for personalized content.
    uses DALL-E for image generation, and considers user preferences for personalized content.
    """

    def __init__(self, openai_client: OpenAIClient, database_client: DatabaseClient, user_preferences: UserPreferences):
        """
        Initialize the ResponseGenerator with the necessary clients and preferences.

        Args:
            openai_client (OpenAIClient): The OpenAIClient instance used for generating responses and images.
            database_client (DatabaseClient): The client to interact with the Supabase database.
            user_preferences (UserPreferences): The user preferences for personalized content.
        """
        self.openai_client = openai_client
        self.database_client = database_client
        self.user_preferences = user_preferences
        self.logger = logging.getLogger(__name__)

    def generate_caption(self, caption_text=None):
        """
        Retrieve and personalize a caption from the database for a new Instagram post,
        with support for configurable tone and style.

        Returns:
            str: A retrieved and personalized caption.

        Raises:
            Exception: If no captions are found or there is an issue with the database.
        """
        try:
            # Retrieve user preferences for response style and tone
            response_style = self.user_preferences.response_style
            content_tone = self.user_preferences.content_tone

            # Construct the prompt for OpenAI with the specified style, tone, and additional directives
            prompt = (
                f"Generate a caption in a {response_style} style with a {content_tone} tone: '{caption_text}'"
            )
            
            # Use OpenAI to generate the personalized caption
            personalized_caption = self.openai_client.complete(prompt)
            self.logger.info(f"Generated caption: {personalized_caption}")
            return personalized_caption

        except Exception as e:
            self.logger.error(f"Error in generating caption: {e}")
            raise Exception(f"Error retrieving or personalizing caption: {e}")

    def generate_image(self, caption):
        """
        Generate an image based on the provided caption using OpenAI's image generation capabilities.

        Args:
            caption (str): The caption to inspire the image generation.

        Returns:
            str: The URL to the generated image.

        Raises:
            Exception: If the image generation fails.
        """
        try:
            preferences = self.user_preferences.get_preferences()  # Ensuring consistency in accessing preferences
            modified_caption = f"{caption} with elements such as {preferences.get('style', None)} style, {preferences.get('color_scheme', None)} color scheme."
            image_url = self.openai_client.generate_image(modified_caption)
            self.logger.info(f"Generated image URL: {image_url}")
            return image_url
        except Exception as e:
            self.logger.error(f"Error in generating image: {e}")
            raise Exception(f"Image generation failed: {e}")

    async def generate_personalized_comment(self, context=None):
        """
        Generate a personalized comment for an Instagram post based on the provided context.

        Args:
            context (str): Optional context to guide the comment generation.

        Returns:
            str: A generated personalized comment.

        Raises:
            Exception: If personalized comment generation fails.
        """
        try:
            response_style = self.user_preferences.comment_response_style
            content_tone = self.user_preferences.comment_content_tone
            interaction_type = self.user_preferences.comment_interaction_type
            
            prompt = f"Generate a comment in a {response_style} style with a {content_tone} tone that aligns with {interaction_type} interactions. Context: {context}"
            personalized_comment = await self.openai_client.complete(prompt)
            self.logger.info(f"Generated personalized comment: {personalized_comment}")
            return personalized_comment
        except Exception as e:
            self.logger.error(f"Error in generating personalized comment: {e}")
            raise Exception(f"Error generating personalized comment: {e}")

    async def generate_personalized_reply(self, context=None):
        """
        Generate a personalized reply to a comment on an Instagram post based on the provided context.

        Args:
            context (str): Optional context to guide the reply generation.

        Returns:
            str: A generated personalized reply.

        Raises:
            Exception: If personalized reply generation fails.
        """
        try:
            response_style = self.user_preferences.reply_response_style
            content_tone = self.user_preferences.reply_content_tone
            interaction_type = self.user_preferences.reply_interaction_type
            
            prompt = f"Generate a reply in a {response_style} style with a {content_tone} tone that aligns with {interaction_type} interactions. Context: {context}"
            personalized_reply = await self.openai_client.complete(prompt)
            self.logger.info(f"Generated personalized reply: {personalized_reply}")
            return personalized_reply
        except Exception as e:
            self.logger.error(f"Error in generating personalized reply: {e}")
            raise Exception(f"Error generating personalized reply: {e}")

    async def generate_all_content_for_post(self, context=None):
        """
        Generate all necessary content (caption, image, comment, and reply) for a post.

        Args:
            context (str): Optional context to guide the content generation.

        Returns:
            dict: A dictionary containing the generated caption, image path, comment, and reply.

        Raises:
            Exception: If any part of the content generation process fails.
        """
        try:
            caption = self.generate_caption()
            image_url = self.generate_image(caption)
            comment = await self.generate_personalized_comment(context)
            reply = await self.generate_personalized_reply(context)

            self.logger.info("Successfully generated all content for the post.")
            return {
                "caption": caption,
                "image_url": image_url,
                "comment": comment,
                "reply": reply
            }
        except Exception as e:
            self.logger.error(f"Error generating content for post: {e}")
            raise Exception(f"Error generating content for post: {e}")
