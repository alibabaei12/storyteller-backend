#!/usr/bin/env python3
"""
StoryTeller - An AI-powered interactive fiction experience.
"""

import os
import sys
from dotenv import load_dotenv

# Ensure we have the correct environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please create a .env file with your OpenAI API key or set it in your environment.")
    print("Example: OPENAI_API_KEY=your_api_key_here")
    sys.exit(1)

# Import the API
from app.api import app

def create_app():
    """Create and return the Flask application for web deployment."""
    return app

def main():
    """Main entry point for the terminal application."""
    # Only import StoryGame for terminal usage
    from app import StoryGame
    game = StoryGame()
    try:
        game.start()
    except KeyboardInterrupt:
        print("\nThank you for playing StoryTeller!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please report this issue.")
        sys.exit(1)

if __name__ == "__main__":
    # If PORT environment variable is set, run the web app
    if os.environ.get("PORT"):
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    else:
        # Otherwise run the terminal game
        main() 