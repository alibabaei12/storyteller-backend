import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('storyteller.log') if not os.environ.get("PORT") else logging.StreamHandler()
    ]
)

# Only import StoryGame for terminal usage, not for web deployment
if not os.environ.get("PORT"):
    from .game import StoryGame

from .models import Story, StoryNode, Choice, StoryCreationParams, StoryMetadata
from .storage import (
    save_story, 
    get_story, 
    delete_story, 
    get_all_stories, 
    add_story_node, 
    save_choice, 
    create_story
)
from .ai_service import AIService
from .api import app, run_api 