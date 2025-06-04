#!/usr/bin/env python3
"""
StoryTeller API Server - An API for the StoryTeller application.
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

# Import the Flask app
from app import run_api

def main():
    """Main entry point for the API server."""
    try:
        print("Starting StoryTeller API server...")
        run_api(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down StoryTeller API server...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please report this issue.")
        sys.exit(1)

if __name__ == "__main__":
    main() 