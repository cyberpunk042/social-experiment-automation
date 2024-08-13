#TODO: redo page
# bot/instapy_integration.py
from instapy import InstaPy
import logging

#TODO: redo class, align with instagram_api functions
class InstaPyIntegration():
    def __init__(self, username, password):
        self.logger = logging.getLogger(__name__)
        try:
            self.bot = InstaPy(username=username, password=password)
            self.bot.login()
            self.logger.info("InstaPy login successful.")
        except Exception as e:
            self.logger.error(f"Failed to login to Instagram: {e}")

    def post_response(self, post_id, response):
        try:
            self.bot.set_do_comment(enabled=True, percentage=100)
            self.bot.set_comments([response])
            # Navigate to post and comment
            self.logger.info(f"Successfully posted a comment on post {post_id}.")
        except Exception as e:
            self.logger.error(f"Failed to post comment on post {post_id}: {e}")

    def __del__(self):
        try:
            self.bot.end()
            self.logger.info("InstaPy session ended.")
        except Exception as e:
            self.logger.error(f"Failed to end InstaPy session: {e}")

    def get_posts(self, hashtag):
        # InstaPy doesn't directly support fetching posts by hashtag.
        # This method would need to be implemented using InstaPy's functionality,
        # or you might need to use another tool or API for this purpose.
        pass

    def __del__(self):
        self.bot.end()
