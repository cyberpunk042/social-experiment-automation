import argparse
import json
from openai_client import OpenAIClient
from user_preferences import UserPreferences
from config_manager import ConfigManager
from database_client import DatabaseClient
from bot import SocialBot

def create_post(bot, platform, logger):
    """
    Create a post on the specified platform.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to post on.
        logger (logging.Logger): The logger instance to log the process.

    Returns:
        dict: The response from the platform, including the post ID.
    """
    try:
        result = bot.post_image(platform)
        logger.info(f"Post created successfully on {platform} with ID: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to create post on {platform}: {e}")
        raise

def comment_to_post(bot, platform, media_id, comment_text, logger):
    """
    Post a comment on a specific media on the specified platform.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to comment on.
        media_id (str): The ID of the media to comment on.
        comment_text (str): The text of the comment.
        logger (logging.Logger): The logger instance to log the process.

    Returns:
        dict: The response from the platform, including the comment ID.
    """
    try:
        result = bot.post_comment(platform, media_id, comment_text)
        logger.info(f"Comment posted successfully on {platform} with ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to post comment on {platform}: {e}")
        raise

def reply_to_comments(bot, platform, comment_id, reply_text, logger):
    """
    Reply to a comment on the specified platform.

    Args:
        bot (SocialBot): The bot instance used to perform the action.
        platform (str): The social media platform to reply on.
        comment_id (str): The ID of the comment to reply to.
        reply_text (str): The text of the reply.
        logger (logging.Logger): The logger instance to log the process.

    Returns:
        dict: The response from the platform, including the reply ID.
    """
    try:
        result = bot.reply_to_comment(platform, comment_id, reply_text)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social Experiment Automation Bot")
    parser.add_argument("--action", type=str, required=True, help="Action to perform (e.g., create_post, comment_to_post, reply_to_comments, add_caption)")
    parser.add_argument("--platform", type=str, help="The social media platform to perform the action on (e.g., instagram)")
    parser.add_argument("--media_id", type=str, help="The ID of the media to comment on or reply to")
    parser.add_argument("--comment_text", type=str, help="The text of the comment to post")
    parser.add_argument("--reply_text", type=str, help="The text of the reply to post")
    parser.add_argument("--file", type=str, help="Path to JSON file for adding captions")
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
        create_post(bot, args.platform, bot.logger)
    
    elif args.action == "comment_to_post":
        if not args.platform or not args.media_id or not args.comment_text:
            raise ValueError("Platform, media_id, and comment_text must be specified for commenting on a post.")
        comment_to_post(bot, args.platform, args.media_id, args.comment_text, bot.logger)
    
    elif args.action == "reply_to_comments":
        if not args.platform or not args.comment_id or not args.reply_text:
            raise ValueError("Platform, comment_id, and reply_text must be specified for replying to a comment.")
        reply_to_comments(bot, args.platform, args.comment_id, args.reply_text, bot.logger)
    
    elif args.action == "add_caption":
        if args.file:
            add_caption_from_file(database_client, args.file)
        else:
            add_caption_interactive(database_client)
    
    else:
        raise ValueError(f"Unknown action: {args.action}")
