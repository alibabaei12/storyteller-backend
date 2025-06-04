import os

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
from .api import app as flask_app, run_api 