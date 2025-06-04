import os
import json
import jsonpickle
from typing import List, Optional, Dict
from .models import Story, StoryNode, StoryMetadata, Choice, StoryCreationParams

# Storage constants
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STORIES_INDEX = "stories_index.json"

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_story(story: Story) -> None:
    """Save a story to local storage."""
    try:
        # Convert to JSON-serializable format
        story_json = jsonpickle.encode(story)
        
        # Save the story to a file
        story_path = os.path.join(STORAGE_DIR, f"{story.id}.json")
        with open(story_path, "w") as f:
            f.write(story_json)
        
        # Update the stories index
        story_ids = get_story_ids()
        if story.id not in story_ids:
            story_ids.append(story.id)
            save_story_ids(story_ids)
        
        print(f"[Storage] Saved story {story.id}: {story.title}")
    except Exception as e:
        print(f"[Storage] Error saving story: {e}")
        raise

def get_story(story_id: str) -> Optional[Story]:
    """Get a story by ID."""
    try:
        story_path = os.path.join(STORAGE_DIR, f"{story_id}.json")
        if not os.path.exists(story_path):
            print(f"[Storage] Story not found: {story_id}")
            return None
        
        with open(story_path, "r") as f:
            story_json = f.read()
        
        story = jsonpickle.decode(story_json)
        print(f"[Storage] Retrieved story {story_id}: {story.title}")
        return story
    except Exception as e:
        print(f"[Storage] Error retrieving story: {e}")
        return None

def delete_story(story_id: str) -> bool:
    """Delete a story."""
    try:
        story_path = os.path.join(STORAGE_DIR, f"{story_id}.json")
        if os.path.exists(story_path):
            os.remove(story_path)
        
        # Update the stories index
        story_ids = get_story_ids()
        if story_id in story_ids:
            story_ids.remove(story_id)
            save_story_ids(story_ids)
        
        print(f"[Storage] Deleted story {story_id}")
        return True
    except Exception as e:
        print(f"[Storage] Error deleting story: {e}")
        return False

def get_all_stories() -> List[StoryMetadata]:
    """Get metadata for all stories."""
    try:
        story_ids = get_story_ids()
        metadata_list = []
        
        for story_id in story_ids:
            story = get_story(story_id)
            if story:
                metadata = StoryMetadata(
                    id=story.id,
                    title=story.title,
                    character_name=story.character_name,
                    setting=story.setting,
                    last_updated=story.last_updated,
                    cultivation_stage=story.cultivation_stage
                )
                metadata_list.append(metadata)
        
        # Sort by last updated (newest first)
        metadata_list.sort(key=lambda x: x.last_updated, reverse=True)
        
        print(f"[Storage] Retrieved {len(metadata_list)} stories")
        return metadata_list
    except Exception as e:
        print(f"[Storage] Error retrieving all stories: {e}")
        return []

def add_story_node(story_id: str, node: StoryNode) -> Optional[Story]:
    """Add a new node to a story."""
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
    """Record a choice selection in a story node."""
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
    """Create a new story with the given parameters."""
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
            nodes={node.id: node}
        )
        
        # Save the story
        save_story(story)
        
        print(f"[Storage] Created new story: {story.id} - {title}")
        return story
    except Exception as e:
        print(f"[Storage] Error creating story: {e}")
        raise

def get_story_ids() -> List[str]:
    """Get list of all story IDs."""
    try:
        index_path = os.path.join(STORAGE_DIR, STORIES_INDEX)
        if not os.path.exists(index_path):
            return []
        
        with open(index_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Storage] Error retrieving story IDs: {e}")
        return []

def save_story_ids(story_ids: List[str]) -> None:
    """Save the list of story IDs."""
    try:
        index_path = os.path.join(STORAGE_DIR, STORIES_INDEX)
        with open(index_path, "w") as f:
            json.dump(story_ids, f)
    except Exception as e:
        print(f"[Storage] Error saving story IDs: {e}")
        raise 