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
                    story_continuations_limit=20,  # Default limit
                    last_reset_date=datetime.now().isoformat()
                )
                # Save the new usage record
                firebase_service.save_user_usage(usage)
                print(f"[Usage] Created new usage record for user: {user_id}")
            
            return usage
        except Exception as e:
            print(f"[Usage] Error getting user usage: {e}")
            # Return default usage as fallback
            return UserUsage(
                user_id=user_id,
                story_continuations_used=0,
                story_continuations_limit=20,
                last_reset_date=datetime.now().isoformat()
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
    
    def reset_daily_limits(self, user_id: str) -> None:
        """Reset daily limits for a user (for admin use)."""
        try:
            usage = self.get_user_usage(user_id)
            usage.story_continuations_used = 0
            usage.last_reset_date = datetime.now().isoformat()
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