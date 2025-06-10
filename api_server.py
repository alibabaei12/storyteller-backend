#!/usr/bin/env python3
"""
Simple API server for StoryTeller
Run with: python3 api_server.py
"""

import logging
import os

from dotenv import load_dotenv

from app.api import app
from app.config.logging import setup_logging

# Configure logging
setup_logging()

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logging.info("Starting StoryTeller API server...")
    logging.info(f"Host: {host}")
    logging.info(f"Port: {port}")
    logging.info(f"Debug mode: {debug}")
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug) 