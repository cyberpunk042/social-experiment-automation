# Social Experiment Automation Bot

This project is an automation bot designed to interact with social media platforms like Instagram and Twitter. It can automatically generate and post content, reply to comments, and handle user preferences. The bot integrates with the OpenAI API for content generation and supports real-time updates via Supabase.

## Features

- **Automated Posting**: Generate and post content to Instagram and Twitter.
- **Automated Replies**: Reply to comments on social media posts based on user-defined preferences.
- **Real-Time Updates**: Subscribe to database changes via Supabase and trigger events in real-time.
- **User Preferences Management**: Store and retrieve user-specific preferences for content generation and interaction styles.
- **Notification Service**: Send notifications via email with support for both plain text and HTML formats.
- **Error Handling & Logging**: Robust error handling and comprehensive logging throughout the application.

## Project Structure

```
social_experiment_automation/
│
├── bot/
│   ├── __init__.py
│   ├── bot.py                    # Main bot logic for interacting with social media platforms
│   ├── config_manager.py         # Manages configuration settings using environment variables
│   ├── database_client.py        # Handles database interactions with Supabase
│   ├── event_system.py           # Manages event-driven architecture and subscribers
│   ├── instagram_api.py          # Handles interactions with Instagram's API
│   ├── twitter.py                # Handles interactions with Twitter's API
│   ├── notification_service.py   # Sends notifications via email
│   ├── openai_client.py          # Interacts with OpenAI's API for content generation
│   ├── real_time_updates.py      # Manages real-time updates via Supabase
│   ├── response_generator.py     # Generates content and replies using OpenAI
│   ├── smtp_client.py            # Handles sending emails using SMTP
│   ├── user_preferences.py       # Manages user-specific preferences
│   └── main.py                   # Entry point to run bot tasks from the command line
│
└── README.md                     # Project documentation
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cyberpunk042/social-experiment-automation.git
   cd social-experiment-automation
   ```

2. **Install Poetry (if you don't have it already):**

   Poetry is a dependency management tool for Python. You can install it using the following command:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Make sure to add Poetry to your system's PATH as instructed by the installer.

3. **Install the dependencies:**

   Once you have Poetry installed, run the following command to install the project dependencies:

   ```bash
   poetry install
   ```

4. **Activate the virtual environment:**

   Poetry automatically creates and manages a virtual environment for your project. You can activate it using:

   ```bash
   poetry shell
   ```

5. **Set up environment variables:**

   Create a `.env` file in the root directory and add the necessary environment variables:

   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   INSTAGRAM_API_KEY=your_instagram_api_key
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET_KEY=your_twitter_api_secret_key
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=your_smtp_port
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   ```

## Usage

### Running the Bot

You can run the bot using the `main.py` script, which provides command-line options for different actions.

#### Create a Post

To create a new post on a social media platform:

```bash
python main.py create_post --platform [instagram|twitter] --content "Your post content"
```

#### Reply to Comments

To reply to a specified number of comments on a social media platform:

```bash
python main.py reply_to_comments --platform [instagram|twitter] --num_comments [number]
```

> **Note:** All commands should be run within the Poetry shell. If you're not in the Poetry shell, prefix commands with `poetry run`, like so:
> ```bash
> poetry run python main.py create_post --platform instagram --content "Hello World!"
> ```

### Real-Time Updates

The bot can also handle real-time updates by subscribing to events via Supabase. This functionality is managed in `real_time_updates.py` and is triggered automatically based on database changes.

### Notification Service

The bot can send notifications via email. Both plain text and HTML formats are supported. This is managed by the `notification_service.py` and `smtp_client.py` modules.

### Configuration

Configuration settings are managed via environment variables, which can be defined in a `.env` file. The `config_manager.py` module handles loading and validating these settings.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
