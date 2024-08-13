import argparse
import logging
import asyncio
from bot import Bot
from bot.config_manager import ConfigManager

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Social Media Bot - Automate social media tasks.")
    parser.add_argument('action', choices=['create_post', 'reply_to_comments', 'like_posts', 'follow_users', 'unfollow_users'], help="Action to perform.")
    parser.add_argument('--platform', required=True, choices=['twitter', 'instagram'], help="Social media platform.")
    parser.add_argument('--interactive', action='store_true', help="Prompt for confirmation before sending data.")
    args = parser.parse_args()

    # Initialize bot with or without interactive mode
    bot = Bot(interactive=args.interactive)

    # Execute the action specified by the user
    asyncio.run(bot.run(args.platform, args.action))

if __name__ == "__main__":
    main()
