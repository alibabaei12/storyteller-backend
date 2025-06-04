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
    tone: str = "adventure"
    character_origin: str = "normal"
    power_system: str = "qi"

class StoryMetadata(BaseModel):
    """Metadata about a story for listings."""
    id: str
    title: str
    character_name: str
    setting: str
    last_updated: float
    cultivation_stage: Optional[str] = None 