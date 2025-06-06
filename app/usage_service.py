import os
import json
from typing import Dict, Optional
from datetime import datetime
from .models import UserUsage
from .firebase_service import firebase_service

class UsageService:
    """Service for tracking and managing user usage limits using Firebase."""
    
    def __init__(self, storage_dir: str = "data"):
        """Initialize the usage service."""
        # Note: storage_dir parameter kept for backward compatibility but not used
        pass
    
    def get_user_usage(self, user_id: str) -> UserUsage:
        """Get usage data for a specific user from Firebase."""
        try:
            usage = firebase_service.get_user_usage(user_id)
            
            if usage is None:
                # Create new usage record for new user
                usage = UserUsage(
                    user_id=user_id,
                    story_continuations_used=0,
                    story_continuations_limit=25,  # Free tier limit
                    stories_created_this_month=0,
                    stories_created_limit=5,  # Free tier limit
                    last_reset_date=datetime.now()
                )
                # Save the new usage record
                firebase_service.save_user_usage(usage)
                print("[Usage] Created new usage record")
            else:
                # Migrate existing users to include new fields
                if not hasattr(usage, 'stories_created_this_month'):
                    # Count existing stories created this month
                    from .storage import get_user_stories
                    from datetime import datetime
                    
                    user_stories = get_user_stories(user_id)
                    current_month_stories = 0
                    
                    for story_meta in user_stories:
                        # Check if story was created this month (use created_at if available, fallback to last_updated)
                        try:
                            if hasattr(story_meta, 'created_at') and story_meta.created_at:
                                # Parse the ISO date string
                                story_date = datetime.fromisoformat(story_meta.created_at.replace('Z', '+00:00'))
                            else:
                                # Fallback to last_updated timestamp
                                story_date = datetime.fromtimestamp(story_meta.last_updated)
                            
                            if (story_date.year == datetime.now().year and 
                                story_date.month == datetime.now().month):
                                current_month_stories += 1
                                print(f"[Usage] Found story from this month: {story_meta.title} created on {story_date}")
                        except Exception as e:
                            print(f"[Usage] Error parsing date for story {story_meta.title}: {e}")
                            # Skip this story in count to be safe
                    
                    usage.stories_created_this_month = current_month_stories
                    usage.stories_created_limit = 5
                    firebase_service.save_user_usage(usage)
                    print(f"[Usage] Migrated user: found {current_month_stories} stories this month")
            
            return usage
        except Exception as e:
            print(f"[Usage] Error getting user usage: {e}")
            # Return default usage as fallback
            return UserUsage(
                user_id=user_id,
                story_continuations_used=0,
                story_continuations_limit=25,  # Free tier limit
                stories_created_this_month=0,
                stories_created_limit=5,  # Free tier limit
                last_reset_date=datetime.now()
            )
    
    def update_user_usage(self, user_id: str, usage: UserUsage) -> None:
        """Update usage data for a specific user in Firebase."""
        try:
            firebase_service.save_user_usage(usage)
            print(f"[Usage] Updated usage for user: {user_id}")
        except Exception as e:
            print(f"[Usage] Error updating user usage: {e}")
            raise
    
    def increment_story_continuations(self, user_id: str) -> UserUsage:
        """Increment story continuations count for a user."""
        try:
            usage = self.get_user_usage(user_id)
            usage.story_continuations_used += 1
            self.update_user_usage(user_id, usage)
            return usage
        except Exception as e:
            print(f"[Usage] Error incrementing story continuations: {e}")
            raise
    
    def can_continue_story(self, user_id: str) -> bool:
        """Check if user can continue stories (hasn't reached limit)."""
        try:
            usage = self.get_user_usage(user_id)
            return usage.story_continuations_used < usage.story_continuations_limit
        except Exception as e:
            print(f"[Usage] Error checking story continuation limit: {e}")
            return False  # Conservative approach - deny if error
    
    def get_remaining_continuations(self, user_id: str) -> int:
        """Get number of remaining story continuations for a user."""
        try:
            usage = self.get_user_usage(user_id)
            remaining = usage.story_continuations_limit - usage.story_continuations_used
            return max(0, remaining)  # Ensure non-negative
        except Exception as e:
            print(f"[Usage] Error getting remaining continuations: {e}")
            return 0  # Conservative approach
    
    def can_create_story(self, user_id: str) -> bool:
        """Check if user can create new stories (hasn't reached limit)."""
        try:
            # Auto-correct usage count by recounting actual stories
            self._auto_correct_usage(user_id)
            
            usage = self.get_user_usage(user_id)
            stories_created = getattr(usage, 'stories_created_this_month', 0)
            stories_limit = getattr(usage, 'stories_created_limit', 5)
            return stories_created < stories_limit
        except Exception as e:
            print(f"[Usage] Error checking story creation limit: {e}")
            return False  # Conservative approach - deny if error
    
    def increment_stories_created(self, user_id: str) -> UserUsage:
        """Increment stories created count for a user."""
        try:
            usage = self.get_user_usage(user_id)
            usage.stories_created_this_month += 1
            self.update_user_usage(user_id, usage)
            return usage
        except Exception as e:
            print(f"[Usage] Error incrementing stories created: {e}")
            raise
    
    def decrement_stories_created(self, user_id: str) -> UserUsage:
        """Decrement stories created count for a user (when a story is deleted)."""
        try:
            usage = self.get_user_usage(user_id)
            # Ensure we don't go below 0
            usage.stories_created_this_month = max(0, usage.stories_created_this_month - 1)
            self.update_user_usage(user_id, usage)
            print(f"[Usage] Decremented stories created for user {user_id}: {usage.stories_created_this_month}")
            return usage
        except Exception as e:
            print(f"[Usage] Error decrementing stories created: {e}")
            raise
    
    def get_remaining_stories(self, user_id: str) -> int:
        """Get number of remaining stories user can create this month."""
        try:
            usage = self.get_user_usage(user_id)
            remaining = usage.stories_created_limit - usage.stories_created_this_month
            return max(0, remaining)  # Ensure non-negative
        except Exception as e:
            print(f"[Usage] Error getting remaining stories: {e}")
            return 0  # Conservative approach
    
    def _auto_correct_usage(self, user_id: str) -> None:
        """Auto-correct usage count by recounting actual current stories."""
        try:
            from .storage import get_user_stories
            user_stories = get_user_stories(user_id)
            
            # Count current month stories manually
            current_month_stories = 0
            now = datetime.now()
            
            for story_meta in user_stories:
                try:
                    if hasattr(story_meta, 'created_at') and story_meta.created_at:
                        story_date = datetime.fromisoformat(story_meta.created_at.replace('Z', '+00:00'))
                    else:
                        story_date = datetime.fromtimestamp(story_meta.last_updated)
                    
                    if (story_date.year == now.year and story_date.month == now.month):
                        current_month_stories += 1
                except Exception as e:
                    print(f"[Usage] Error parsing story date: {e}")
            
            # Update usage if different
            usage = firebase_service.get_user_usage(user_id)
            if usage and hasattr(usage, 'stories_created_this_month'):
                if usage.stories_created_this_month != current_month_stories:
                    print(f"[Usage] Auto-correcting count for {user_id}: {usage.stories_created_this_month} -> {current_month_stories}")
                    usage.stories_created_this_month = current_month_stories
                    firebase_service.save_user_usage(usage)
        except Exception as e:
            print(f"[Usage] Error in auto-correction: {e}")

    def reset_daily_limits(self, user_id: str) -> None:
        """Reset daily limits for a user (for admin use)."""
        try:
            usage = self.get_user_usage(user_id)
            usage.story_continuations_used = 0
            usage.last_reset_date = datetime.now()
            self.update_user_usage(user_id, usage)
            print(f"[Usage] Reset daily limits for user: {user_id}")
        except Exception as e:
            print(f"[Usage] Error resetting daily limits: {e}")
            raise
    
    # Legacy methods for backward compatibility
    def _load_all_usage(self) -> Dict[str, UserUsage]:
        """Load all user usage data (legacy method - now uses Firebase)."""
        try:
            return firebase_service.get_all_user_usage()
        except Exception as e:
            print(f"[Usage] Error loading all usage data: {e}")
            return {}
    
    def _save_all_usage(self, usage_data: Dict[str, UserUsage]) -> None:
        """Save all user usage data (legacy method - now saves to Firebase)."""
        try:
            for user_id, usage in usage_data.items():
                firebase_service.save_user_usage(usage)
        except Exception as e:
            print(f"[Usage] Error saving all usage data: {e}")


# Global usage service instance
usage_service = UsageService() 