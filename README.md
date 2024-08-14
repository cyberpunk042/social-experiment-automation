# Social Experiment Automation

This project automates interactions on social media platforms, particularly Instagram, using a bot that can create posts, comment on posts, and reply to comments. The bot leverages OpenAI for generating content and interacts with Instagram`s API to automate these tasks.

## Features

- **Automated Post Creation**: Generates and posts images with captions to Instagram.
- **Commenting**: Posts comments on existing Instagram posts.
- **Replying to Comments**: Automatically replies to comments on Instagram posts.
- **Integration Tests**: End-to-end tests using real API interactions to validate the bot`s functionality.

## Setup

### Prerequisites

- Python 3.8+
- Poetry (Python dependency management tool)
- Instagram API credentials
- OpenAI API credentials

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/social-experiment-automation.git
   cd social-experiment-automation
   ```

2. **Set Up a Virtual Environment with Poetry**

   Ensure Poetry is installed. If not, install it via:

   ```bash
   pip install poetry
   ```

   Then, install the dependencies:

   ```bash
   poetry install
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```ini
   instagram_api_key=your_instagram_api_key
   instagram_access_token=your_instagram_access_token
   openai_api_key=your_openai_api_key
   ```

   Replace `your_instagram_api_key`, `your_instagram_access_token`, and `your_openai_api_key` with your actual credentials.

### Usage

You can run the bot by invoking the `main.py` script and specifying the action you want to perform:

```bash
poetry run python bot/main.py --action create_post --platform instagram
poetry run python bot/main.py --action comment_to_post --platform instagram
poetry run python bot/main.py --action reply_to_comments --platform instagram
```

The bot will use the credentials and configurations specified in the `.env` file to interact with Instagram.

## Adding Captions to the Database

The bot supports adding new captions to the Supabase database either interactively through the command line or via a JSON file. This feature allows users to populate the database with captions that can later be used for social media posts.

### Usage

You can add captions using two methods:

1. **Interactive Mode**: This mode prompts you to enter each field of the caption interactively.

    To use interactive mode:

    ```bash
    poetry run python bot/main.py --action add_caption
    ```

    You will be prompted to enter the following details for each caption:

    - **Caption Text**: The actual caption content.
    - **Tags**: Tags associated with the caption (comma-separated).
    - **Length**: Length of the caption (e.g., short, medium, long).
    - **Category**: Category or theme of the caption (e.g., inspirational, humorous).
    - **Tone**: The tone of the caption (e.g., friendly, formal).
    - **Engagement Metrics**: Historical data on engagement, such as the number of likes, shares, and comments.

2. **File Mode**: This mode allows you to add multiple captions from a JSON file.

    To use file mode:

    ```bash
    poetry run python bot/main.py --action add_caption --file path/to/captions.json
    ```

    The JSON file should contain an array of caption objects, where each object has the following structure:

    ```json
    [
        {
            "text": "The future belongs to those who believe in the beauty of their dreams.",
            "tags": ["inspirational", "future", "dreams"],
            "length": "medium",
            "category": "inspirational",
            "tone": "inspirational",
            "engagement": {
                "likes": 120,
                "shares": 15,
                "comments": 5
            }
        },
        {
            "text": "Believe you can and you're halfway there.",
            "tags": ["motivation", "believe", "success"],
            "length": "short",
            "category": "motivational",
            "tone": "encouraging",
            "engagement": {
                "likes": 200,
                "shares": 25,
                "comments": 10
            }
        }
    ]
    ```

### Important Notes

- Ensure that the JSON file is correctly formatted and that each caption object includes all required fields.
- The `DatabaseClient` will validate the structure of each caption before inserting it into the database. If any required fields are missing, the insertion will fail.
- This feature is integrated with Supabase via the `DatabaseClient`, ensuring that all captions are stored consistently.



### Testing

#### Unit Tests

Unit tests are provided to validate individual components of the bot, such as content generation and API interactions. These tests use mocked data to simulate various scenarios.

To run the unit tests:

```bash
poetry run python -m unittest discover -s tests
```

#### Integration Tests

Integration tests are provided to validate the full workflow of the bot using real API interactions with Instagram. These tests create real posts, comments, and replies on Instagram.

**Important:** Use a test Instagram account for integration tests to avoid cluttering your production account.

To run the integration tests:

```bash
poetry run python test_integration_social_bot.py
```

### Directory Structure

```
.
├── bot
│   ├── __init__.py
│   ├── bot.py
│   ├── config_manager.py
│   ├── openai_client.py
│   ├── response_generator.py
│   ├── social_media
│   │   ├── __init__.py
│   │   ├── instagram_api.py
│   │   └── twitter_api.py  # If applicable
│   ├── user_preferences.py
│   └── database_client.py
├── tests
│   ├── __init__.py
│   ├── test_instagram_api_integration.py
│   ├── test_openai_api_client.py
│   ├── test_response_generator.py
│   └── test_social_bot.py
├── .env.example
├── README.md
├── requirements.txt
├── pyproject.toml
└── test_integration_social_bot.py
```

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

