import os
import json
import jsonpickle
from typing import List, Optional, Dict
from .models import Story, StoryNode, StoryMetadata, Choice, StoryCreationParams, Feedback, FeedbackRequest
from .firebase_service import firebase_service
from datetime import datetime, timezone, timedelta
from uuid import uuid4

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
        # Generate title based on setting and tone
        tone_titles = {
            "romantic": "Love Story", "mystery": "Mystery", "adventure": "Adventure", 
            "thriller": "Thriller", "comedy": "Comedy", "drama": "Story",
            "horror": "Horror Tale", "slice-of-life": "Story", "epic": "Epic",
            "philosophical": "Journey"
        }
        
        setting_titles = {
            "modern": "Urban", "fantasy": "Fantasy", "scifi": "Space", 
            "academy": "Academy", "historical": "Historical", "gamelike": "Game",
            "cultivation": "Cultivation", "apocalypse": "Survival"
        }
        
        tone_title = tone_titles.get(params.tone, "Story")
        setting_title = setting_titles.get(params.setting, "")
        
        if setting_title:
            title = f"{params.character_name}'s {setting_title} {tone_title}"
        else:
            title = f"{params.character_name}'s {tone_title}"
        
        # Create a node ID
        node_id = "initial"
        
        # Use provided node or create default
        if initial_node:
            node = initial_node
        else:
            node = StoryNode(
                id=node_id,
                content="Your adventure is about to begin...",
                choices=[
                    Choice(id="1", text="Start your journey")
                ],
                parent_node_id=None
            )
        
        # Determine progress indicator based on setting
        cultivation_stage = None
        if params.setting == "cultivation":
            cultivation_stage = "Qi Condensation Stage (Level 1)"
        elif params.setting == "fantasy":
            cultivation_stage = "Novice Adventurer (Level 1)"
        elif params.setting == "academy":
            cultivation_stage = "First Year Student (Rank F)"
        elif params.setting == "gamelike":
            cultivation_stage = "Level 1 Adventurer"
        elif params.setting == "apocalypse":
            cultivation_stage = "Rookie Survivor"
        elif params.setting == "scifi":
            cultivation_stage = "Cadet" 
        elif params.setting == "modern":
            cultivation_stage = "Rookie Investigator"
        elif params.setting == "historical":
            cultivation_stage = "Aspiring Apprentice"
        # Other general settings get no progress indicator for slice-of-life stories
        
        # Create the story
        story = Story(
            title=title,
            character_name=params.character_name,
            character_gender=params.character_gender,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
    
            language_complexity=params.language_complexity,
            manga_genre=params.manga_genre,  # Add the missing manga_genre field
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

def submit_feedback(user_id: str, feedback_request: FeedbackRequest) -> bool:
    """
    Submit feedback with rate limiting and validation.
    Returns True if successful, False if rate limited or invalid.
    """
    try:
        # Check rate limiting - max 3 per day, 1 per 10 minutes
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        ten_minutes_ago = now - timedelta(minutes=10)
        
        # Check daily limit
        daily_count = firebase_service.db.collection('feedback').where(
            'user_id', '==', user_id
        ).where(
            'created_at', '>=', today_start.isoformat()
        ).get()
        
        if len(daily_count) >= 3:
            print(f"[Storage] Rate limit exceeded for user {user_id}: {len(daily_count)} submissions today")
            return False
        
        # Check recent submission limit
        recent_count = firebase_service.db.collection('feedback').where(
            'user_id', '==', user_id
        ).where(
            'created_at', '>=', ten_minutes_ago.isoformat()
        ).get()
        
        if len(recent_count) >= 1:
            print(f"[Storage] Rate limit exceeded for user {user_id}: recent submission")
            return False
        
        # Validate input
        if not feedback_request.message or len(feedback_request.message.strip()) < 5:
            print(f"[Storage] Invalid feedback: message too short")
            return False
            
        if len(feedback_request.message) > 500:
            print(f"[Storage] Invalid feedback: message too long")
            return False
            
        if feedback_request.feedback_type not in ['bug', 'feature', 'general']:
            print(f"[Storage] Invalid feedback type: {feedback_request.feedback_type}")
            return False
        
        # Create feedback record
        feedback_id = str(uuid4())
        feedback = Feedback(
            id=feedback_id,
            user_id=user_id,
            feedback_type=feedback_request.feedback_type,
            message=feedback_request.message.strip()[:500],  # Ensure max length
            contact_email=feedback_request.contact_email.strip()[:100] if feedback_request.contact_email else "",
            status="open",
            created_at=now.isoformat()
        )
        
        # Store in database
        firebase_service.db.collection('feedback').document(feedback_id).set({
            'user_id': feedback.user_id,
            'feedback_type': feedback.feedback_type,
            'message': feedback.message,
            'contact_email': feedback.contact_email,
            'status': feedback.status,
            'created_at': feedback.created_at
        })
        
        print(f"[Storage] Feedback submitted successfully: {feedback_id}")
        return True
        
    except Exception as e:
        print(f"[Storage] Error submitting feedback: {e}")
        return False

def update_story_share_token(story_id: str, share_token: str) -> bool:
    """Update a story's share token in Firebase."""
    try:
        return firebase_service.update_story_share_token(story_id, share_token)
    except Exception as e:
        print(f"[Storage] Error updating share token: {e}")
        return False

def get_story_by_share_token(share_token: str) -> Optional[Story]:
    """Get a story by its share token from Firebase."""
    try:
        story = firebase_service.get_story_by_share_token(share_token)
        if story:
            print(f"[Storage] Retrieved shared story: {story.title}")
        else:
            print("[Storage] Shared story not found for provided token")
        return story
    except Exception as e:
        print(f"[Storage] Error retrieving shared story: {e}")
        return None