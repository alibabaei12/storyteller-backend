import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from ..models.models import Story, StoryNode, StoryMetadata, Choice, StoryCreationParams, Feedback, FeedbackRequest
from ..services.firebase_service import firebase_service
from ..services.story_planner import generate_big_story_goal

# Get the logger
logger = logging.getLogger(__name__)

# Storage constants
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
STORIES_INDEX = "stories_index.json"

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_story(story: Story) -> None:
    """Save a story to Firebase Firestore."""
    try:
        firebase_service.save_story(story)
        logger.info(f"Saved story {story.id}: {story.title}")
    except Exception as e:
        logger.error(f"Error saving story: {e}")
        raise

def get_story(story_id: str) -> Optional[Story]:
    """Get a story by ID from Firebase."""
    try:
        story = firebase_service.get_story(story_id)
        if story:
            logger.info(f"Retrieved story {story_id}: {story.title}")
        else:
            logger.info(f"Story not found: {story_id}")
        return story
    except Exception as e:
        logger.error(f"Error retrieving story: {e}")
        return None

def delete_story(story_id: str) -> bool:
    """Delete a story from Firebase."""
    try:
        result = firebase_service.delete_story(story_id)
        if result:
            logger.info(f"Deleted story {story_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting story: {e}")
        return False

def get_all_stories() -> List[StoryMetadata]:
    """Get metadata for all stories from Firebase."""
    try:
        metadata_list = firebase_service.get_all_stories()
        logger.info(f"Retrieved {len(metadata_list)} stories")
        return metadata_list
    except Exception as e:
        logger.error(f"Error retrieving all stories: {e}")
        return []

def get_user_stories(user_id: str) -> List[StoryMetadata]:
    """Get metadata for stories owned by a specific user from Firebase."""
    try:
        user_stories = firebase_service.get_user_stories(user_id)
        logger.info(f"Retrieved {len(user_stories)} stories for user {user_id}")
        return user_stories
    except Exception as e:
        logger.error(f"Error retrieving user stories: {e}")
        return []

def add_story_node(story_id: str, node: StoryNode) -> Optional[Story]:
    """Add a new node to a story in Firebase."""
    try:
        story = get_story(story_id)
        if not story:
            logger.warning(f"Story not found for adding node: {story_id}")
            return None
        
        # Add the node
        story.nodes[node.id] = node
        
        # Update current node ID
        story.current_node_id = node.id
        
        # Update timestamp
        story.last_updated = node.timestamp
        
        # Update memory if it exists
        if hasattr(story, 'memory') and story.memory:
            # Add node ID to story_nodes if not already there
            if node.id not in story.memory.story_nodes:
                story.memory.story_nodes.append(node.id)
            logger.info(f"Updated story memory with node {node.id}")
        
        # Save the story
        try:
            save_story(story)
            logger.info(f"Added node {node.id} to story {story_id}")
            return story
        except Exception as e:
            logger.error(f"Error saving story after adding node: {e}")
            # Try to save without memory if there might be an issue there
            if hasattr(story, 'memory'):
                try:
                    # Create a backup of memory
                    memory_backup = story.memory
                    # Try saving without memory
                    story.memory = None
                    save_story(story)
                    # Restore memory and try again
                    story.memory = memory_backup
                    save_story(story)
                    logger.info(f"Successfully saved story after memory adjustment")
                    return story
                except Exception as backup_error:
                    logger.error(f"Failed backup save attempt: {backup_error}")
            return None
    except Exception as e:
        logger.error(f"Error adding node: {e}")
        return None

def save_choice(story_id: str, node_id: str, choice_id: str) -> Optional[Story]:
    """Record a choice selection in a story node in Firebase."""
    try:
        story = get_story(story_id)
        if not story:
            logger.warning(f"Story not found for saving choice: {story_id}")
            return None
        
        if node_id not in story.nodes:
            logger.warning(f"Node not found in story: {node_id}")
            return None
        
        # Record the choice
        story.nodes[node_id].selected_choice_id = choice_id
        
        # Update timestamp
        import time
        story.last_updated = time.time()
        
        # Save the story
        save_story(story)
        
        logger.info(f"Saved choice {choice_id} for node {node_id} in story {story_id}")
        return story
    except Exception as e:
        logger.error(f"Error saving choice: {e}")
        return None

def create_story(params: StoryCreationParams, initial_node: Optional[StoryNode] = None, arc_goal: Optional[str] = None, big_story_goal: str = "", all_arc_goals: Optional[List[str]] = None) -> Story:
    """Create a new story with the given parameters in Firebase."""
    try:
        # Generate title based on setting and tone

        tone_title = params.tone
        setting_title = params.setting
        
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
        
        # For cultivation stories, initialize memory with story goals
        from ..models.models import StoryMemory

        # Create a memory object with the big story goal
        memory = StoryMemory(
            character_name=params.character_name,
            character_gender=params.character_gender,
            character_origin=params.character_origin,
            setting=params.setting,
            big_story_goal=big_story_goal
        )

        # Use the provided arc goal and all arc goals if available
        if arc_goal:
            # Use all provided arc goals if available
            if all_arc_goals and len(all_arc_goals) > 0:
                memory.arcs = all_arc_goals
                logger.info(f"Using provided arc goals: {len(all_arc_goals)} goals")
            else:
                # If only a single arc goal was provided, use it
                memory.arcs = [arc_goal]
                
            # Initialize arc tracking variables
            memory.current_arc_index = 0
            memory.chapters_completed = 0
            
            # Add first arc to arc history
            if memory.arcs and memory.arcs[0] not in memory.arc_history:
                memory.arc_history.append(memory.arcs[0])
                
            # Set total arcs planned without changing total_chapters_planned 
            memory.total_arcs_planned = len(memory.arcs)
            
            # Make sure chapters_per_arc is consistent with the planned values
            if memory.total_arcs_planned > 0:
                memory.chapters_per_arc = memory.total_chapters_planned // memory.total_arcs_planned
                # Ensure at least 1 chapter per arc
                memory.chapters_per_arc = max(1, memory.chapters_per_arc)
                
            logger.info(f"Using provided arc goal: {memory.arcs[0]}")
        else:
            # Generate new arc goals if none were provided
            try:
                from ..services.story_planner import generate_new_arc_goal
                # Get arc goals with number calculated from total chapters
                arc_goals = generate_new_arc_goal(big_story_goal, [], num_arcs=None)
                
                if arc_goals:
                    # Store all generated arcs in the arcs list
                    memory.arcs = arc_goals
                    
                    # Initialize arc tracking variables
                    memory.current_arc_index = 0
                    memory.chapters_completed = 0
                    
                    # Add first arc to arc history
                    if memory.arcs and memory.arcs[0] not in memory.arc_history:
                        memory.arc_history.append(memory.arcs[0])
                    
                    # Set total arcs planned without changing total_chapters_planned
                    memory.total_arcs_planned = len(memory.arcs)
                    
                    # Make sure chapters_per_arc is consistent with the planned values
                    if memory.total_arcs_planned > 0:
                        memory.chapters_per_arc = memory.total_chapters_planned // memory.total_arcs_planned
                        # Ensure at least 1 chapter per arc
                        memory.chapters_per_arc = max(1, memory.chapters_per_arc)
                    
                    logger.info(f"Generated {len(arc_goals)} arc goals. Current arc goal: {memory.arcs[0]}")
                else:
                    # Fallback if no arcs were generated
                    fallback_arc = "Survive the sect's brutal outer disciple training."
                    memory.arcs = [fallback_arc]
                    memory.arc_history.append(fallback_arc)
                    # Initialize arc tracking variables
                    memory.current_arc_index = 0
                    memory.chapters_completed = 0
                    # Set total arcs planned without changing total_chapters_planned
                    memory.total_arcs_planned = 1
                    memory.chapters_per_arc = memory.total_chapters_planned  # All chapters in one arc
            except Exception as e:
                logger.error(f"Error initializing arc goals: {e}")
                # Set a fallback arc goal
                fallback_arc = "Survive the sect's brutal outer disciple training."
                memory.arcs = [fallback_arc]
                memory.arc_history.append(fallback_arc)
                # Initialize arc tracking variables
                memory.current_arc_index = 0
                memory.chapters_completed = 0
                # Set total arcs planned without changing total_chapters_planned
                memory.total_arcs_planned = 1
                memory.chapters_per_arc = memory.total_chapters_planned  # All chapters in one arc
                logger.info(f"Set fallback arc goal: {fallback_arc}")

        current_arc = memory.arcs[memory.current_arc_index] if memory.arcs else ""
        logger.info(f"Initialized memory with big goal: '{big_story_goal}' and arc goal: '{current_arc}'")
        logger.info(f"Arc progression: {memory.current_arc_index + 1}/{memory.total_arcs_planned}, Chapter: {memory.chapters_completed + 1}/{memory.chapters_per_arc}")
        
        # Calculate overall story progress
        current_story_chapter = ((memory.current_arc_index) * memory.chapters_per_arc) + memory.chapters_completed + 1
        story_progress_percent = round((current_story_chapter / memory.total_chapters_planned) * 100)
        logger.info(f"Overall story progress: Chapter {current_story_chapter}/{memory.total_chapters_planned} ({story_progress_percent}%)")
                
        # Create the story
        story = Story(
            title=title,
            character_name=params.character_name,
            character_gender=params.character_gender,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
            power_system="auto",  # AI will decide the appropriate power system
            cultivation_stage=cultivation_stage,
            current_node_id=node.id,
            nodes={node.id: node},
            user_id=params.user_id,  # Include user_id from params
            memory=memory,  # Add the memory object if it exists
            big_story_goal=big_story_goal  # Add the big story goal
        )
        
        # Save the story
        save_story(story)
        
        # Return the story
        logger.info(f"Created new story: {story.id}: {story.title}")
        return story
    except Exception as e:
        logger.error(f"Error creating story: {e}")
        raise

def get_story_ids() -> List[str]:
    """Get all story IDs from the index file."""
    try:
        index_path = os.path.join(STORAGE_DIR, STORIES_INDEX)
        if not os.path.exists(index_path):
            return []
        with open(index_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error getting story IDs: {e}")
        return []

def save_story_ids(story_ids: List[str]) -> None:
    """Save story IDs to the index file."""
    with open(os.path.join(STORAGE_DIR, STORIES_INDEX), 'w') as f:
        json.dump(story_ids, f)

def submit_feedback(user_id: str, feedback_request: FeedbackRequest) -> bool:
    """Submit user feedback."""
    try:
        # Create a feedback ID
        feedback_id = f"feedback_{int(datetime.now(timezone.utc).timestamp())}_{uuid4().hex[:8]}"
        
        # Get current timestamp as ISO format
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Create the feedback object
        feedback = Feedback(
            id=feedback_id,
            user_id=user_id,
            feedback_type=feedback_request.feedback_type,
            message=feedback_request.message,
            contact_email=feedback_request.contact_email,
            status="open",
            created_at=created_at
        )
        
        # Save the feedback to Firebase
        result = firebase_service.save_feedback(feedback)
        
        if result:
            logger.info(f"Saved feedback {feedback_id} from user {user_id}")
        else:
            logger.warning(f"Failed to save feedback from user {user_id}")
        
        return result
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return False

def get_feedback(feedback_id: str) -> Optional[Feedback]:
    """Get feedback by ID."""
    try:
        return firebase_service.get_feedback(feedback_id)
    except Exception as e:
        logger.error(f"Error getting feedback {feedback_id}: {e}")
        return None

def get_all_feedback() -> List[Feedback]:
    """Get all feedback submissions."""
    try:
        return firebase_service.get_all_feedback()
    except Exception as e:
        logger.error(f"Error getting all feedback: {e}")
        return []

def get_user_feedback(user_id: str) -> List[Feedback]:
    """Get all feedback submissions from a specific user."""
    try:
        return firebase_service.get_user_feedback(user_id)
    except Exception as e:
        logger.error(f"Error getting feedback for user {user_id}: {e}")
        return []

def update_feedback_status(feedback_id: str, status: str) -> bool:
    """Update the status of a feedback submission."""
    try:
        return firebase_service.update_feedback_status(feedback_id, status)
    except Exception as e:
        logger.error(f"Error updating feedback status: {e}")
        return False

def update_story_share_token(story_id: str, share_token: str) -> bool:
    """Update the share token for a story and make it shareable."""
    try:
        return firebase_service.update_story_share_token(story_id, share_token)
    except Exception as e:
        logger.error(f"Error updating share token: {e}")
        return False

def get_story_by_share_token(share_token: str) -> Optional[Story]:
    """Get a story by its share token."""
    try:
        return firebase_service.get_story_by_share_token(share_token)
    except Exception as e:
        logger.error(f"Error getting story by share token: {e}")
        return None

 