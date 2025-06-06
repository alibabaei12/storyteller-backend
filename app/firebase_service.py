import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from typing import List, Optional, Dict, Any
from .models import Story, StoryNode, StoryMetadata, UserUsage

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


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
            print("[Firebase] Using existing Firebase app")
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
                    print(f"[Firebase] Initialized with environment credentials for project: {project_id}")
                    
                elif cred_path and os.path.exists(cred_path):
                    # Development: Use service account file
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {'projectId': project_id})
                    self._db = firestore.client()
                    print(f"[Firebase] Initialized with service account file: {cred_path}")
                    
                else:
                    # Fallback to default credentials
                    firebase_admin.initialize_app()
                    self._db = firestore.client()
                    print("[Firebase] Initialized with default credentials")
            except Exception as e:
                print(f"[Firebase] Error initializing: {e}")
                print("[Firebase] Make sure Firebase Admin SDK is properly configured")
                print(f"[Firebase] GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
                print(f"[Firebase] File exists: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))}")
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
            
            print(f"[Firebase] Saved story {story.id}: {story.title}")
        except Exception as e:
            print(f"[Firebase] Error saving story: {e}")
            raise
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Get a story by ID from Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc = doc_ref.get()
            
            if doc.exists:
                story_data = doc.to_dict()
                story = Story(**story_data)
                print(f"[Firebase] Retrieved story {story_id}: {story.title}")
                return story
            else:
                print(f"[Firebase] Story not found: {story_id}")
                return None
        except Exception as e:
            print(f"[Firebase] Error retrieving story: {e}")
            return None
    
    def delete_story(self, story_id: str) -> bool:
        """Delete a story from Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc_ref.delete()
            print(f"[Firebase] Deleted story {story_id}")
            return True
        except Exception as e:
            print(f"[Firebase] Error deleting story: {e}")
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
            
            print(f"[Firebase] Retrieved {len(metadata_list)} stories")
            return metadata_list
        except Exception as e:
            print(f"[Firebase] Error retrieving all stories: {e}")
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
            
            print(f"[Firebase] Retrieved {len(metadata_list)} stories for user {user_id}")
            return metadata_list
        except Exception as e:
            print(f"[Firebase] Error retrieving user stories: {e}")
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
            print(f"[Firebase] Error retrieving user usage: {e}")
            return None
    
    def save_user_usage(self, usage: UserUsage) -> None:
        """Save user usage data to Firestore."""
        try:
            doc_ref = self.db.collection('usage').document(usage.user_id)
            doc_ref.set(usage.to_dict())
            print(f"[Firebase] Saved usage for user {usage.user_id}")
        except Exception as e:
            print(f"[Firebase] Error saving user usage: {e}")
            raise
    
    def get_all_user_usage(self) -> Dict[str, UserUsage]:
        """Get all user usage data from Firestore."""
        try:
            usage_ref = self.db.collection('usage')
            docs = usage_ref.stream()
            
            usage_dict = {}
            for doc in docs:
                usage_data = doc.to_dict()
                user_id = doc.id
                usage_dict[user_id] = UserUsage.from_dict(usage_data)
            
            print(f"[Firebase] Retrieved usage data for {len(usage_dict)} users")
            return usage_dict
        except Exception as e:
            print(f"[Firebase] Error retrieving all user usage: {e}")
            return {}

    # Share token operations
    def update_story_share_token(self, story_id: str, share_token: str) -> bool:
        """Update a story's share token in Firestore."""
        try:
            doc_ref = self.db.collection('stories').document(story_id)
            doc_ref.update({
                'share_token': share_token,
                'is_shareable': True
            })
            print(f"[Firebase] Updated share token for story {story_id}")
            return True
        except Exception as e:
            print(f"[Firebase] Error updating share token: {e}")
            return False

    def get_story_by_share_token(self, share_token: str) -> Optional[Story]:
        """Get a story by its share token from Firestore."""
        try:
            stories_ref = self.db.collection('stories').where('share_token', '==', share_token)
            docs = list(stories_ref.stream())
            
            if docs:
                story_data = docs[0].to_dict()
                story = Story(**story_data)
                print(f"[Firebase] Retrieved shared story {story.id}: {story.title}")
                return story
            else:
                print(f"[Firebase] No shared story found for token: {share_token}")
                return None
        except Exception as e:
            print(f"[Firebase] Error retrieving shared story: {e}")
            return None


# Global Firebase service instance
firebase_service = FirebaseService() 