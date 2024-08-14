import argparse
import logging
import asyncio
from bot.config_manager import ConfigManager
from bot.bot import SocialBot

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Social Media Bot - Automate social media tasks.")
    parser.add_argument('action', choices=['create_post', 'comment_to_post', 'reply_to_comments'], help="Action to perform.")
    parser.add_argument('--platform', required=True, choices=['twitter', 'instagram'], help="Social media platform.")
    parser.add_argument('--interactive', action='store_true', help="Prompt for confirmation before sending data.")
    args = parser.parse_args()

    # Initialize configuration manager
    config_manager = ConfigManager()

    # Initialize SocialBot with or without interactive mode
    bot = SocialBot(config_manager, interactive=args.interactive)

    # Execute the action specified by the user
    try:
        asyncio.run(execute_action(bot, args, logger))
    except Exception as e:
        logger.error(f"An error occurred: {e}")

async def execute_action(bot, args, logger):
    """
    Execute the action specified by the command-line arguments.
    """
    if args.action == 'create_post':
        await create_post(bot, args.platform, logger)
    elif args.action == 'comment_to_post':
        await comment_to_post(bot, args.platform, logger)
    elif args.action == 'reply_to_comments':
        await reply_to_comments(bot, args.platform, logger)
    else:
        logger.error(f"Unsupported action: {args.action}")

async def create_post(bot, platform, logger):
    try:
        result = bot.post_image(platform=platform)
        print(f"Post Result: {result}")
    except Exception as e:
        logger.error(f"Failed to create post on {platform}: {e}")

async def comment_to_post(bot, platform, logger):
    try:
        media_id = input("Enter the media ID to comment on: ") if bot.interactive else None
        result = bot.post_comment(platform=platform, media_id=media_id)
        print(f"Comment to Post Result: {result}")
    except Exception as e:
        logger.error(f"Failed to comment on post on {platform}: {e}")

async def reply_to_comments(bot, platform, logger):
    try:
        comment_id = input("Enter the comment ID to reply to: ") if bot.interactive else None
        result = bot.reply_to_comment(platform=platform, comment_id=comment_id)
        print(f"Reply Result: {result}")
    except Exception as e:
        logger.error(f"Failed to reply to comment on {platform}: {e}")

if __name__ == "__main__":
    main()
