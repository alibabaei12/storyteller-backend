"""
Story planning utilities for generating story goals and arcs.
"""
import logging
import random
import re
from typing import List, Optional, Any, Dict, Tuple

# Set up logger
logger = logging.getLogger(__name__)

# Story goals and their associated arcs for cultivation stories
cultivation_story_templates = [
    {
        "goal": "Climb from the weakest rank to the peak of cultivation in order to defeat the powerful enemies who destroyed your family and bring justice to those who wronged you.",
        "theme": "revenge",
        "arcs": [
            "Train under a secret master to recover lost cultivation talent and begin your path to power.",
            "Defeat a rival in a public duel to restore your family's honor.",
            "Obtain a rare heavenly flame or artifact to advance rapidly.",
            "Join a prestigious academy or sect and prove yourself through deadly tournaments.",
            "Return to your homeland to save your family and battle invaders.",
            "Rescue your captured master or loved ones from an enemy faction.",
            "Unite multiple clans or factions by winning a national tournament.",
            "Confront and defeat the enemy sect responsible for your family's destruction.",
            "Unlock a hidden realm or inheritance that boosts your cultivation to a new level.",
            "Challenge the leaders of your world in a final battle to bring justice and peace."
        ]
    },
    {
        "goal": "Use your knowledge of a tragic future life to change fate, protect your loved ones, and prevent the fall of your world.",
        "theme": "past_life",
        "arcs": [
            "Rebuild your strength quickly by using knowledge from your past life.",
            "Strengthen your family's influence by introducing new techniques.",
            "Recruit young talents to form a powerful alliance early.",
            "Expose a traitor within your sect or city before they can cause harm.",
            "Explore ancient ruins or secret realms to gain rare items and power.",
            "Defend your city or sect from an overwhelming beast or enemy army.",
            "Travel to higher realms and train under powerful masters.",
            "Unite sects across realms to prepare for a coming catastrophe.",
            "Confront the supreme evil responsible for the world's collapse.",
            "Break the cycle of destruction and lead your realm into a new era."
        ]
    },
    {
        "goal": "Pursue the path to true immortality and enlightenment by mastering the Dao and ascending beyond mortal limits.",
        "theme": "immortality",
        "arcs": [
            "Awaken a hidden talent or unique physique suited for high cultivation.",
            "Join a powerful sect and pass its harsh entrance trials.",
            "Build your foundation by mastering elemental or spiritual techniques.",
            "Enter forbidden lands to find ancient knowledge or sacred manuals.",
            "Learn alchemy, talisman crafting, or artifact forging to support your cultivation.",
            "Overcome an inner demon trial to break through a bottleneck.",
            "Comprehend the Dao in seclusion or under a natural phenomenon.",
            "Survive a heavenly tribulation to ascend to a higher plane.",
            "Compete in divine tournaments to secure a place among immortals.",
            "Confront a divine guardian to reach the final stage of transcendence."
        ]
    },
    {
        "goal": "Unite the martial world under your leadership and create a new era of peace and strength.",
        "theme": "unite_martial_clans",
        "arcs": [
            "Travel to distant sects and win their allegiance through duels or diplomacy.",
            "Expose corruption in a dominant sect or alliance.",
            "Save a declining clan and gain loyal allies.",
            "Defeat rogue factions threatening balance in the martial world.",
            "Survive assassination attempts sent by rival powers.",
            "Win a grand martial tournament to earn the right to lead.",
            "Form your own powerful sect and recruit elite disciples.",
            "Resist political sabotage and internal betrayal.",
            "Challenge the council of sect leaders to prove your vision.",
            "Establish a united alliance and gain recognition from the heavens."
        ]
    },
    {
        "goal": "Recover a legendary artifact sealed by ancient cultivators to gain its immense power and reshape the world.",
        "theme": "recover_legendary_artifact",
        "arcs": [
            "Find an ancient map or clue leading to the artifact's location.",
            "Survive secret realm trials that guard the artifact's path.",
            "Battle rival treasure hunters seeking the same artifact.",
            "Solve ancient puzzles or tests left by powerful cultivators.",
            "Defeat a powerful beast or guardian spirit bound to the artifact.",
            "Gather lost fragments of the artifact scattered across regions.",
            "Unlock the artifact's powers step by step through blood, Qi, or soul.",
            "Resist the artifact's will or backlash that tests your mind and heart.",
            "Fight a sect that claims ancestral rights over the artifact.",
            "Fuse with or master the artifact, transforming your cultivation path."
        ]
    },
    {
        "goal": "Awaken the memories and powers of your past life to reclaim your former glory and settle unfinished karma.",
        "theme": "past_life",
        "arcs": [
            "Recover fragments of your past memories through dreams or relics.",
            "Unlock sealed cultivation techniques left by your former self.",
            "Confront former enemies who still walk the world.",
            "Visit ancient tombs or ruins tied to your past identity.",
            "Unravel mysteries around your past death or betrayal.",
            "Stop impersonators or rivals claiming your legacy.",
            "Rebuild the sect or empire you once led.",
            "Fuse your current and past cultivation paths to ascend.",
            "Face judgment from cosmic forces punishing reincarnation cheats.",
            "Transcend your past and reshape your own destiny anew."
        ]
    },
    {
        "goal": "Forge a unique cultivation path rejected by the world, overcoming divine resistance to prove your Dao is supreme.",
        "theme": "unique_dao",
        "arcs": [
            "Be rejected by major sects for having no potential or a forbidden path.",
            "Discover or invent an unconventional cultivation method.",
            "Practice your technique in secret while deceiving others.",
            "Survive backlash from heaven or the sect after revealing your path.",
            "Attract disciples who believe in your method.",
            "Battle orthodox cultivators who try to suppress your progress.",
            "Create your own cultivation manual or philosophy.",
            "Fuse Dao concepts to gain enlightenment beyond traditional realms.",
            "Challenge the heavens or divine guardians defending the status quo.",
            "Be recognized as a Dao pioneer and reshape cultivation forever."
        ]
    },
    {
        "goal": "Protect someone dear to you by becoming strong enough that no force in the world can ever threaten them again.",
        "theme": "protection",
        "arcs": [
            "Start with a peaceful life that's shattered by loss or illness.",
            "Search for a rare herb, cure, or technique to save your loved one.",
            "Enter a forbidden zone or beast forest under time pressure.",
            "Negotiate with sects or alchemists who control the cure.",
            "Sacrifice part of your cultivation to trade for their life.",
            "Train under a master or sect to gain strength for protection.",
            "Rescue them from a kidnapping or spiritual possession.",
            "Lose them once and pursue a path of resurrection.",
            "Defy karma or the underworld to retrieve their soul.",
            "Create a peaceful haven where no one can threaten your bond."
        ]
    }
]

# Map themes to their story templates for quick lookup
theme_to_templates = {}

# Initialize the theme mapping
for template in cultivation_story_templates:
    theme = template["theme"]
    if theme not in theme_to_templates:
        theme_to_templates[theme] = []
    theme_to_templates[theme].append(template)

def generate_big_story_goal(setting: str) -> str:
    """
    Generate a big story goal based on the setting.
    
    Args:
        setting: The story setting (e.g., "cultivation")
        
    Returns:
        A randomly selected big story goal appropriate for the setting
    """
    if setting == "cultivation":
        # Randomly select a story template
        template = random.choice(cultivation_story_templates)
        return template["goal"]
    return "Become the strongest cultivator."

def generate_new_arc_goal(big_story_goal: str, arc_history: List[str], num_arcs: int = None) -> List[str]:
    """
    Generate multiple new story arc goals based on the big story goal theme.
    
    Args:
        big_story_goal: The main character's long-term goal
        arc_history: List of previously completed arc goals
        num_arcs: Number of arc goals to generate (if None, will calculate based on total chapters)
        
    Returns:
        A list of new story arc goals that haven't been used recently
    """
    # Import here to avoid circular imports
    from ..models.models import StoryMemory
    
    # If num_arcs is not provided, calculate it based on total chapters
    if num_arcs is None:
        # Get default values from StoryMemory
        default_memory = StoryMemory(character_name="", setting="")
        total_chapters_planned = default_memory.total_chapters_planned
        chapters_per_arc = default_memory.chapters_per_arc  # Use the value from StoryMemory
        num_arcs = max(3, round(total_chapters_planned / chapters_per_arc))
        logger.info(f"Calculated number of arcs: {num_arcs} based on {total_chapters_planned} chapters and {chapters_per_arc} chapters per arc")

    # Find matching theme and templates
    matching_templates = []
    
    # Look for exact match in goals first
    for template in cultivation_story_templates:
        if template["goal"] == big_story_goal:
            matching_templates = [template]
            logger.info(f"Found exact match for goal: '{big_story_goal}'")
            break
    
    # If no exact match, try to identify theme from keywords
    if not matching_templates:
        theme = ""
        if "revenge" in big_story_goal.lower() or "justice" in big_story_goal.lower() or "destroy" in big_story_goal.lower() or "avenge" in big_story_goal.lower():
            theme = "revenge"
        elif "immortality" in big_story_goal.lower() or "enlightenment" in big_story_goal.lower() or "ascend" in big_story_goal.lower():
            theme = "immortality"
        elif "past life" in big_story_goal.lower() or "reincarnation" in big_story_goal.lower() or "memories" in big_story_goal.lower():
            theme = "past_life"
        elif "unite" in big_story_goal.lower() or "leadership" in big_story_goal.lower() or "lead" in big_story_goal.lower():
            theme = "unite_martial_clans"
        elif "artifact" in big_story_goal.lower() or "treasure" in big_story_goal.lower() or "relic" in big_story_goal.lower():
            theme = "recover_legendary_artifact"
        elif "protect" in big_story_goal.lower() or "save" in big_story_goal.lower() or "dear" in big_story_goal.lower():
            theme = "protection"
        elif "unique" in big_story_goal.lower() or "own path" in big_story_goal.lower() or "rejected" in big_story_goal.lower():
            theme = "unique_dao"
        else:
            # Default to a random theme if no match found
            theme = random.choice(list(theme_to_templates.keys()))
            logger.info(f"No matching theme found for goal: '{big_story_goal}', defaulting to '{theme}'")
        
        # Get templates for the identified theme
        matching_templates = theme_to_templates.get(theme, [])
        if not matching_templates:
            # Fallback to first template if no matches
            matching_templates = [cultivation_story_templates[0]]
    
    # Randomly select one of the matching templates
    template = random.choice(matching_templates)
    pool = template["arcs"]
    
    # Filter out arcs already used recently
    available_arcs = [arc for arc in pool if arc not in arc_history]
    if not available_arcs or len(available_arcs) < num_arcs:
        logger.info(f"All or most arcs for theme '{template['theme']}' have been used, resetting pool")
        available_arcs = pool  # Reset if exhausted
    
    # Ensure we don't try to get more arcs than are available
    num_arcs = min(num_arcs, len(available_arcs))
    
    # Get random arcs without repetition
    new_arcs = random.sample(available_arcs, num_arcs)
    logger.info(f"Generated {len(new_arcs)} new arc goals for theme: '{template['theme']}'")
    
    return new_arcs

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

def extract_characters_from_content(memory: Any, story_content: str, protagonist_name: str) -> Any:
    """
    Extract potential character information from story content using simple text analysis.
    No additional API calls are made - this uses string matching and regex.
    
    Args:
        memory: The StoryMemory object to update
        story_content: The story content to analyze
        protagonist_name: The protagonist's name to avoid adding them
        
    Returns:
        The updated memory object
    """
    import re
    from logging import getLogger
    logger = getLogger(__name__)
    
    try:
        # Skip if content is too short
        if len(story_content) < 100:
            return memory
            
        # Initialize characters list if needed
        if not hasattr(memory, 'characters') or memory.characters is None:
            # Import here to avoid circular imports
            from ..models.models import Character
            memory.characters = []
            
        # Look for [NEW CHARACTERS] section first
        character_section_match = re.search(r'\[NEW CHARACTERS\](.*?)\[/NEW CHARACTERS\]', story_content, re.DOTALL)
        if character_section_match:
            # Extract characters from the dedicated section
            character_section = character_section_match.group(1).strip()
            logger.info(f"Found [NEW CHARACTERS] section: {character_section}")
            
            # Process each character entry
            character_entries = re.split(r'\n\s*\n', character_section)
            for entry in character_entries:
                if not entry.strip():
                    continue
                    
                # Extract character information
                lines = entry.strip().split('\n')
                if len(lines) < 2:
                    continue
                    
                name = lines[0].split(':', 1)[1].strip() if ':' in lines[0] else lines[0].strip()
                relationship = lines[1].split(':', 1)[1].strip() if ':' in lines[1] else lines[1].strip()
                
                # Optional sect and role
                sect = None
                role = None
                for line in lines[2:]:
                    if 'sect:' in line.lower():
                        sect = line.split(':', 1)[1].strip()
                    elif 'role:' in line.lower():
                        role = line.split(':', 1)[1].strip()
                
                logger.info(f"Extracted character from section: {name} - {relationship}")
                
                # Add character to memory
                memory = add_character_to_memory(
                    memory=memory,
                    name=name,
                    relationship=relationship,
                    sect=sect,
                    role=role
                )
                
            # Update supporting_characters dict
            for char in memory.characters:
                memory.supporting_characters[char.name] = {
                    "relationship": char.relationship,
                    "sect": char.sect,
                    "role": char.role
                }
                
            # Log final characters in memory
            logger.info(f"Memory now has {len(memory.characters)} characters: {', '.join([c.name for c in memory.characters])}")
        else:
            # Fallback to very basic character detection
            # This is just a simplified approach to catch obvious characters
            # We try to extract character names that appear in quotes or with common titles
            logger.info(f"No [NEW CHARACTERS] section found, using simplified detection")
            
            # Create a set of existing character names (lowercase for comparison)
            existing_names = {char.name.lower() for char in memory.characters}
            
            # Add protagonist name to avoid adding them
            existing_names.add(protagonist_name.lower())
            
            # Very basic pattern to catch "Elder X" or "Master Y" mentions
            basic_pattern = r'(Elder|Master)\s+([A-Z][a-z]+)'
            matches = re.finditer(basic_pattern, story_content)
            found_characters = {}
            
            for match in matches:
                title = match.group(1)
                name = match.group(2)
                
                # Skip if already exists or is protagonist
                if name.lower() in existing_names:
                    continue
                
                # Skip common words that might be mistaken for names
                if name in ["The", "And", "But", "This", "That", "Where", "When", "Who", "What", "Why", "How"]:
                    continue
                
                # Store the character
                key = name.lower()
                if key not in found_characters:
                    found_characters[key] = {
                        "name": name,
                        "relationship": "Unknown",
                        "sect": None,
                        "role": title
                    }
                    
            # Add found characters to memory
            if found_characters:
                logger.info(f"Found {len(found_characters)} potential characters with simple detection")
                
                for char_data in found_characters.values():
                    memory = add_character_to_memory(
                        memory=memory,
                        name=char_data["name"],
                        relationship=char_data["relationship"],
                        sect=char_data["sect"],
                        role=char_data["role"]
                    )
                    
                # Update supporting_characters dict
                for char in memory.characters:
                    memory.supporting_characters[char.name] = {
                        "relationship": char.relationship,
                        "sect": char.sect,
                        "role": char.role
                    }
    
    except Exception as e:
        logger.error(f"Error extracting characters from content: {e}")
        
    return memory 