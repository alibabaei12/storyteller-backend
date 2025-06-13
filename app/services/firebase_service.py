"""
Firebase service for database operations.
"""
import logging
import os
import json
import tempfile
import time
from typing import List, Dict, Optional

import firebase_admin
# Load environment variables
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

from ..models.models import Story, StoryMetadata, UserUsage, Feedback

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
            return
        except ValueError:
            # No app exists, create new one
            try:
                # First try: Use FIREBASE_CREDENTIALS environment variable (complete JSON)
                firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
                if firebase_creds_json:
                    try:
                        # Parse the JSON string to a dictionary
                        cred_dict = json.loads(firebase_creds_json)
                        
                        # Create a temporary file with the credentials
                        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                        json.dump(cred_dict, temp_file, indent=2)
                        temp_file.close()
                        temp_path = temp_file.name
                        
                        # Use the temporary file
                        cred = credentials.Certificate(temp_path)
                        firebase_admin.initialize_app(cred)
                        self._db = firestore.client()
                        
                        # Delete the temporary file
                        os.unlink(temp_path)
                        
                        logger.info(f"Initialized with FIREBASE_CREDENTIALS for project: {cred_dict.get('project_id')}")
                        return
                    except Exception as e:
                        logger.error(f"Error initializing with FIREBASE_CREDENTIALS: {e}")
                
                # Second try: Use individual credential fields
                firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                project_id = os.getenv('FIREBASE_PROJECT_ID')
                
                if firebase_private_key and firebase_client_email and project_id:
                    # Fix the private key format - ensure newlines are properly formatted
                    fixed_private_key = firebase_private_key
                    if '\\n' in fixed_private_key:
                        fixed_private_key = fixed_private_key.replace('\\n', '\n')
                    
                    # Create a direct credential object without using a file
                    cred_dict = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key": fixed_private_key,
                        "client_email": firebase_client_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    
                    try:
                        # Try direct initialization with the credential dict
                        cred = credentials.Certificate(cred_dict)
                        firebase_admin.initialize_app(cred)
                        self._db = firestore.client()
                        logger.info(f"Initialized with direct credentials for project: {project_id}")
                        return
                    except Exception as e:
                        logger.error(f"Error initializing with direct credentials: {e}")
                        # Continue to fallback method
                    
                    # If direct initialization failed, try with a temporary file
                    try:
                        # Create a more complete credential dict for the file
                        temp_cred_dict = {
                            "type": "service_account",
                            "project_id": project_id,
                            "private_key_id": f"temp_key_id_{int(time.time())}",  # Add timestamp to make it unique
                            "private_key": fixed_private_key,
                            "client_email": firebase_client_email,
                            "client_id": "",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email.replace('@', '%40')}"
                        }
                        
                        # Write to temporary file
                        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                        json.dump(temp_cred_dict, temp_file, indent=2)
                        temp_file.close()
                        temp_path = temp_file.name
                        
                        # Use the temporary file
                        cred = credentials.Certificate(temp_path)
                        firebase_admin.initialize_app(cred)
                        self._db = firestore.client()
                        
                        # Delete the temporary file
                        os.unlink(temp_path)
                        
                        logger.info(f"Initialized with temporary service account file for project: {project_id}")
                        return
                    except Exception as e:
                        logger.error(f"Error creating temporary service account file: {e}")
                
                # Fallback to default credentials
                try:
                    firebase_admin.initialize_app()
                    self._db = firestore.client()
                    logger.info("Initialized with default credentials")
                    return
                except Exception as e:
                    logger.error(f"Error initializing with default credentials: {e}")
                    raise ValueError("Failed to initialize Firebase with any available method")
                    
            except Exception as e:
                logger.error(f"Error initializing: {e}")
                logger.error("Make sure Firebase Admin SDK is properly configured")
                logger.error(f"FIREBASE_PROJECT_ID is set: {bool(os.getenv('FIREBASE_PROJECT_ID'))}")
                logger.error(f"FIREBASE_CLIENT_EMAIL is set: {bool(os.getenv('FIREBASE_CLIENT_EMAIL'))}")
                logger.error(f"FIREBASE_PRIVATE_KEY is set: {bool(os.getenv('FIREBASE_PRIVATE_KEY'))}")
                logger.error(f"FIREBASE_CREDENTIALS is set: {bool(os.getenv('FIREBASE_CREDENTIALS'))}")
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