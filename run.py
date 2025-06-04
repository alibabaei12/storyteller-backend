#!/usr/bin/env python3
"""
Development server script for StoryTeller API.
"""

from app.api import app

if __name__ == "__main__":
    print("Starting StoryTeller API development server...")
    print("API will be available at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True) 