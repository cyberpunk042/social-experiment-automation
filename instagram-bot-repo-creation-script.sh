#!/bin/bash

# Define project name and description
PROJECT_NAME="cyberpunk042_instagram_bot"
PROJECT_DESCRIPTION="A bot for Instagram interaction and response generation using OpenAI's GPT model."

# Initialize the project with Poetry, specifying the name and description
poetry init --name "$PROJECT_NAME" --description "$PROJECT_DESCRIPTION" --author "Cyberpunk042 <admin@cyberpunk042.net>" -n

# Add necessary dependencies
poetry add requests python-dotenv openai

# Create the project directory structure
mkdir -p bot tests

# Create the necessary files for the bot and tests
touch bot/__init__.py \
      bot/main.py \
      bot/bot.py \
      bot/instagram_client.py \
      bot/openai_client.py \
      bot/config_manager.py \
      bot/response_generator.py \
      tests/__init__.py \
      .env \
      README.md

# Write the initial README content
cat > README.md <<EOF
# $PROJECT_NAME

## Description
$PROJECT_DESCRIPTION

## Setup
To set up the project, follow these steps:

1. Install Poetry if you haven't already.
2. Clone this repository.
3. Navigate to the project directory and run \`poetry install\` to install dependencies.

## Configuration
Create a \`.env\` file in the project root with the following variables:

\`\`\`
INSTAGRAM_API_KEY=your_instagram_api_key
OPENAI_API_KEY=your_openai_api_key
\`\`\`

## Usage
To run the bot, execute the following command:

\`\`\`bash
poetry run python bot/main.py
\`\`\`

## Development
This project follows Object-Oriented Programming principles and is structured for easy maintenance and scalability.

## Contributing
Contributions are welcome. Please open an issue or submit a pull request.

## License
Specify the license under which the project is made available.
EOF

# Write the initial .env content with placeholders for API keys
cat > .env <<EOF
# Instagram API Key
INSTAGRAM_API_KEY=your_instagram_api_key

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key
EOF

# Write the initial ConfigManager class with comments
cat > bot/config_manager.py <<EOF
from dotenv import load_dotenv
import os

class ConfigManager:
    """Manages the configuration settings for the bot."""

    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        self.instagram_api_key = os.getenv('INSTAGRAM_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # Ensure that the API keys are present
        if not self.instagram_api_key or not self.openai_api_key:
            raise ValueError("API keys for Instagram or OpenAI are missing in the .env file.")

    # Add any additional configuration methods here
EOF

# Initialize Git repository and create .gitignore
git init
echo '.env' >> .gitignore
echo 'poetry.lock' >> .gitignore
echo '__pycache__/' >> .gitignore
echo '.venv' >> .gitignore

# Add all files to the repository and commit
git add .
git commit -m "Initial project setup with Poetry, README, and basic file structure."

# End of script
echo "Project setup complete. Please review the README.md and .env files."
