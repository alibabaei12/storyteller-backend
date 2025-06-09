"""
Logging configuration for the StoryTeller application.
"""

import logging

def setup_logging():
    """
    Configure logging for the application.
    Sets up a basic logger with formatting and log level.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ) 