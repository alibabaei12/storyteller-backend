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
            num_arcs: int = 5
    ) -> Tuple[str, List[Choice], str, str, List[str]]:
        """Generate initial story content with choices based on genre."""
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
            # CultivationProgression returns extra values (arc goal and all arc goals)
            story_content, choices, arc_goal, all_arc_goals = genre.generate_story(
                character_name=character_name,
                character_gender=character_gender,
                character_origin=character_origin,
                big_story_goal=big_story_goal,
                style=tone
            )
            return story_content, choices, arc_goal, big_story_goal, all_arc_goals
        else:
            # No fallback - raise an error for unsupported settings
            raise ValueError(f"Setting not supported: {setting}")

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
            memory=None,
            num_arcs: int = 5
    ) -> Tuple[str, List[Choice]]:
        """Continue story based on previous content and selected choice."""
        try:
            # Create genre map here to avoid circular imports
            GENRE_MAP = {
                "cultivation": CultivationSetting(),
                # "fantasy_adventure": FantasyAdventure(),
                # "academy_magic": AcademyMagic(),
            }

            # Log memory state before processing
            if memory:
                logger.info(f"Memory before processing - chapters_completed: {memory.chapters_completed}, current_arc_index: {memory.current_arc_index}, chapters_per_arc: {memory.chapters_per_arc}")
                if hasattr(memory, 'arcs') and memory.arcs:
                    logger.info(f"Memory arcs: {len(memory.arcs)} arcs total")
                    if memory.current_arc_index < len(memory.arcs):
                        logger.info(f"Current arc: '{memory.arcs[memory.current_arc_index]}'")
                    else:
                        logger.error(f"Invalid arc index: {memory.current_arc_index} (max: {len(memory.arcs)-1})")

            # Track chapter completion and check for arc completion if memory exists
            if memory and hasattr(memory, 'arcs') and memory.arcs:
                try:
                    # Safely get current arc goal
                    current_arc_goal = None
                    if 0 <= memory.current_arc_index < len(memory.arcs):
                        current_arc_goal = memory.arcs[memory.current_arc_index]
                    else:
                        logger.error(f"Arc index out of range: {memory.current_arc_index}, arcs: {len(memory.arcs)}")
                        # Fix invalid index
                        memory.current_arc_index = min(max(0, memory.current_arc_index), max(0, len(memory.arcs)-1))
                        if memory.arcs:
                            current_arc_goal = memory.arcs[memory.current_arc_index]
                    
                    # Increment chapters completed
                    memory.chapters_completed += 1
                    logger.info(f"Chapter {memory.chapters_completed} of arc '{current_arc_goal}' completed")
                    
                    # Check if we need to move to the next arc
                    if memory.chapters_completed >= memory.chapters_per_arc:
                        # Current arc is complete
                        completed_arc = current_arc_goal
                        
                        # Check if we have more arcs
                        if memory.current_arc_index + 1 < len(memory.arcs):
                            # Move to the next arc
                            memory.current_arc_index += 1
                            new_arc_goal = memory.arcs[memory.current_arc_index]
                            
                            # Reset chapter counter for the new arc
                            memory.chapters_completed = 0
                            
                            # Add to arc history if not already there
                            if new_arc_goal not in memory.arc_history:
                                memory.arc_history.append(new_arc_goal)
                                
                            logger.info(f"Moving to next arc: '{new_arc_goal}', index {memory.current_arc_index}")
                        else:
                            # We've completed all arcs - the story is finished
                            logger.info("All arcs completed! Story is finished.")
                            
                            # Mark the story as completed
                            memory.story_completed = True
                            
                            # For a finished story, return a final message and special choices
                            final_content = f"""
                            ---
                            
                            # The Journey Concludes
                            
                            {character_name}'s epic journey comes to a close. With the final goal of **{current_arc_goal}** achieved, {character_name} has accomplished what few could even dream of.
                            
                            ---
                            
                            Looking back on the road traveled, from humble beginnings to reaching the pinnacle of power, {character_name} feels a profound sense of achievement. The challenges overcome, enemies defeated, and allies made along the way have all contributed to this moment of triumph.
                            
                            ---
                            
                            **Congratulations on completing your story!**
                            """
                            
                            final_choices = [
                                Choice(id="1", text="Start a new adventure"),
                                Choice(id="2", text="Reflect on your journey"),
                                Choice(id="3", text="Share your story")
                            ]
                            
                            return final_content, final_choices
                except Exception as e:
                    logger.error(f"Error processing arc progression: {str(e)}")
                    # Continue with the story even if arc progression fails

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

            # Add current arc goal to the prompt
            arc_goal_text = ""
            if memory and hasattr(memory, 'arcs') and memory.arcs and 0 <= memory.current_arc_index < len(memory.arcs):
                current_arc_goal = memory.arcs[memory.current_arc_index]
                arc_goal_text = f"\n\nCURRENT ARC GOAL: {current_arc_goal}"
                
                # Add progress info
                if memory.chapters_completed > 0:
                    arc_goal_text += f" (Chapter {memory.chapters_completed + 1} of {memory.chapters_per_arc})"
                
                # If this is the final chapter of the arc, mention it
                if memory.chapters_completed == memory.chapters_per_arc - 1:
                    arc_goal_text += "\nThis is the FINAL CHAPTER of the current arc. Conclude this arc goal in a satisfying way."

            # Try to use the specific genre implementation if available
            if setting and setting in GENRE_MAP:
                genre = GENRE_MAP[setting]
                logger.info(f"Using {setting} genre for story continuation")

                # For cultivation_progression, we also want to pass the big_story_goal
                if setting == "cultivation":
                    # Get big story goal from memory if available, otherwise generate
                    big_story_goal = memory.big_story_goal if memory and hasattr(memory, 'big_story_goal') and memory.big_story_goal else generate_big_story_goal(setting)
                    logger.info(f"Using big story goal for cultivation continuation: {big_story_goal}")

                    return genre.continue_story(
                        character_name=character_name,
                        character_gender=character_gender,
                        previous_content=previous_content + character_relationships_text + arc_goal_text,
                        selected_choice=selected_choice,
                        character_origin=character_origin,
                        big_story_goal=big_story_goal,
                        memory=memory,
                        style=tone
                    )
                else:
                    # For other genres, don't pass the big_story_goal or character info
                    return genre.continue_story(
                        character_name=character_name,
                        character_gender=character_gender,
                        previous_content=previous_content,
                        selected_choice=selected_choice,
                        character_origin=character_origin,
                        style=tone
                    )
            else:
                # No fallback - raise an error for unsupported settings
                raise ValueError(f"Setting not supported: {setting}")
        except Exception as e:
            logger.error(f"Error in continue_story: {str(e)}")
            # Return a basic error message with valid choices to keep the app working
            error_content = f"""
            # Unexpected Error
            
            We encountered an issue continuing your story. Don't worry, your story is saved.
            
            Technical details: {str(e)}
            
            Please choose an option below to continue:
            """
            
            error_choices = [
                Choice(id="1", text="Try continuing from here"),
                Choice(id="2", text="Start a new branch of the story"),
                Choice(id="3", text="Let the AI suggest how to continue")
            ]
            
            return error_content, error_choices

    @staticmethod
    def _create_character_origin_profile(character_origin: str, setting: str) -> str:
        """Create character origin profile for prompt engineering."""
        # Import here to avoid circular import
        from ..models.base_genre import BaseGenre
        
        # Use the BaseGenre implementation with a placeholder character name
        # This is a fallback method, as most code should use the BaseGenre method directly
        return BaseGenre.create_character_origin_profile(character_origin, "the character")

    @staticmethod
    def get_genre_instance(setting: str):
        """Get the genre instance based on the setting."""
        # Create genre map here to avoid circular imports
        from ..genres.cultivation_setting import CultivationSetting
        
        GENRE_MAP = {
            "cultivation": CultivationSetting(),
            # Add other genres here as they are implemented
        }
        
        return GENRE_MAP.get(setting)
