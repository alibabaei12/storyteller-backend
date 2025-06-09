"""
Fantasy Adventure genre implementation for epic quest stories.
"""
from typing import List, Tuple, Optional, Literal
import openai
import logging
from pydantic import Field
from app.models.models import Choice
from app.models.base_genre import BaseGenre, Genre
import os
import json
import random
from dotenv import load_dotenv
from ..services import AIService  # Fixed import using relative path

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)


class FantasyAdventure(Genre):
    """Fantasy adventure story generator for epic quest narratives."""
    
    genre_name_value: Literal["Fantasy Adventure"] = "Fantasy Adventure"
    genre_context_value: Literal["fantasy adventure realm"] = "fantasy adventure realm"
    
    @property
    def genre_name(self) -> str:
        return self.genre_name_value
    
    @property
    def genre_context(self) -> str:
        return self.genre_context_value
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        character_origin: str = "normal",
        big_story_goal: str = None
    ) -> Tuple[str, List[Choice]]:
        """Generate a fantasy adventure story opening."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Create character origin profile
        origin_prompt = BaseGenre.create_character_origin_profile(character_origin, "fantasy")
        
        # Add big story goal if provided
        big_goal_prompt = ""
        if big_story_goal:
            big_goal_prompt = f"\n\nMAIN CHARACTER GOAL: {character_name}'s ultimate goal is to {big_story_goal}"
        
        system_prompt = f"""You are creating an engaging fantasy adventure manga/manhwa opening scene.

Use {pronouns} pronouns for {character_name}.

{origin_prompt}{big_goal_prompt}

FANTASY ADVENTURE REQUIREMENTS:
🏰 Setting: Magical fantasy world with wizards, magical creatures, enchanted locations
🎯 Structure: Create 4-6 panels that flow like manga/manhwa
💬 Dialogue: Characters must speak with distinct personalities (under 15 words per line)
🧠 Inner thoughts: Show {character_name}'s emotions and motivations (use italics)
✨ Magic: Include specific named spells or magical abilities with visual effects
🗺️ Quest elements: Adventure hooks, mysteries, or challenges to overcome

ESSENTIAL ELEMENTS:
- Specific magical location (enchanted forest, wizard tower, mystical city)
- Named magical spells or abilities ("Flame Burst", "Wind Walk", etc.)
- Clear indication of {character_name}'s magical abilities/experience
- Visual magical effects (glowing auras, elemental energies, etc.)
- At least one other character who speaks
- {character_name}'s inner thoughts showing personality

FORMAT:
[STORY]
Panel 1:
(Scene setup with magical location)

Panel 2:
(Character introduction with dialogue or inner thought)

Panel 3:
(Adventure hook or challenge appears)

Panel 4:
(Magic demonstration or action)

Panel 5:
(Consequence or reaction)

Panel 6 (optional):
(Setup for choices)
[/STORY]

[CHOICES]
1. (Adventurous/bold choice - 12+ words)
2. (Cautious/strategic choice - 12+ words)  
3. (Magical/mysterious choice - 12+ words)
[/CHOICES]"""

        user_prompt = f"""Create a fantasy adventure manga opening for {character_name} with {character_origin} origin.

Requirements:
- Show {character_name} in a magical fantasy location
- Include named magical spell or ability with visual effects
- Add dialogue from {character_name} and at least one other character
- Show {character_name}'s magical experience level
- Create adventure hook or quest challenge
- End with meaningful adventure choices

Make it engaging and magical like a real fantasy manga chapter opening."""

        try:
            logger.info(f"Generating fantasy adventure story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        # Simple fallback
        return BaseGenre.create_fallback_story(
            character_name,
            f"{character_name} stood at the edge of the Whispering Woods, clutching an ancient map that promised to lead to magical treasures. "
            f"As someone with a {character_origin} background, they faced the choice of how to begin their magical adventure.",
            [
                Choice(id="1", text="Enter the magical forest following the ancient map's path"),
                Choice(id="2", text="Seek out a local guide who knows the forest's dangers"),
                Choice(id="3", text="Use your magical abilities to reveal hidden paths ahead")
            ]
        )

    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        character_origin: str = None
    ) -> Tuple[str, List[Choice]]:
        """Continue a fantasy adventure story."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        system_prompt = f"""You are continuing a fantasy adventure manga/manhwa story.

Use {pronouns} pronouns for {character_name}.

CONTINUATION REQUIREMENTS:
- Start with immediate consequence of the previous choice
- Create 3-5 panels showing what happens next
- Include dialogue and inner thoughts
- Show magical progress or new challenges
- Advance the adventure meaningfully
- End with new choices

FANTASY ELEMENTS:
- Named spells with visual magical effects
- Fantasy locations and creatures
- Clear progression in magical abilities or quest
- Character growth or challenges

FORMAT:
[STORY]
Panel 1:
(Immediate result of previous choice)

Panel 2-4:
(Adventure development with dialogue and magic)

Final Panel:
(Setup for next choices)
[/STORY]

[CHOICES]
1. (Choice based on current adventure situation)
2. (Alternative magical approach)
3. (Bold/risky option)
[/CHOICES]"""

        user_prompt = f"""Continue the fantasy adventure story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

Show what happens next with:
- Immediate consequence of {character_name}'s choice
- Character dialogue and reactions
- Magical spells or fantasy elements
- Adventure progression
- Meaningful choices for what to do next"""

        try:
            logger.info(f"Continuing fantasy adventure story for {character_name}")
            
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except Exception as e:
            logger.error(f"Error continuing fantasy adventure story: {e}")
            return BaseGenre.create_contextual_fallback(character_name, selected_choice, self.genre_context) 