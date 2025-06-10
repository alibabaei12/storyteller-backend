"""
StoryTeller Python API for interactive fiction stories.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

import openai

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(f"{log_dir}/storyteller.log", maxBytes=1000000, backupCount=5),
        logging.StreamHandler()
    ]
)

from .storage.storage import get_all_stories, save_story, get_story, delete_story, add_story_node, save_choice, create_story
from .models.models import Story, StoryNode, Choice, StoryCreationParams, StoryMetadata
from .services import AIService
from .api import app, run_api

__version__ = "0.1.0"

# Configure OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    logging.warning("OPENAI_API_KEY environment variable not set. OpenAI features will not work.")