import argparse
import json
import os
import logging
from uuid import uuid4
from openai_client import OpenAIClient
from user_preferences import UserPreferences
from config_manager import ConfigManager
from database_client import DatabaseClient
from datetime import datetime, timedelta
from bot import SocialBot

LOG_DIR = 'logs'
LOG_FILE = f"{LOG_DIR}/{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}-{uuid4()}.log"

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
    
# Logging configuration
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_post(bot, platform, logger, delay_post=None):
    """
    Create a post on the specified platform, with an optional delay.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to post on.
        logger (logging.Logger): The logger instance to log the process.
        delay_post (str, optional): A string representing the delay in hours before posting. Default is None.

    Returns:
        dict: The response from the platform, including the post ID.
    """
    try:
        # If delay_post is specified, convert it to a timedelta and calculate the scheduled time
        if delay_post:
            try:
                delay_duration = parse_delay_post(delay_post)
                post_date = datetime.now() + delay_duration
                post_timestamp = int(post_date.timestamp())
                logger.info(f"Scheduling post on {platform} to be published at {post_date.isoformat()}")
                result = bot.post_image(platform, schedule_time=post_timestamp)
            except ValueError as ve:
                logger.error(f"Invalid delay_post value: {delay_post}. {str(ve)}")
                raise
        else:
            # Immediate post if no delay is specified
            result = bot.post_image(platform)
        
        logger.info(f"Post created successfully on {platform} with ID: {result.get('scheduled_post_id') or result.get('url')}")
        return result

    except Exception as e:
        logger.error(f"Failed to create post on {platform}: {e}", exc_info=True)
        raise

def comment_to_post(bot, platform, media_id, logger):
    """
    Post a comment on a specific media on the specified platform.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to comment on.
        media_id (str): The ID of the media to comment on.
        logger (logging.Logger): The logger instance to log the process.

    Returns:
        dict: The response from the platform, including the comment ID.
    """
    try:
        result = bot.post_comment(platform, media_id)
        logger.info(f"Comment posted successfully on {platform} with ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to post comment on {platform}: {e}")
        raise

def reply_to_comments(bot, platform, media_id, logger):
    """
    Reply to a comment on the specified platform.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to reply on.
        media_id (str): The ID of the media to reply to.
        logger (logging.Logger): The logger instance to log the process.

    Returns:
        dict: The response from the platform, including the reply ID.
    """
    try:
        result = bot.reply_to_comments(platform, media_id)
        logger.info(f"Reply posted successfully on {platform} with ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to reply to comment on {platform}: {e}")
        raise

def add_caption_interactive(database_client):
    """
    Prompt the user to input caption data interactively.

    Args:
        database_client (DatabaseClient): The database client used to add the caption.
    """
    caption_data = {}

    # Interactive input for each required field
    caption_data["caption_text"] = input("Enter the caption text: ")
    caption_data["tags"] = input("Enter tags (comma-separated): ").split(',')
    caption_data["length"] = input("Enter the caption length (short/medium/long): ")
    caption_data["category"] = input("Enter the caption category: ")
    caption_data["tone"] = input("Enter the caption tone: ")
    
    # Engagement data
    caption_data["likes"] = int(input("Enter the number of likes: "))
    caption_data["shares"] = int(input("Enter the number of shares: "))
    caption_data["comments"] = int(input("Enter the number of comments: "))

    # Add the caption to the database
    result = database_client.add_caption(caption_data)
    print(f"Caption added successfully with ID: {result}")

def add_caption_from_file(database_client, file_path):
    """
    Add captions from a JSON file.

    Args:
        database_client (DatabaseClient): The database client used to add captions.
        file_path (str): The path to the JSON file containing caption data.
    """
    with open(file_path, 'r') as file:
        captions = json.load(file)
        for caption_data in captions:
            result = database_client.add_caption(caption_data)
            
            # Since result is a list, access the first element
            if isinstance(result, list) and result:
                print(f"Caption added successfully with ID: {result[0]['id']}")
            else:
                print("Failed to add caption or retrieve ID.")
                
def parse_delay_post(delay_post):
    """
    Parse the delay_post string to return a timedelta object.

    Args:
        delay_post (str): A string representing the delay in the format of "Xh", "Ym", or "Zd"
                        where X, Y, Z are integers and h, m, d represent hours, minutes, and days respectively.

    Returns:
        timedelta: The corresponding timedelta object.
    
    Raises:
        ValueError: If the format of delay_post is invalid.
    """
    try:
        if delay_post.endswith("h"):
            delay_hours = int(delay_post[:-1])
            return timedelta(hours=delay_hours)
        elif delay_post.endswith("m"):
            delay_minutes = int(delay_post[:-1])
            return timedelta(minutes=delay_minutes)
        elif delay_post.endswith("d"):
            delay_days = int(delay_post[:-1])
            return timedelta(days=delay_days)
        else:
            raise ValueError("Invalid format. Use 'Xm' for minutes, 'Xh' for hours, or 'Xd' for days, where X is an integer.")
    except ValueError:
        raise ValueError("Invalid delay_post value. Ensure it's in the format of 'Xm', 'Xh', or 'Xd'.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social Experiment Automation Bot")
    parser.add_argument("--action", type=str, required=True, help="Action to perform (e.g., create_post, comment_to_post, reply_to_comments, add_caption)")
    parser.add_argument("--platform", type=str, help="The social media platform to perform the action on (e.g., instagram)")
    parser.add_argument("--media_id", type=str, help="The ID of the media to comment on or reply to")
    parser.add_argument("--file", type=str, help="Path to JSON file for adding captions")
    parser.add_argument("--delay_post", type=str, help="The delay in minutes, hours, or days to schedule the post (e.g., '15m', '2h', '1d')", default=None)
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # Initialize the necessary components
    config_manager = ConfigManager()
    database_client = DatabaseClient(config_manager)
    user_preferences = UserPreferences(config_manager, database_client, 1)
    openai_client = OpenAIClient(config_manager, user_preferences)
    interactive_mode = args.interactive
    bot = SocialBot(config_manager, openai_client, database_client, user_preferences, interactive_mode)

    if args.action == "create_post":
        if not args.platform:
            raise ValueError("Platform must be specified for creating a post.")
        create_post(bot, args.platform, bot.logger, args.delay_post)
    
    elif args.action == "comment_to_post":
        if not args.platform or not args.media_id or not args.comment_text:
            raise ValueError("Platform and media_id must be specified for commenting on a post.")
        comment_to_post(bot, args.platform, args.media_id, bot.logger)
    
    elif args.action == "reply_to_comments":
        if not args.platform or not args.media_id or not args.reply_text:
            raise ValueError("Platform and media_id must be specified for replying to a comments.")
        reply_to_comments(bot, args.platform, args.media_id, bot.logger)
    
    elif args.action == "add_caption":
        if args.file:
            add_caption_from_file(database_client, args.file)
        else:
            add_caption_interactive(database_client)
    
    else:
        raise ValueError(f"Unknown action: {args.action}")
