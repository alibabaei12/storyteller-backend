import os
import json
from typing import Dict, Optional
from datetime import datetime
from .models import UserUsage

class UsageService:
    """Service for tracking and managing user usage limits."""
    
    def __init__(self, storage_dir: str = "data"):
        """Initialize the usage service with storage directory."""
        self.storage_dir = storage_dir
        self.usage_file = os.path.join(storage_dir, "user_usage.json")
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Ensure storage directory and files exist."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        if not os.path.exists(self.usage_file):
            with open(self.usage_file, "w") as f:
                json.dump({}, f)
    
    def _load_all_usage(self) -> Dict[str, UserUsage]:
        """Load all user usage data from storage."""
        try:
            with open(self.usage_file, "r") as f:
                data = json.load(f)
                return {user_id: UserUsage.from_dict({**usage_data, "user_id": user_id}) 
                        for user_id, usage_data in data.items()}
        except Exception as e:
            print(f"Error loading usage data: {e}")
            return {}
    
    def _save_all_usage(self, usage_data: Dict[str, UserUsage]) -> None:
        """Save all user usage data to storage."""
        try:
            serialized_data = {user_id: usage.to_dict() for user_id, usage in usage_data.items()}
            with open(self.usage_file, "w") as f:
                json.dump(serialized_data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage data: {e}")
    
    def get_user_usage(self, user_id: str) -> UserUsage:
        """Get usage data for a specific user, creating if it doesn't exist."""
        all_usage = self._load_all_usage()
        if user_id not in all_usage:
            all_usage[user_id] = UserUsage(user_id=user_id)
            self._save_all_usage(all_usage)
        
        return all_usage[user_id]
    
    def increment_story_continuation(self, user_id: str) -> bool:
        """
        Increment story continuation count for a user.
        Returns True if successful (under limit), False if limit reached.
        """
        all_usage = self._load_all_usage()
        usage = all_usage.get(user_id, UserUsage(user_id=user_id))
        
        if not usage.can_continue_story():
            return False
        
        usage.increment_usage()
        all_usage[user_id] = usage
        self._save_all_usage(all_usage)
        return True
    
    def get_remaining_continuations(self, user_id: str) -> int:
        """Get remaining story continuations for a user."""
        usage = self.get_user_usage(user_id)
        return usage.get_remaining_continuations()
    
    def reset_usage(self, user_id: str) -> None:
        """Reset usage for a user (admin function)."""
        all_usage = self._load_all_usage()
        if user_id in all_usage:
            all_usage[user_id] = UserUsage(user_id=user_id)
            self._save_all_usage(all_usage)
    
    def update_limit(self, user_id: str, new_limit: int) -> None:
        """Update the continuation limit for a user (for premium users)."""
        all_usage = self._load_all_usage()
        usage = all_usage.get(user_id, UserUsage(user_id=user_id))
        usage.story_continuations_limit = new_limit
        all_usage[user_id] = usage
        self._save_all_usage(all_usage) 