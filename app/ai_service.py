import openai
import logging
from typing import List, Tuple

from .models import Choice
from .genres.cultivation_progression import CultivationProgression
from .genres.fantasy_adventure import FantasyAdventure
from .genres.academy_magic import AcademyMagic

# Set up logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI()

class AIService:
    """Clean, focused AI service for manga/manhwa story generation."""
    
    # Only the 3 genres that the frontend actually uses
    GENRE_MAP = {
        "cultivation_progression": CultivationProgression(),
        "fantasy_adventure": FantasyAdventure(),
        "academy_magic": AcademyMagic(),
    }
    
    @staticmethod
    def generate_initial_story(
        character_name: str,
        character_gender: str,
        setting: str,
        tone: str,
        character_origin: str,
        manga_genre: str = None
    ) -> Tuple[str, List[Choice]]:
        """Generate initial story using the appropriate genre handler."""
        try:
            logger.info(f"Generating initial story for {character_name} in {manga_genre or setting}")
            
            # Use specialized genre if specified
            if manga_genre and manga_genre in AIService.GENRE_MAP:
                selected_genre = AIService.GENRE_MAP[manga_genre]
                return selected_genre.generate_story(
                    character_name, character_gender, character_origin
                )
            
            # Fallback to basic story if no manga genre specified
            return AIService._create_basic_story(character_name, setting, character_origin)
            
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
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Continue story using the appropriate genre handler."""
        try:
            logger.info(f"Continuing story for {character_name} in {manga_genre or setting}")
            
            # Use specialized genre if specified
            if manga_genre and manga_genre in AIService.GENRE_MAP:
                selected_genre = AIService.GENRE_MAP[manga_genre]
                return selected_genre.continue_story(
                    character_name, character_gender, previous_content, selected_choice, character_origin
                )
            
            # Fallback to basic continuation if no manga genre specified
            return AIService._create_basic_continuation(character_name, setting, previous_content, selected_choice)
            
        except Exception as e:
            logger.error(f"Error continuing story: {e}")
            return AIService._create_emergency_continuation(character_name, selected_choice)
    
    @staticmethod
    def _create_basic_story(character_name: str, setting: str, character_origin: str) -> Tuple[str, List[Choice]]:
        """Create a basic story for non-manga genres."""
        story_content = f"{character_name} stands at the beginning of their journey in this {setting} world. " \
                       f"As someone with a {character_origin} background, they face unique challenges and opportunities ahead."
        
        choices = [
            Choice(id="1", text=f"Explore the {setting} world carefully"),
            Choice(id="2", text="Seek out allies and companions"),
            Choice(id="3", text="Take bold action to make a name for yourself")
        ]
        
        return story_content, choices
    
    @staticmethod
    def _create_basic_continuation(character_name: str, setting: str, previous_content: str, selected_choice: str) -> Tuple[str, List[Choice]]:
        """Create a basic story continuation for non-manga genres with mandatory clarity rules."""
        
        # Enhanced prompt with mandatory story clarity rules
        system_prompt = f"""
🔑 **MANDATORY STORY CLARITY RULES (Every Chapter MUST fulfill):**

1. **Clear Logical Sequence**:
   - Every event and action MUST have a logical cause-and-effect relationship clearly shown visually.
   - Explicitly describe how the protagonist moves from one location or situation to another logically and visually.

2. **Meaningful Payoff**:
   - When {character_name} completes a challenge or test, explicitly provide a clear, tangible reward or clear meaningful consequence.
   - Rewards must be visually and narratively clear (e.g., clearly described new techniques, valuable knowledge, powerful artifacts, allies).

3. **Clear Motivation & Intention**:
   - Clearly explain character motivations and dialogue context visually or through internal thought.
   - Do NOT use repetitive cryptic dialogues ("prove your worth") without explicitly clarifying what this means in the current situation.

4. **Explicit Scene Continuity**:
   - Clearly and logically transition from one chapter scene to the next, explicitly describing where the protagonist is and why they moved there.

🚫 **STRICTLY FORBIDDEN (Do NOT do this):**
- Unexplained scene transitions.
- Vague rewards or unclear outcomes after challenges.
- Repetitive cryptic dialogue without explicit clarity or meaningful context.
- Actions or outcomes that confuse readers about what exactly happened.

Create a {setting} story continuation that strictly adheres to these mandatory clarity rules, ensuring readers easily follow every event visually, logically, and emotionally.
"""

        user_prompt = f"""
PREVIOUS STORY:
{previous_content}

CHOSEN ACTION: {selected_choice}

Continue the story for {character_name} following their chosen action. Write 4-6 panels showing:
- Clear logical consequences of their choice
- Explicit scene transitions with visual descriptions
- Meaningful outcomes or rewards
- Clear character motivations
- Set up the next decision point logically

Format as:
Panel 1: [Clear scene description with logical continuation]
Panel 2: [Visual action/dialogue with clear motivation]
...
Panel N: [Meaningful outcome leading to choices]
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            story_content = response.choices[0].message.content.strip()
            
            # Generate contextual choices
            choices = [
                Choice(id="1", text=f"Continue {character_name}'s journey with determination"),
                Choice(id="2", text=f"Have {character_name} seek guidance about what just happened"),
                Choice(id="3", text=f"Let {character_name} explore the new opportunity carefully")
            ]
            
            return story_content, choices
            
        except Exception as e:
            logger.error(f"Error in enhanced basic continuation: {e}")
            # Fallback to simple continuation
            story_content = f"Following their decision to {selected_choice.lower()}, {character_name} discovers new " \
                           f"opportunities in this {setting} world. The path ahead becomes clearer with each step."
            
            choices = [
                Choice(id="1", text="Continue with confidence"),
                Choice(id="2", text="Proceed with caution"),
                Choice(id="3", text="Take a different approach")
            ]
            
            return story_content, choices
    
    @staticmethod
    def _create_emergency_fallback(character_name: str, setting: str) -> Tuple[str, List[Choice]]:
        """Emergency fallback when everything else fails."""
        story_content = f"Welcome to your adventure, {character_name}. Your journey in this {setting} world is about to begin."
        
        choices = [
            Choice(id="1", text="Begin your adventure"),
            Choice(id="2", text="Prepare carefully first"),
            Choice(id="3", text="Seek guidance")
        ]
        
        return story_content, choices
    
    @staticmethod
    def _create_emergency_continuation(character_name: str, selected_choice: str) -> Tuple[str, List[Choice]]:
        """Emergency continuation fallback."""
        story_content = f"{character_name} moves forward with determination, ready to face whatever comes next."
        
        choices = [
            Choice(id="1", text="Continue forward"),
            Choice(id="2", text="Look for new opportunities"),
            Choice(id="3", text="Reassess the situation")
        ]
        
        return story_content, choices
    
    @staticmethod
    def _create_character_origin_profile(character_origin: str, setting: str) -> str:
        """Create character origin profile for the given setting."""
        
        origin_profiles = {
            "weak": {
                "cultivation": "Starting with minimal qi sensitivity, often mocked by sect members",
                "fantasy": "Possessing little magical talent initially, overlooked by most",
                "academy": "Struggling with basic magical concepts, ranked at the bottom of class"
            },
            "normal": {
                "cultivation": "Average cultivation potential with steady, unremarkable progress",
                "fantasy": "Typical magical abilities, neither gifted nor hindered",
                "academy": "Standard magical aptitude, blending in with most students"
            },
            "hidden": {
                "cultivation": "Concealing true cultivation level or possessing secret techniques",
                "fantasy": "Hiding powerful magical bloodline or ancient knowledge",
                "academy": "Masking exceptional abilities to avoid unwanted attention"
            },
            "reincarnated": {
                "cultivation": "Retaining memories of past life as a powerful cultivator",
                "fantasy": "Carrying knowledge from previous existence in this world",
                "academy": "Remembering advanced magical theory from past incarnation"
            },
            "genius": {
                "cultivation": "Exceptional qi comprehension and rapid cultivation advancement",
                "fantasy": "Extraordinary magical talent that surpasses peers",
                "academy": "Prodigious magical abilities that astound teachers"
            },
            "fallen": {
                "cultivation": "Once powerful but now reduced to lowest cultivation levels",
                "fantasy": "Former magical prodigy who lost abilities due to tragedy",
                "academy": "Previously top student now struggling after mysterious incident"
            }
        }
        
        profile = origin_profiles.get(character_origin, {})
        description = profile.get(setting, f"A {character_origin} character in a {setting} world")
        
        return f"CHARACTER ORIGIN: {character_origin.title()} - {description}" 