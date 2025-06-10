import logging
import os
from typing import List, Optional, Dict, Tuple

import openai
from dotenv import load_dotenv
from .story_planner import generate_big_story_goal
from ..genres import CultivationSetting
from ..models.models import Choice
from ..services.story_planner import generate_new_arc_goal

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI()


class AIService:
    """AI service for manga/manhwa story generation."""

    def __init__(self):
        """Initialize the AI service."""
        logger.info("Initialized AIService")

    @staticmethod
    def generate_initial_story(
            character_name: str,
            character_gender: str,
            setting: str,
            tone: str,
            character_origin: str,

    ) -> Tuple[str, List[Choice], Optional[str]]:
        """Generate initial story content with choices based on genre."""
        try:
            # Generate a big story goal
            big_story_goal = generate_big_story_goal(setting)
            logger.info(f"Generated big story goal: {big_story_goal}")

            # Create genre map here to avoid circular imports
            GENRE_MAP = {
                "cultivation": CultivationSetting(),
                # "fantasy_adventure": FantasyAdventure(),
                # "academy_magic": AcademyMagic(),
            }

            # Try to use the specific genre implementation if available
            if setting and setting in GENRE_MAP:
                genre = GENRE_MAP[setting]
                logger.info(f"Using {setting} genre for initial story")
                try:
                    if setting == "cultivation_progression":
                        # CultivationProgression returns an extra value (the arc goal)
                        story_content, choices, arc_goal = genre.generate_story(
                            character_name=character_name,
                            character_gender=character_gender,
                            character_origin=character_origin,
                            big_story_goal=big_story_goal,
                            style=tone
                        )
                        return story_content, choices, arc_goal
                    else:
                        # Other genres don't return arc goal
                        return genre.generate_story(
                            character_name=character_name,
                            character_gender=character_gender,
                            character_origin=character_origin,
                            big_story_goal=big_story_goal
                        )
                except Exception as e:
                    logger.error(f"Error in genre-specific story generation: {e}")
                    # Fall back to basic story but with the big_story_goal
                    return AIService._create_basic_story(character_name, setting, character_origin, big_story_goal)

            # Fallback to basic story
            logger.info(f"Using default genre for initial story (no specific genre found for {setting})")
            return AIService._create_basic_story(character_name, setting, character_origin, big_story_goal)

        except Exception as e:
            logger.error(f"Error generating initial story: {e}")
            return AIService._create_emergency_fallback(character_name, setting)

    @staticmethod
    def continue_story(
            character_name: str,
            character_gender: str,
            setting: str,
            tone: str,
            previous_content: str,
            selected_choice: str,
            character_origin: str = "normal",
            characters: List[Dict[str, str]] = None,
            memory=None
    ) -> Tuple[str, List[Choice]]:
        """Continue story based on previous content and selected choice."""
        try:
            # Import genre classes here to avoid circular imports

            # Create genre map here to avoid circular imports
            GENRE_MAP = {
                "cultivation": CultivationSetting(),
                # "fantasy_adventure": FantasyAdventure(),
                # "academy_magic": AcademyMagic(),
            }

            # Initialize or update arc goal for cultivation genre
            if setting == "cultivation" and memory:
                # Initialize current_arc_goal if not set
                if not memory.current_arc_goal and memory.big_story_goal:
                    memory.current_arc_goal = generate_new_arc_goal(memory.big_story_goal, memory.arc_history)
                    logger.info(f"Initialized arc goal: {memory.current_arc_goal}")

                    # Add to arc history
                    if memory.current_arc_goal not in memory.arc_history:
                        memory.arc_history.append(memory.current_arc_goal)

            # Prepare character relationships text for cultivation genre only
            character_relationships_text = ""
            if setting == "cultivation" and characters and len(characters) > 0:
                character_relationships_text = "\n\nKnown Characters:\n"
                for char in characters:
                    char_info = f"- {char.name}: {char.relationship}"
                    if hasattr(char, 'sect') and char.sect:
                        char_info += f", {char.sect}"
                    if hasattr(char, 'role') and char.role:
                        char_info += f", {char.role}"
                    character_relationships_text += char_info + "\n"
                character_relationships_text += "\nRemember to:\n- Maintain existing relationships\n- Bring back important characters when relevant\n- Update relationships if they change (e.g., Friend becomes Rival)"

            # Try to use the specific genre implementation if available
            if setting and setting in GENRE_MAP:
                genre = GENRE_MAP[setting]
                logger.info(f"Using {setting} genre for story continuation")

                # For cultivation_progression, we also want to pass the big_story_goal
                if setting == "cultivation":
                    # Generate a big story goal for cultivation
                    big_story_goal = generate_big_story_goal(setting)
                    logger.info(f"Using big story goal for cultivation continuation: {big_story_goal}")

                    return genre.continue_story(
                        character_name=character_name,
                        character_gender=character_gender,
                        previous_content=previous_content + character_relationships_text,
                        selected_choice=selected_choice,
                        character_origin=character_origin,
                        big_story_goal=big_story_goal,
                        memory=memory
                    )
                else:
                    # For other genres, don't pass the big_story_goal or character info
                    return genre.continue_story(
                        character_name=character_name,
                        character_gender=character_gender,
                        previous_content=previous_content,
                        selected_choice=selected_choice,
                        character_origin=character_origin
                    )

            # Fallback to basic continuation
            logger.info(f"Using default genre for story continuation (no specific genre found for {setting})")
            return AIService._create_basic_continuation(character_name, setting, previous_content, selected_choice)

        except Exception as e:
            logger.error(f"Error continuing story: {e}")
            return AIService._create_emergency_continuation(character_name, selected_choice)

    @staticmethod
    def _create_character_origin_profile(character_origin: str, setting: str) -> str:
        """Create character origin profile for prompt engineering."""
        if character_origin == "reincarnated":
            return f"The character was reincarnated from another world with knowledge of their past life."
        elif character_origin == "weak":
            return f"The character starts with major disadvantages and is considered weak in this world."
        elif character_origin == "hidden":
            return f"The character has hidden talents or a secret background not apparent to others."
        elif character_origin == "genius":
            return f"The character is naturally talented and learns much faster than others."
        elif character_origin == "fallen":
            return f"The character once had high status but has fallen from grace and must rebuild."
        else:  # normal/ordinary
            return f"The character has a normal background with no special advantages or disadvantages."
