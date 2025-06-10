import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Choice(BaseModel):
    """A choice that the user can make in the story."""
    id: str
    text: str

class Character(BaseModel):
    """A character in the story with relationship to the protagonist."""
    name: str
    relationship: str  # e.g., Ally, Enemy, Rival, Mentor
    sect: Optional[str] = None  # e.g., Azure Cloud Sect
    role: Optional[str] = None  # e.g., Outer Disciple, Elder

class StoryMemory(BaseModel):
    """Memory system for storing and retrieving story context and state."""
    character_name: str
    character_gender: str = "unspecified"
    character_origin: str = "ordinary"
    setting: str
    story_nodes: List[str] = Field(default_factory=list)  # IDs of nodes in chronological order
    character_traits: Dict[str, Any] = Field(default_factory=dict)
    locations: Dict[str, Any] = Field(default_factory=dict)
    supporting_characters: Dict[str, Any] = Field(default_factory=dict)
    important_items: Dict[str, Any] = Field(default_factory=dict)
    story_day: int = 1  # Day in the story timeline
    cultivation_stage: Optional[str] = None
    current_arc: Optional[str] = None
    big_story_goal: Optional[str] = None  # Main character's long-term goal (e.g., revenge, immortality, reclaim power)
    characters: List[Character] = Field(default_factory=list)  # List of characters with relationships
    current_arc_goal: Optional[str] = None  # Current story arc goal
    arc_history: List[str] = Field(default_factory=list)  # List of completed story arcs

class StoryNode(BaseModel):
    """A single node in the story with content and choices."""
    id: str
    content: str
    choices: List[Choice]
    parent_node_id: Optional[str] = None
    selected_choice_id: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: time.time())

class Story(BaseModel):
    """The main story object containing all nodes and metadata."""
    id: str = Field(default_factory=lambda: f"story_{int(time.time())}_{uuid4().hex[:8]}")
    title: str
    character_name: str
    character_gender: str = "unspecified"
    setting: str
    tone: str
    character_origin: str
    nodes: Dict[str, StoryNode]
    current_node_id: str
    last_updated: float = Field(default_factory=lambda: time.time())
    # Internal fields that aren't directly set by users
    power_system: str = "auto"
    cultivation_stage: Optional[str] = None
    # User identification
    user_id: Optional[str] = None
    # Public sharing
    share_token: Optional[str] = None
    is_shareable: bool = False
    # Story memory system
    memory: Optional[StoryMemory] = None
    # Main character's long-term goal
    big_story_goal: Optional[str] = None

class StoryCreationParams(BaseModel):
    """Parameters for creating a new story."""
    character_name: str
    character_gender: str = "unspecified"
    setting: str = "cultivation"
    tone: str = "optimistic"
    character_origin: str = "ordinary"
    user_id: Optional[str] = None

class StoryMetadata(BaseModel):
    """Metadata about a story for listings."""
    id: str
    title: str
    character_name: str
    setting: str
    last_updated: float
    cultivation_stage: Optional[str] = None
    user_id: Optional[str] = None

class UserUsage(BaseModel):
    """Tracks a user's API usage."""
    user_id: str
    story_continuations_used: int = 0
    story_continuations_limit: int = 25  # Free tier limit
    stories_created_this_month: int = 0
    stories_created_limit: int = 5  # Free tier limit
    last_reset_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "story_continuations_used": self.story_continuations_used,
            "story_continuations_limit": self.story_continuations_limit,
            "stories_created_this_month": self.stories_created_this_month,
            "stories_created_limit": self.stories_created_limit,
            "last_reset_date": self.last_reset_date.isoformat() if self.last_reset_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserUsage':
        """Create from dictionary."""
        last_reset_data = data.get("last_reset_date")
        last_reset = None
        
        if last_reset_data:
            if isinstance(last_reset_data, str):
                try:
                    last_reset = datetime.fromisoformat(last_reset_data)
                except ValueError:
                    # Fallback to current datetime if parsing fails
                    last_reset = datetime.now(timezone.utc)
            elif isinstance(last_reset_data, datetime):
                last_reset = last_reset_data
            else:
                last_reset = datetime.now(timezone.utc)
        else:
            last_reset = datetime.now(timezone.utc)
        
        return cls(
            user_id=data.get("user_id", ""),
            story_continuations_used=data.get("story_continuations_used", 0),
            story_continuations_limit=data.get("story_continuations_limit", 25),
            stories_created_this_month=data.get("stories_created_this_month", 0),
            stories_created_limit=data.get("stories_created_limit", 5),
            last_reset_date=last_reset
        )
    
    def can_continue_story(self) -> bool:
        """Check if user can continue a story based on current usage."""
        # For infinite stories, we still use the regular limits
        return self.story_continuations_used < self.story_continuations_limit
    
    def increment_usage(self) -> None:
        """Increment the story continuation usage counter."""
        self.story_continuations_used += 1
    
    def get_remaining_continuations(self) -> int:
        """Get the number of remaining story continuations."""
        return max(0, self.story_continuations_limit - self.story_continuations_used)

class Feedback(BaseModel):
    """User feedback model."""
    id: str
    user_id: str
    feedback_type: str  # 'bug', 'feature', 'general'
    message: str  # max 500 chars
    contact_email: str = ""
    status: str = "open"  # 'open', 'resolved', 'spam'
    created_at: str = ""
    
class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    feedback_type: str
    message: str
    contact_email: str = "" 