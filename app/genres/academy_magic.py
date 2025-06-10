"""
Academy Magic genre implementation for magical school stories.
"""
import logging
from typing import List, Tuple, Literal

import openai
from dotenv import load_dotenv  # Fixed import using relative path

from app.models.base_genre import BaseGenre, Genre
from app.models.models import Choice

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

class AcademyMagic(Genre):
    """Academy magic story generator for magical school narratives."""
    
    genre_name_value: Literal["Academy Magic"] = "Academy Magic"
    genre_context_value: Literal["magical academy realm"] = "magical academy realm"
    
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
        """Generate an academy magic story opening."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Create character origin profile
        origin_prompt = BaseGenre.create_character_origin_profile(character_origin, "academy")
        
        system_prompt = f"""You are creating an engaging magical academy manga/manhwa opening scene.

Use {pronouns} pronouns for {character_name}.

{origin_prompt}

MAGICAL ACADEMY REQUIREMENTS:
🏫 Setting: Magical school with students, teachers, classes, dormitories, competitions
🎯 Structure: Create 4-6 panels that flow like manga/manhwa
💬 Dialogue: Characters must speak with distinct personalities (under 15 words per line)
🧠 Inner thoughts: Show {character_name}'s emotions and motivations (use italics)
📚 Magic: Include specific named spells or magical subjects with visual effects
👨‍🎓 School elements: Classes, rankings, rivalries, professors, competitions

ESSENTIAL ELEMENTS:
- Specific academy location (classroom, training hall, dormitory, library)
- Named magical subjects or spells ("Elemental Theory", "Light Weaving", etc.)
- Clear indication of {character_name}'s magical rank/class standing
- Visual magical effects (spell casting, magical auras, etc.)
- At least one other character who speaks (classmate, rival, professor)
- {character_name}'s inner thoughts showing personality

FORMAT:
[STORY]
Panel 1:
(Scene setup with academy location)

Panel 2:
(Character introduction with dialogue or inner thought)

Panel 3:
(School challenge or competition appears)

Panel 4:
(Magic demonstration or class activity)

Panel 5:
(Consequence or reaction)

Panel 6 (optional):
(Setup for choices)
[/STORY]

[CHOICES]
1. (Academic/studious choice - 12+ words)
2. (Social/competitive choice - 12+ words)  
3. (Bold/risky choice - 12+ words)
[/CHOICES]"""

        user_prompt = f"""Create a magical academy manga opening for {character_name} with {character_origin} origin.

Requirements:
- Show {character_name} in a specific academy location
- Include named magical subject or spell with visual effects
- Add dialogue from {character_name} and at least one other character
- Show {character_name}'s academic rank or magical abilities
- Create school challenge or competition scenario
- End with meaningful academic/social choices

Make it engaging and magical like a real school magic manga chapter opening."""

        try:
            logger.info(f"Generating academy magic story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        # Simple fallback
        return BaseGenre.create_fallback_story(
            character_name,
            f"{character_name} walked through the halls of Mystral Academy, nervously clutching their spell books. "
            f"As a {character_origin} student in the first-year class, they faced their first major magical examination.",
            [
                Choice(id="1", text="Study harder in the library to improve your magical theory knowledge"),
                Choice(id="2", text="Practice spells with classmates to build teamwork and friendship"),
                Choice(id="3", text="Attempt to learn advanced magic beyond your current year level")
            ]
        )

    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        character_origin: str = None,
        big_story_goal: str = None
    ) -> Tuple[str, List[Choice]]:
        """Continue an academy magic story."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        system_prompt = f"""You are continuing a magical academy manga/manhwa story.

Use {pronouns} pronouns for {character_name}.

CONTINUATION REQUIREMENTS:
- Start with immediate consequence of the previous choice
- Create 3-5 panels showing what happens next
- Include dialogue and inner thoughts
- Show academic progress or new challenges
- Advance the school story meaningfully
- End with new choices

ACADEMY ELEMENTS:
- Named spells with visual magical effects
- School locations and characters (classmates, professors)
- Clear progression in magical abilities or school rank
- Character growth or academic challenges

FORMAT:
[STORY]
Panel 1:
(Immediate result of previous choice)

Panel 2-4:
(School development with dialogue and magic)

Final Panel:
(Setup for next choices)
[/STORY]

[CHOICES]
1. (Choice based on current school situation)
2. (Alternative academic approach)
3. (Social/risky option)
[/CHOICES]"""

        user_prompt = f"""Continue the magical academy story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

Show what happens next with:
- Immediate consequence of {character_name}'s choice
- Character dialogue and reactions
- Magical spells or academy elements
- School progression
- Meaningful choices for what to do next"""

        try:
            logger.info(f"Continuing academy magic story for {character_name}")
            
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except Exception as e:
            logger.error(f"Error continuing academy magic story: {e}")
            return BaseGenre.create_contextual_fallback(character_name, selected_choice, self.genre_context) 