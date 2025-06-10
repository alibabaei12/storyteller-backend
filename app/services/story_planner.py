"""
Story planning utilities for generating story goals and arcs.
"""
import logging
import random
import re
from typing import List, Optional, Any

# Set up logger
logger = logging.getLogger(__name__)

# Arc pool for various big story goal themes
arc_pool = {
    "revenge": [
        "Take the sect entrance exam and earn qualification.",
        "Survive the sect's brutal outer disciple training.",
        "Win the internal sect tournament to rise in rank.",
        "Investigate rumors about the betrayer's past.",
        "Challenge an inner disciple to gain attention.",
        "Explore the forbidden grounds near the sect.",
        "Uncover a hidden traitor among sect elders.",
        "Rescue a captured ally from a rival sect.",
        "Gain the title of Core Disciple.",
        "Hunt for a forbidden technique sealed by ancient cultivators."
    ],
    "immortality": [
        "Master the Foundation Building stage.",
        "Find and decode ancient cultivation manuals.",
        "Survive the life-and-death trials of the inner disciples.",
        "Unlock latent talents through forbidden sect trials.",
        "Train under a mysterious hidden master.",
        "Discover an ancient relic said to lead to immortality.",
        "Face a Heart Demon Trial.",
        "Create a unique cultivation technique.",
        "Form a Pillar of Dao to stabilize cultivation.",
        "Enter the secret realm opened once every century."
    ],
    "past_life": [
        "Recover fragmented memories from a past life.",
        "Seek remnants of past life treasures.",
        "Battle old enemies who once defeated you.",
        "Uncover the secrets behind your past death.",
        "Rebuild your lost cultivation base.",
        "Reclaim the title once held in your past life.",
        "Unravel hidden betrayals from your old allies.",
        "Find your past life's inheritance trial.",
        "Create a new sect inspired by your former life.",
        "Face the clan that destroyed your old self."
    ],
    "unite_martial_clans": [
        "Travel to different sects and clans to build alliances.",
        "Survive assassination attempts from rival clans.",
        "Prove your strength in inter-sect tournaments.",
        "Unite small sects under your banner through diplomacy or duels.",
        "Discover ancient clan relics needed for unity.",
        "Expose corruption inside the leading martial sects.",
        "Save a declining sect to gain loyalty.",
        "Defeat rival clan leaders in open duels.",
        "Establish your own martial alliance.",
        "Challenge the council of elders from various sects."
    ],
    "recover_legendary_artifact": [
        "Decode ancient maps pointing to the artifact.",
        "Survive forbidden secret realm trials.",
        "Battle rival treasure hunters.",
        "Find and protect artifact guardians.",
        "Defeat ancient beasts guarding the artifact.",
        "Solve the riddles of ancient cultivators.",
        "Fight through illusion arrays protecting the artifact.",
        "Gather scattered relic fragments across territories.",
        "Unlock the artifact's hidden powers step-by-step.",
        "Face an ancient sect that claims ownership of the artifact."
    ]
}

def generate_big_story_goal(setting: str) -> str:
    """
    Generate a big story goal based on the setting.
    
    Args:
        setting: The story setting (e.g., "cultivation_progression")
        
    Returns:
        A randomly selected big story goal appropriate for the setting
    """
    if setting == "cultivation":
        goals = [
            "Revenge on the Sect Leader who betrayed their family.",
            "Seek immortality and uncover ancient cultivation secrets.",
            "Regain lost memories from a past life.",
            "Unite the fractured martial clans under one rule.",
            "Recover the legendary artifact sealed by ancient cultivators."
        ]
        return random.choice(goals)
    return "Become the strongest cultivator."

def generate_new_arc_goal(big_story_goal: str, arc_history: List[str]) -> str:
    """
    Generate a new story arc goal based on the big story goal theme.
    
    Args:
        big_story_goal: The main character's long-term goal
        arc_history: List of previously completed arc goals
        
    Returns:
        A new story arc goal that hasn't been used recently
    """
    theme = ""
    if "revenge" in big_story_goal.lower():
        theme = "revenge"
    elif "immortality" in big_story_goal.lower():
        theme = "immortality"
    elif "past life" in big_story_goal.lower():
        theme = "past_life"
    elif "unite" in big_story_goal.lower():
        theme = "unite_martial_clans"
    elif "artifact" in big_story_goal.lower():
        theme = "recover_legendary_artifact"
    else:
        # Default to revenge if no match found
        theme = "revenge"
        logger.info(f"No matching theme found for goal: '{big_story_goal}', defaulting to 'revenge'")
    
    pool = arc_pool.get(theme, [])
    # Filter out arcs already used recently
    available_arcs = [arc for arc in pool if arc not in arc_history]
    if not available_arcs:
        logger.info(f"All arcs for theme '{theme}' have been used, resetting pool")
        available_arcs = pool  # Reset if exhausted
    
    new_arc = random.choice(available_arcs)
    logger.info(f"Generated new arc goal: '{new_arc}' for theme: '{theme}'")
    return new_arc

def add_character_to_memory(memory: Any, name: str, relationship: str, sect: Optional[str] = None, role: Optional[str] = None) -> Any:
    """
    Add or update a character in the story memory.
    
    Args:
        memory: The StoryMemory object to update
        name: The character's name
        relationship: The character's relationship to the protagonist
        sect: The character's sect or organization (optional)
        role: The character's role or position (optional)
        
    Returns:
        The updated StoryMemory object
        
    Validation:
        - Rejects empty or very short names (< 2 chars)
        - Rejects names with non-alphabetic characters
        - Updates existing characters rather than creating duplicates
    """
    # Validate inputs
    if not name or not isinstance(name, str) or len(name) < 2:
        logger.warning(f"Invalid character name: '{name}' - too short or empty")
        return memory
    
    # Check if name contains mostly alphabetic characters (allow spaces)
    if not re.match(r'^[A-Za-z\s]+$', name) or name.isspace():
        logger.warning(f"Invalid character name: '{name}' - contains invalid characters")
        return memory
        
    # Common names that might be used incorrectly
    common_words = ["The", "And", "But", "This", "That", "Where", "When", "Who", "What", "Why", "How"]
    if name in common_words:
        logger.warning(f"Rejected common word as character name: '{name}'")
        return memory
    
    # Validate relationship
    if not relationship or not isinstance(relationship, str) or len(relationship) < 2:
        logger.warning(f"Invalid relationship: '{relationship}' - too short or empty")
        return memory
    
    # Validate sect if provided
    if sect is not None and (not isinstance(sect, str) or len(sect) < 2):
        logger.warning(f"Invalid sect: '{sect}' - too short or empty")
        sect = None
    
    # Validate role if provided
    if role is not None and (not isinstance(role, str) or len(role) < 2):
        logger.warning(f"Invalid role: '{role}' - too short or empty")
        role = None
    
    # Initialize characters list if needed
    if not hasattr(memory, 'characters') or memory.characters is None:
        # Import here to avoid circular imports
        from ..models.models import Character
        memory.characters = []
    
    # Import Character class
    from ..models.models import Character
    
    # Avoid duplicates — check if character already exists
    existing_char = None
    for i, character in enumerate(memory.characters):
        if character.name == name:
            existing_char = character
            # Remove from list to replace with updated version
            memory.characters.pop(i)
            break
    
    # If character exists, update with new info
    if existing_char:
        logger.info(f"Updating character: {name}")
        
        # Only update fields if new values are provided
        if relationship:
            existing_char.relationship = relationship
        if sect:
            existing_char.sect = sect
        if role:
            existing_char.role = role
        
        # Add updated character back to list
        memory.characters.append(existing_char)
    else:
        # Create and add new character
        logger.info(f"Adding new character: {name} ({relationship})")
        new_char = Character(
            name=name,
            relationship=relationship,
            sect=sect,
            role=role
        )
        memory.characters.append(new_char)
    
    return memory 