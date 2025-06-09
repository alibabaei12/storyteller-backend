import os
import json
import time
import openai
import requests
import logging
from typing import List, Optional, Dict, Any, Tuple, Union
from dotenv import load_dotenv
import tiktoken
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Import only the models needed for types, not the genre classes
from ..models.models import StoryNode, Choice
from .story_planner import generate_big_story_goal
from .story_planner import generate_big_story_goal

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
        manga_genre: str = None
    ) -> Tuple[str, List[Choice], Optional[str]]:
        """Generate initial story content with choices based on genre."""
        try:
            # Generate a big story goal
            big_story_goal = generate_big_story_goal(manga_genre or setting)
            logger.info(f"Generated big story goal: {big_story_goal}")
            
            # Import genre classes here to avoid circular imports
            from ..genres.cultivation_progression import CultivationProgression
            from ..genres.fantasy_adventure import FantasyAdventure
            from ..genres.academy_magic import AcademyMagic
            
            # Create genre map here to avoid circular imports
            GENRE_MAP = {
                "cultivation_progression": CultivationProgression(),
                "fantasy_adventure": FantasyAdventure(),
                "academy_magic": AcademyMagic(),
            }
            
            # Try to use the specific genre implementation if available
            if manga_genre and manga_genre in GENRE_MAP:
                genre = GENRE_MAP[manga_genre]
                logger.info(f"Using {manga_genre} genre for initial story")
                try:
                    if manga_genre == "cultivation_progression":
                        # CultivationProgression returns an extra value (the arc goal)
                        story_content, choices, arc_goal = genre.generate_story(
                            character_name=character_name,
                            character_gender=character_gender,
                            character_origin=character_origin,
                            big_story_goal=big_story_goal
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
            logger.info(f"Using default genre for initial story (no specific genre found for {manga_genre})")
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
        manga_genre: str = None,
        character_origin: str = "normal",
        characters: List[Dict[str, str]] = None,
        memory = None
    ) -> Tuple[str, List[Choice]]:
        """Continue story based on previous content and selected choice."""
        try:
            # Import genre classes here to avoid circular imports
            from ..genres.cultivation_progression import CultivationProgression
            from ..genres.fantasy_adventure import FantasyAdventure
            from ..genres.academy_magic import AcademyMagic
            from ..services.story_planner import generate_new_arc_goal
            
            # Create genre map here to avoid circular imports
            GENRE_MAP = {
                "cultivation_progression": CultivationProgression(),
                "fantasy_adventure": FantasyAdventure(),
                "academy_magic": AcademyMagic(),
            }
            
            # Initialize or update arc goal for cultivation genre
            if manga_genre == "cultivation_progression" and memory:
                # Initialize current_arc_goal if not set
                if not memory.current_arc_goal and memory.big_story_goal:
                    memory.current_arc_goal = generate_new_arc_goal(memory.big_story_goal, memory.arc_history)
                    logger.info(f"Initialized arc goal: {memory.current_arc_goal}")
                    
                    # Add to arc history
                    if memory.current_arc_goal not in memory.arc_history:
                        memory.arc_history.append(memory.current_arc_goal)
            
            # Prepare character relationships text for cultivation genre only
            character_relationships_text = ""
            if manga_genre == "cultivation_progression" and characters and len(characters) > 0:
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
            if manga_genre and manga_genre in GENRE_MAP:
                genre = GENRE_MAP[manga_genre]
                logger.info(f"Using {manga_genre} genre for story continuation")
                
                # For cultivation_progression, we also want to pass the big_story_goal
                if manga_genre == "cultivation_progression":
                    # Generate a big story goal for cultivation
                    big_story_goal = generate_big_story_goal(manga_genre)
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
            logger.info(f"Using default genre for story continuation (no specific genre found for {manga_genre})")
            return AIService._create_basic_continuation(character_name, setting, previous_content, selected_choice)
            
        except Exception as e:
            logger.error(f"Error continuing story: {e}")
            return AIService._create_emergency_continuation(character_name, selected_choice)
    
    @staticmethod
    def _create_basic_story(character_name: str, setting: str, character_origin: str, big_story_goal: str) -> Tuple[str, List[Choice], Optional[str]]:
        """Create a basic story opening when no specific genre is available."""
        # Generate a simple arc goal
        from ..services.story_planner import generate_new_arc_goal
        try:
            arc_goal = generate_new_arc_goal(big_story_goal, [])
        except Exception:
            arc_goal = "Survive the sect's brutal outer disciple training."
            
        # For cultivation settings, create a more appropriate story opening
        if setting == "cultivation" or setting == "cultivation_progression":
            story_content = (
                f"{character_name} stood at the entrance of Azure Cloud Sect, clutching the admission token tightly. "
                f"With a {character_origin} background, they knew the path ahead would be challenging. "
                f"The sect was known for its strict training and powerful cultivation techniques. "
                f"As a new disciple seeking to {big_story_goal}, they must navigate the complex world of cultivation carefully."
            )
            return (
                story_content,
                [
                    Choice(id="1", text="Request to join the outer disciples' training grounds"),
                    Choice(id="2", text="Seek out a potential mentor among the senior disciples"),
                    Choice(id="3", text="Explore the sect library to learn about cultivation techniques")
                ],
                arc_goal
            )
        else:
            return (
                f"{character_name} finds themselves in a {setting} setting. With a {character_origin} background, "
                f"they must navigate this world and overcome the challenges that lie ahead. The big story goal is: {big_story_goal}",
                [
                    Choice(id="1", text="Explore the immediate surroundings to get your bearings"),
                    Choice(id="2", text="Seek out other characters who might provide guidance"),
                    Choice(id="3", text="Focus on developing your abilities to prepare for challenges")
                ],
                arc_goal
            )
    
    @staticmethod
    def _create_basic_continuation(character_name: str, setting: str, previous_content: str, selected_choice: str) -> Tuple[str, List[Choice]]:
        """Create a basic story continuation when no specific genre is available."""
        return (
            f"{character_name} decides to {selected_choice.lower()}. "
            f"This choice leads to new discoveries and challenges in the {setting} setting.",
            [
                Choice(id="1", text="Take a cautious approach to the new situation"),
                Choice(id="2", text="Boldly confront the challenges head-on"),
                Choice(id="3", text="Seek an alternative path or unexpected solution")
            ]
        )
    
    @staticmethod
    def _create_emergency_fallback(character_name: str, setting: str) -> Tuple[str, List[Choice], Optional[str]]:
        """Create an emergency fallback story when generation fails."""
        # Use a default arc goal for emergency fallback
        arc_goal = "Survive the sect's brutal outer disciple training."
        
        return (
            f"{character_name}'s journey begins in the {setting}. What path will they choose?",
            [
                Choice(id="1", text="Take the path of caution and preparation"),
                Choice(id="2", text="Choose the path of action and courage"),
                Choice(id="3", text="Follow the path of wisdom and strategy")
            ],
            arc_goal
        )
    
    @staticmethod
    def _create_emergency_continuation(character_name: str, selected_choice: str) -> Tuple[str, List[Choice]]:
        """Create an emergency fallback continuation when generation fails."""
        return (
            f"{character_name} decides to {selected_choice.lower()}. What will they do next?",
            [
                Choice(id="1", text="Carefully consider your options before proceeding"),
                Choice(id="2", text="Take decisive action based on your instincts"),
                Choice(id="3", text="Look for creative solutions to the problem")
            ]
        )
    
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