"""
Fantasy Adventure genre implementation for epic quest stories.
"""
from typing import List, Tuple
import openai
import logging
from ..models import Choice
from ..base_genre import BaseGenre, Genre

# Set up logger
logger = logging.getLogger(__name__)


class FantasyAdventure(Genre):
    """Fantasy adventure story generator optimized for manga-style epic quests."""
    
    @property
    def genre_name(self) -> str:
        return "Fantasy Adventure"
    
    @property
    def genre_context(self) -> str:
        return "fantasy adventure realm"
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        language_complexity: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Generate a fantasy adventure story optimized for manga-style progression."""
        
        # Create language complexity prompt addition
        language_prompt = BaseGenre.create_language_prompt(language_complexity)
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Import the origin profile method
        from app.ai_service import AIService
        
        # Create character origin profile with fantasy-specific context
        origin_prompt = AIService._create_character_origin_profile(character_origin, "fantasy")
        
        system_prompt = f"""You are a master storyteller creating ENGAGING fantasy adventure stories in the style of popular manga/light novels like "That Time I Got Reincarnated as a Slime," "Overlord," and "KonoSuba."

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

FANTASY ADVENTURE STORY REQUIREMENTS:
🌟 IMMEDIATE HOOK: Start with {character_name} in a moment that shows their personality before explaining the fantasy world
🏰 WORLD IMMERSION: Create a vivid fantasy setting with unique magical elements, not generic "kingdom" or "village"
✨ CLEAR MAGIC SYSTEM: Establish how magic/powers work in this world with specific examples
🎯 PERSONAL STAKES: Give {character_name} a compelling reason to adventure (save someone, find truth, fulfill promise)
🌍 LIVING WORLD: Include specific locations, factions, or conflicts that feel real and lived-in

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

ENGAGEMENT REQUIREMENTS:
- EMOTIONAL OPENING: Make readers care about {character_name} within the first paragraph
- ADVENTURE SCALE: Balance intimate character moments with epic adventure possibilities
- CLEAR PROGRESSION: Show how {character_name} can grow stronger/more capable
- VISUAL STORYTELLING: Use rich descriptions that feel cinematic and manga-like
- IMMEDIATE CONFLICT: Present a challenge that matters to {character_name} personally

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Exploration: Discover new locations, investigate mysteries
- Social: Build alliances, help NPCs, negotiate
- Combat: Face dangers head-on, protect others
- Strategic: Plan carefully, gather information
- Magical: Use or learn magic, experiment with powers
- Diplomatic: Resolve conflicts peacefully
- Risk-taking: Take bold actions, attempt difficult feats
- Protective: Help others, prevent harm
- Mysterious: Follow clues, investigate secrets
- Cautious: Observe and plan before acting

Each choice must reference specific adventure elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and adventure-specific.

Generate a fantasy adventure opening that makes readers think: "This world is fascinating and I want to see {character_name} explore it!"

FORMAT:
[STORY]
(Your story here)
[/STORY]

[CHOICES]
1. (First dynamic choice based on your story)
2. (Second dynamic choice based on your story) 
3. (Third dynamic choice based on your story)
[/CHOICES]
"""

        user_prompt = f"""Create an engaging fantasy adventure story opening for {character_name} with a {character_origin} origin. 

ORIGIN INTEGRATION REQUIREMENTS:
- Make {character_name}'s {character_origin} background central to the fantasy adventure setup
- Show how their origin affects their approach to magic, quests, and relationships
- Include at least one moment where their {character_origin} nature creates opportunities or challenges
- Let their origin influence their starting situation and available choices

Make it feel like the start of an epic quest with clear magical elements and personal stakes that relate to their {character_origin} background.

Format your response as:
[STORY]
(400-500 words of story content)
[/STORY]

[CHOICES]  
1. (First choice)
2. (Second choice)
3. (Third choice)
[/CHOICES]"""
        
        try:
            logger.info(f"Generating fantasy adventure story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating fantasy adventure story: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating fantasy adventure story: {e}")
            # Fantasy adventure fallback
            return BaseGenre.create_fallback_story(
                character_name,
                f"{character_name} stood at the edge of the mystical Whispering Woods, clutching an ancient map that promised to lead to the Crystal of Eloria. "
                f"The village elder had entrusted them with this quest to save their homeland from the encroaching Shadow Plague. "
                f"As magical butterflies danced around them, {character_name} realized this journey would test not just their courage, but their very soul...",
                [
                    Choice(id="1", text="Follow the magical butterflies deeper into the forest"),
                    Choice(id="2", text="Return to the village to gather more allies"),
                    Choice(id="3", text="Set up camp and study the ancient map carefully")
                ]
            )

    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        language_complexity: str,
        character_origin: str = None
    ) -> Tuple[str, List[Choice]]:
        """Continue a fantasy adventure story."""
        
        # Create language complexity prompt addition
        language_prompt = BaseGenre.create_language_prompt(language_complexity)
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        system_prompt = f"""You are continuing an engaging fantasy adventure story in the style of popular manga/light novels.

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

FANTASY ADVENTURE CONTINUATION REQUIREMENTS:
🎯 ADVENTURE PROGRESS: Show advancement in quest, new locations, or magical discoveries
🌟 RAISE STAKES: Introduce new challenges, allies, enemies, or mysteries
✨ MAGICAL GROWTH: Demonstrate {character_name}'s developing abilities or knowledge
🏰 WORLD EXPANSION: Add new fantasy locations, creatures, or lore
👥 CHARACTER DYNAMICS: Develop relationships with allies, enemies, or mystical beings

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

STORYTELLING EXCELLENCE:
- Show immediate consequences of the previous choice
- Advance {character_name}'s quest or magical abilities
- Create moments of wonder, discovery, or heroism
- Include interactions with fantasy creatures, magic users, or quest-givers
- Build toward the next important adventure milestone

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Exploration: Discover new locations, investigate mysteries
- Social: Build alliances, help NPCs, negotiate
- Combat: Face dangers head-on, protect others
- Strategic: Plan carefully, gather information
- Magical: Use or learn magic, experiment with powers
- Diplomatic: Resolve conflicts peacefully
- Risk-taking: Take bold actions, attempt difficult feats
- Protective: Help others, prevent harm
- Mysterious: Follow clues, investigate secrets
- Cautious: Observe and plan before acting

Each choice must reference specific adventure elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and adventure-specific.

Continue the fantasy adventure in a way that makes readers excited to see {character_name}'s next move!

FORMAT:
[STORY]
(Your story here)
[/STORY]

[CHOICES]
1. (First dynamic choice based on your story)
2. (Second dynamic choice based on your story)
3. (Third dynamic choice based on your story)
[/CHOICES]
"""

        user_prompt = f"""Continue this fantasy adventure story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

Show the consequences of this choice and advance the story toward the next exciting decision point.

Format your response as:
[STORY]
(300-400 words of story content)
[/STORY]

[CHOICES]  
1. (First choice)
2. (Second choice)
3. (Third choice)
[/CHOICES]"""
        
        try:
            logger.info(f"Continuing fantasy adventure story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error continuing fantasy adventure story: {e}")
        except Exception as e:
            logger.error(f"Unexpected error continuing fantasy adventure story: {e}")
            # Contextual fallback based on the selected choice
            return BaseGenre.create_contextual_fallback(
                character_name, selected_choice, self.genre_context
            ) 