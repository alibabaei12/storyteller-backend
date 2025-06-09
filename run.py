#!/usr/bin/env python3
"""
Development server script for StoryTeller API.
"""

import logging
from app.api import app
from app.config.logging import setup_logging

# Configure logging
setup_logging()

if __name__ == "__main__":
    logging.info("Starting StoryTeller API development server...")
    logging.info("API will be available at http://localhost:8000")
    app.run(host="0.0.0.0", port=5001, debug=True) 