import os
import json
import jsonpickle
from typing import List, Optional, Dict
from .models import Story, StoryNode, StoryMetadata, Choice, StoryCreationParams
from .firebase_service import firebase_service

# Storage constants
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STORIES_INDEX = "stories_index.json"

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_story(story: Story) -> None:
    """Save a story to Firebase Firestore."""
    try:
        firebase_service.save_story(story)
        print(f"[Storage] Saved story {story.id}: {story.title}")
    except Exception as e:
        print(f"[Storage] Error saving story: {e}")
        raise

def get_story(story_id: str) -> Optional[Story]:
    """Get a story by ID from Firebase."""
    try:
        story = firebase_service.get_story(story_id)
        if story:
            print(f"[Storage] Retrieved story {story_id}: {story.title}")
        else:
            print(f"[Storage] Story not found: {story_id}")
        return story
    except Exception as e:
        print(f"[Storage] Error retrieving story: {e}")
        return None

def delete_story(story_id: str) -> bool:
    """Delete a story from Firebase."""
    try:
        result = firebase_service.delete_story(story_id)
        if result:
            print(f"[Storage] Deleted story {story_id}")
        return result
    except Exception as e:
        print(f"[Storage] Error deleting story: {e}")
        return False

def get_all_stories() -> List[StoryMetadata]:
    """Get metadata for all stories from Firebase."""
    try:
        metadata_list = firebase_service.get_all_stories()
        print(f"[Storage] Retrieved {len(metadata_list)} stories")
        return metadata_list
    except Exception as e:
        print(f"[Storage] Error retrieving all stories: {e}")
        return []

def get_user_stories(user_id: str) -> List[StoryMetadata]:
    """Get metadata for stories owned by a specific user from Firebase."""
    try:
        user_stories = firebase_service.get_user_stories(user_id)
        print(f"[Storage] Retrieved {len(user_stories)} stories for user {user_id}")
        return user_stories
    except Exception as e:
        print(f"[Storage] Error retrieving user stories: {e}")
        return []

def add_story_node(story_id: str, node: StoryNode) -> Optional[Story]:
    """Add a new node to a story in Firebase."""
    try:
        story = get_story(story_id)
        if not story:
            print(f"[Storage] Story not found for adding node: {story_id}")
            return None
        
        # Add the node
        story.nodes[node.id] = node
        
        # Update current node ID
        story.current_node_id = node.id
        
        # Update timestamp
        story.last_updated = node.timestamp
        
        # Save the story
        save_story(story)
        
        print(f"[Storage] Added node {node.id} to story {story_id}")
        return story
    except Exception as e:
        print(f"[Storage] Error adding node: {e}")
        return None

def save_choice(story_id: str, node_id: str, choice_id: str) -> Optional[Story]:
    """Record a choice selection in a story node in Firebase."""
    try:
        story = get_story(story_id)
        if not story:
            print(f"[Storage] Story not found for saving choice: {story_id}")
            return None
        
        if node_id not in story.nodes:
            print(f"[Storage] Node not found in story: {node_id}")
            return None
        
        # Record the choice
        story.nodes[node_id].selected_choice_id = choice_id
        
        # Update timestamp
        import time
        story.last_updated = time.time()
        
        # Save the story
        save_story(story)
        
        print(f"[Storage] Saved choice {choice_id} for node {node_id} in story {story_id}")
        return story
    except Exception as e:
        print(f"[Storage] Error saving choice: {e}")
        return None

def create_story(params: StoryCreationParams, initial_node: Optional[StoryNode] = None) -> Story:
    """Create a new story with the given parameters in Firebase."""
    try:
        # Generate title based on setting
        if params.setting == "cultivation":
            title = f"{params.character_name}'s Cultivation Journey"
        elif params.setting == "academy":
            title = f"{params.character_name} at the Academy"
        elif params.setting == "gamelike":
            title = f"The Adventures of {params.character_name}"
        elif params.setting == "apocalypse":
            title = f"{params.character_name}'s Survival"
        elif params.setting == "fantasy":
            title = f"{params.character_name}'s Fantasy Quest"
        elif params.setting == "scifi":
            title = f"{params.character_name}'s Space Odyssey"
        elif params.setting == "modern":
            title = f"{params.character_name}'s Urban Mystery"
        else:
            title = f"{params.character_name}'s Story"
        
        # Create a node ID
        node_id = "initial"
        
        # Use provided node or create default
        if initial_node:
            node = initial_node
        else:
            import time
            node = StoryNode(
                id=node_id,
                content="Your adventure is about to begin...",
                choices=[
                    Choice(id="1", text="Start your journey")
                ],
                parent_node_id=None,
                timestamp=time.time()
            )
        
        # Determine cultivation stage for cultivation setting
        cultivation_stage = "Qi Condensation Stage (Level 1)" if params.setting == "cultivation" else None
        
        # Create the story
        story = Story(
            title=title,
            character_name=params.character_name,
            character_gender=params.character_gender,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
            story_length=params.story_length,
            power_system="auto",  # AI will decide the appropriate power system
            cultivation_stage=cultivation_stage,
            current_node_id=node.id,
            nodes={node.id: node},
            user_id=params.user_id  # Include user_id from params
        )
        
        # Save the story to Firebase
        save_story(story)
        
        print(f"[Storage] Created new story: {story.id} - {title}")
        return story
    except Exception as e:
        print(f"[Storage] Error creating story: {e}")
        raise

# Legacy functions for backward compatibility (not used with Firebase)
def get_story_ids() -> List[str]:
    """Get list of all story IDs (legacy function for compatibility)."""
    try:
        stories = get_all_stories()
        return [story.id for story in stories]
    except Exception as e:
        print(f"[Storage] Error retrieving story IDs: {e}")
        return []

def save_story_ids(story_ids: List[str]) -> None:
    """Save the list of story IDs (legacy function - no-op with Firebase)."""
    # No-op: Firebase handles this automatically
    pass 