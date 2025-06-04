from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4

class Choice(BaseModel):
    """A choice that the user can make in the story."""
    id: str
    text: str

class StoryNode(BaseModel):
    """A single node in the story with content and choices."""
    id: str
    content: str
    choices: List[Choice]
    parent_node_id: Optional[str] = None
    selected_choice_id: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class Story(BaseModel):
    """The main story object containing all nodes and metadata."""
    id: str = Field(default_factory=lambda: f"story_{int(datetime.now().timestamp())}_{uuid4().hex[:8]}")
    title: str
    character_name: str
    setting: str
    tone: str
    character_origin: str
    power_system: str
    cultivation_stage: Optional[str] = None
    current_node_id: str
    nodes: Dict[str, StoryNode]
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())

class StoryCreationParams(BaseModel):
    """Parameters for creating a new story."""
    character_name: str
    setting: str = "cultivation"
    tone: str = "optimistic"
    character_origin: str = "normal"
    power_system: str = "none"

class StoryMetadata(BaseModel):
    """Metadata about a story for listings."""
    id: str
    title: str
    character_name: str
    setting: str
    last_updated: float
    cultivation_stage: Optional[str] = None

class UserUsage:
    """Tracks a user's API usage."""
    
    def __init__(
        self,
        user_id: str,
        story_continuations_used: int = 0,
        story_continuations_limit: int = 20,
        last_reset_date: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.story_continuations_used = story_continuations_used
        self.story_continuations_limit = story_continuations_limit
        self.last_reset_date = last_reset_date or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "story_continuations_used": self.story_continuations_used,
            "story_continuations_limit": self.story_continuations_limit,
            "last_reset_date": self.last_reset_date.isoformat() if self.last_reset_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserUsage':
        """Create from dictionary."""
        last_reset = datetime.fromisoformat(data.get("last_reset_date")) if data.get("last_reset_date") else None
        
        return cls(
            user_id=data.get("user_id", ""),
            story_continuations_used=data.get("story_continuations_used", 0),
            story_continuations_limit=data.get("story_continuations_limit", 10),
            last_reset_date=last_reset
        )
    
    def can_continue_story(self) -> bool:
        """Check if user can continue a story based on current usage."""
        return self.story_continuations_used < self.story_continuations_limit
    
    def increment_usage(self) -> None:
        """Increment the story continuation usage counter."""
        self.story_continuations_used += 1
    
    def get_remaining_continuations(self) -> int:
        """Get the number of remaining story continuations."""
        return max(0, self.story_continuations_limit - self.story_continuations_used) 