import argparse
import logging
from bot import Bot
from bot.config_manager import ConfigManager

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Social Media Bot - Automate social media tasks.")
    parser.add_argument('action', choices=['create_post', 'reply_to_comments'], help="Action to perform.")
    parser.add_argument('--platform', required=True, choices=['instagram', 'twitter'], help="Social media platform.")
    parser.add_argument('--content', help="Content for the post or reply.")
    parser.add_argument('--num_comments', type=int, default=1, help="Number of comments to reply to.")
    args = parser.parse_args()

    # Initialize the bot
    config_manager = ConfigManager()
    bot = Bot()

    # Execute the action based on the arguments
    try:
        if args.action == 'create_post':
            if not args.content:
                logger.error("Content is required to create a post.")
                return
            bot.generate_and_post(args.platform, args.content)
            logger.info(f"Post created on {args.platform} with content: {args.content}")
        
        elif args.action == 'reply_to_comments':
            for _ in range(args.num_comments):
                bot.reply_to_random_comment(args.platform)
            logger.info(f"Replied to {args.num_comments} comment(s) on {args.platform}.")

    except Exception as e:
        logger.exception(f"An error occurred while performing the action: {e}")

if __name__ == '__main__':
    main()
