# bot/instapy_integration.py
from instapy import InstaPy
from bot.social_media.base import SocialMediaIntegrationBase

class InstaPyIntegration(SocialMediaIntegrationBase):
    def __init__(self, username, password):
        self.bot = InstaPy(username=username, password=password)
        self.bot.login()

    def get_posts(self, hashtag):
        # InstaPy doesn't directly support fetching posts by hashtag.
        # This method would need to be implemented using InstaPy's functionality,
        # or you might need to use another tool or API for this purpose.
        pass

    def post_response(self, post_id, response):
        # InstaPy doesn't directly support commenting by post ID.
        # You would need to navigate to the post and then comment.
        # This is a placeholder for how you might implement such a method.
        self.bot.set_do_comment(enabled=True, percentage=100)
        self.bot.set_comments([response])
        # Navigate to post and comment
        pass

    def __del__(self):
        self.bot.end()
