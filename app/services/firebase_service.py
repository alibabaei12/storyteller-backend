import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging
from typing import List, Optional, Dict, Any
from ..models.models import Story, StoryNode, StoryMetadata, UserUsage, Feedback, FeedbackRequest

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for Firebase Firestore operations."""
    
    def __init__(self):
        """Initialize Firebase Admin SDK."""
        self._db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Try to get existing app
            app = firebase_admin.get_app()
            self._db = firestore.client(app)
            logger.info("Using existing Firebase app")
        except ValueError:
            # No app exists, create new one
            try:
                # Get credentials from environment variables
                cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                project_id = os.getenv('FIREBASE_PROJECT_ID')
                
                # Check for individual credential environment variables (for production)
                firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                
                if firebase_private_key and firebase_client_email and project_id:
                    # Production: Use individual environment variables
                    cred_dict = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key": firebase_private_key.replace('\\n', '\n'),  # Fix newlines
                        "client_email": firebase_client_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred, {'projectId': project_id})
                    self._db = firestore.client()
                    logger.info(f"Initialized with environment credentials for project: {project_id}")
                    
                elif cred_path and os.path.exists(cred_path):
                    # Development: Use service account file
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {'projectId': project_id})
                    self._db = firestore.client()
                    logger.info(f"Initialized with service account file: {cred_path}")
                    
                else:
                    # Fallback to default credentials
                    firebase_admin.initialize_app()
                    self._db = firestore.client()
                    logger.info("Initialized with default credentials")
            except Exception as e:
                logger.error(f"Error initializing: {e}")
                logger.error("Make sure Firebase Admin SDK is properly configured")
                logger.error(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
                logger.error(f"File exists: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))}")
                raise
    
    @property
    def db(self):
        """Get Firestore database client."""
        if not self._db:
            self._initialize_firebase()
        return self._db
    
    # Story operations
    def save_story(self, story: Story) -> None:
        """Save a story to Firestore."""
        try:
            # Convert story to dict
            story_data = story.model_dump()
            
            # Save to Firestore
            doc_ref = self.db.collection('stories').document(story.id)
            doc_ref.set(story_data)
            
            logger.info(f"Saved story {story.id}: {story.title}")
        except Exception as e:
            logger.error(f"Error saving story: {e}")
            raise
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Get a story by ID from Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc = doc_ref.get()
            
            if doc.exists:
                story_data = doc.to_dict()
                story = Story(**story_data)
                logger.info(f"Retrieved story {story_id}: {story.title}")
                return story
            else:
                logger.info(f"Story not found: {story_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving story: {e}")
            return None
    
    def delete_story(self, story_id: str) -> bool:
        """Delete a story from Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc_ref.delete()
            logger.info(f"Deleted story {story_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting story: {e}")
            return False
    
    def get_all_stories(self) -> List[StoryMetadata]:
        """Get metadata for all stories from Firestore."""
        try:
            stories_ref = self.db.collection('stories')
            docs = stories_ref.stream()
            
            metadata_list = []
            for doc in docs:
                story_data = doc.to_dict()
                metadata = StoryMetadata(
                    id=story_data['id'],
                    title=story_data['title'],
                    character_name=story_data['character_name'],
                    setting=story_data['setting'],
                    last_updated=story_data['last_updated'],
                    cultivation_stage=story_data.get('cultivation_stage'),
                    user_id=story_data.get('user_id')
                )
                metadata_list.append(metadata)
            
            # Sort by last updated (newest first)
            metadata_list.sort(key=lambda x: x.last_updated, reverse=True)
            
            logger.info(f"Retrieved {len(metadata_list)} stories")
            return metadata_list
        except Exception as e:
            logger.error(f"Error retrieving all stories: {e}")
            return []
    
    def get_user_stories(self, user_id: str) -> List[StoryMetadata]:
        """Get metadata for stories owned by a specific user from Firestore."""
        try:
            stories_ref = self.db.collection('stories').where('user_id', '==', user_id)
            docs = stories_ref.stream()
            
            metadata_list = []
            for doc in docs:
                story_data = doc.to_dict()
                metadata = StoryMetadata(
                    id=story_data['id'],
                    title=story_data['title'],
                    character_name=story_data['character_name'],
                    setting=story_data['setting'],
                    last_updated=story_data['last_updated'],
                    cultivation_stage=story_data.get('cultivation_stage'),
                    user_id=story_data.get('user_id')
                )
                metadata_list.append(metadata)
            
            # Sort by last updated (newest first)
            metadata_list.sort(key=lambda x: x.last_updated, reverse=True)
            
            logger.info(f"Retrieved {len(metadata_list)} stories for user {user_id}")
            return metadata_list
        except Exception as e:
            logger.error(f"Error retrieving user stories: {e}")
            return []
    
    # User usage operations
    def get_user_usage(self, user_id: str) -> Optional[UserUsage]:
        """Get user usage data from Firestore."""
        try:
            doc_ref = self.db.collection('usage').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                usage_data = doc.to_dict()
                return UserUsage.from_dict(usage_data)
            else:
                return None
        except Exception as e:
            logger.error(f"Error retrieving user usage: {e}")
            return None
    
    def save_user_usage(self, usage: UserUsage) -> None:
        """Save user usage data to Firestore."""
        try:
            doc_ref = self.db.collection('usage').document(usage.user_id)
            doc_ref.set(usage.to_dict())
        except Exception as e:
            logger.error(f"Error saving user usage: {e}")
            raise
    
    def get_all_user_usage(self) -> Dict[str, UserUsage]:
        """Get usage data for all users from Firestore."""
        try:
            usage_ref = self.db.collection('usage')
            docs = usage_ref.stream()
            
            usage_dict = {}
            for doc in docs:
                usage_data = doc.to_dict()
                user_id = usage_data.get("user_id")
                if user_id:
                    usage_dict[user_id] = UserUsage.from_dict(usage_data)
            
            return usage_dict
        except Exception as e:
            logger.error(f"Error retrieving all user usage: {e}")
            return {}

    # Feedback operations
    def save_feedback(self, feedback: Feedback) -> bool:
        """Save feedback to Firestore."""
        try:
            doc_ref = self.db.collection('feedback').document(feedback.id)
            doc_ref.set(feedback.model_dump())
            logger.info(f"Saved feedback {feedback.id} from user {feedback.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False
    
    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID from Firestore."""
        try:
            doc_ref = self.db.collection('feedback').document(feedback_id)
            doc = doc_ref.get()
            
            if doc.exists:
                feedback_data = doc.to_dict()
                return Feedback(**feedback_data)
            else:
                return None
        except Exception as e:
            logger.error(f"Error retrieving feedback: {e}")
            return None
    
    def get_all_feedback(self) -> List[Feedback]:
        """Get all feedback submissions from Firestore."""
        try:
            feedback_ref = self.db.collection('feedback')
            docs = feedback_ref.stream()
            
            feedback_list = []
            for doc in docs:
                feedback_data = doc.to_dict()
                feedback_list.append(Feedback(**feedback_data))
            
            return feedback_list
        except Exception as e:
            logger.error(f"Error retrieving all feedback: {e}")
            return []
    
    def get_user_feedback(self, user_id: str) -> List[Feedback]:
        """Get all feedback submissions from a specific user from Firestore."""
        try:
            feedback_ref = self.db.collection('feedback').where('user_id', '==', user_id)
            docs = feedback_ref.stream()
            
            feedback_list = []
            for doc in docs:
                feedback_data = doc.to_dict()
                feedback_list.append(Feedback(**feedback_data))
            
            return feedback_list
        except Exception as e:
            logger.error(f"Error retrieving user feedback: {e}")
            return []
    
    def update_feedback_status(self, feedback_id: str, status: str) -> bool:
        """Update the status of a feedback submission in Firestore."""
        try:
            doc_ref = self.db.collection('feedback').document(feedback_id)
            doc_ref.update({"status": status})
            logger.info(f"Updated feedback status {feedback_id} to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating feedback status: {e}")
            return False
    
    def update_story_share_token(self, story_id: str, share_token: str) -> bool:
        """Update a story's share token in Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc_ref.update({"share_token": share_token, "is_shareable": True})
            logger.info(f"Updated share token for story {story_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating share token: {e}")
            return False
    
    def get_story_by_share_token(self, share_token: str) -> Optional[Story]:
        """Get a story by its share token from Firestore."""
        try:
            stories_ref = self.db.collection('stories').where('share_token', '==', share_token).where('is_shareable', '==', True)
            docs = list(stories_ref.stream())
            
            if docs:
                story_data = docs[0].to_dict()
                story = Story(**story_data)
                logger.info(f"Retrieved shared story: {story.title}")
                return story
            else:
                logger.info(f"No story found with share token: {share_token}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving story by share token: {e}")
            return None

# Global instance
firebase_service = FirebaseService() 