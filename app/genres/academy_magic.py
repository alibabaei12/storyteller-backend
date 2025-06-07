"""
Academy Magic genre implementation for magic school stories.
"""
from typing import List, Tuple
import openai
import logging
from ..models import Choice
from ..base_genre import BaseGenre, Genre

# Set up logger
logger = logging.getLogger(__name__)


class AcademyMagic(Genre):
    """Academy magic story generator for magic school progression stories."""
    
    @property
    def genre_name(self) -> str:
        return "Academy Magic"
    
    @property
    def genre_context(self) -> str:
        return "magical academy environment"
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        language_complexity: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Generate an academy magic story optimized for school progression."""
        
        # Create language complexity prompt addition
        language_prompt = BaseGenre.create_language_prompt(language_complexity)
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Import the origin profile method
        from app.ai_service import AIService
        
        # Create character origin profile with academy-specific context
        origin_prompt = AIService._create_character_origin_profile(character_origin, "academy")
        
        system_prompt = f"""You are creating an engaging magic academy story in the style of popular manga/light novels like "The Irregular at Magic High School" and "Little Witch Academia."

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

ACADEMY MAGIC STORY REQUIREMENTS:
🎓 SCHOOL IMMERSION: Create a vivid magic academy with unique systems, not generic "magic school"
✨ MAGIC PROGRESSION: Establish clear magical ranking/grading systems with advancement potential
🎯 ACADEMY STAKES: Give {character_name} compelling academic goals (rankings, competitions, proving worth)
🏫 LIVING SCHOOL: Include specific classes, professors, dormitories, and academy traditions
👥 SCHOOL DYNAMICS: Create rivalries, friendships, and academic social hierarchies

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

ENGAGEMENT REQUIREMENTS:
- STUDENT CONNECTION: Make readers relate to {character_name}'s academic struggles within the first paragraph
- PROGRESSION SYSTEM: Show clear paths for magical and academic advancement
- COMPETITIVE EDGE: Present ranking systems, tournaments, or academic competitions
- VISUAL MAGIC: Use rich descriptions of spells, magical techniques, and academy architecture
- PERSONAL STAKES: Present challenges that matter to {character_name}'s future at the academy

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Academic: Study harder, research subjects, master techniques
- Social: Build friendships, handle rivalries, join groups
- Risk-taking: Break rules, explore forbidden areas
- Strategic: Plan for competitions, gather information
- Magical: Practice spells, experiment with power
- Protective: Help struggling classmates, prevent bullying
- Mysterious: Investigate academy secrets, follow clues
- Competitive: Challenge rivals, prove abilities
- Diplomatic: Mediate conflicts, form alliances
- Cautious: Observe situations, avoid trouble

Each choice must reference specific academy elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and academy-specific.

Generate an academy opening that makes readers think: "This magic school is fascinating and I want to see {character_name} rise through the ranks!"

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

        user_prompt = f"""Create an engaging magic academy story opening for {character_name} with a {character_origin} origin.

ORIGIN INTEGRATION REQUIREMENTS:
- Make {character_name}'s {character_origin} background central to their academy experience
- Show how their origin affects their magical abilities, academic standing, and relationships with classmates
- Include at least one moment where their {character_origin} nature creates academic advantages or challenges
- Let their origin influence their reputation and starting position at the academy

Make it feel like the start of an academy adventure with clear magical progression and social dynamics that relate to their {character_origin} background.

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
            logger.info(f"Generating academy magic story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating academy magic story: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating academy magic story: {e}")
            # Academy magic fallback
            return BaseGenre.create_fallback_story(
                character_name,
                f"{character_name} nervously clutched their acceptance letter to Arcanum Academy, the most prestigious magic school in the realm. "
                f"Despite being from a non-magical family, they had somehow manifested rare abilities that caught the academy's attention. "
                f"Now, standing in the grand entrance hall surrounded by students from powerful magical bloodlines, {character_name} realized they would need to prove themselves worthy of being here. "
                f"The first-year placement trials were about to begin, and rumor had it that those who failed would be expelled immediately...",
                [
                    Choice(id="1", text="Focus on studying magic theory to prepare for trials"),
                    Choice(id="2", text="Try to make allies among other first-year students"),
                    Choice(id="3", text="Quietly observe the competition to learn their weaknesses")
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
        """Continue an academy magic story."""
        
        # Create language complexity prompt addition
        language_prompt = BaseGenre.create_language_prompt(language_complexity)
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        system_prompt = f"""You are continuing an engaging magic academy story in the style of popular manga/light novels.

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

ACADEMY MAGIC CONTINUATION REQUIREMENTS:
🎯 ACADEMY PROGRESS: Show advancement in classes, rankings, or magical abilities
🌟 RAISE STAKES: Introduce academy competitions, threats, or mysteries
✨ MAGICAL GROWTH: Demonstrate {character_name}'s developing powers or knowledge
👥 RELATIONSHIP DYNAMICS: Develop friendships, rivalries, or mentorships
🏫 SCHOOL DEPTH: Add new academy locations, subjects, or traditions

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

STORYTELLING EXCELLENCE:
- Show immediate consequences of the previous choice
- Advance {character_name}'s academy standing or abilities
- Create moments of magical discovery or academic challenge
- Include interactions with classmates, teachers, or rivals
- Build toward the next important academy milestone

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Academic: Study, research, master subjects
- Social: Build friendships, handle rivalries, join groups
- Risk-taking: Break rules, explore forbidden areas
- Strategic: Plan for competitions, gather information
- Magical: Practice spells, experiment with power
- Protective: Help struggling classmates, prevent bullying
- Mysterious: Investigate academy secrets, follow clues
- Competitive: Challenge rivals, prove abilities
- Diplomatic: Mediate conflicts, form alliances
- Cautious: Observe situations, avoid trouble

Each choice must reference specific academy elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and academy-specific.

Continue the academy story in a way that makes readers excited to see {character_name}'s next move!

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

        user_prompt = f"""Continue this magic academy story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

Show the consequences of this choice and advance the story toward the next exciting academy challenge.

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
            logger.info(f"Continuing academy magic story for {character_name}")
            
            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error continuing academy magic story: {e}")
        except Exception as e:
            logger.error(f"Unexpected error continuing academy magic story: {e}")
                        # Contextual fallback based on the selected choice
            return BaseGenre.create_contextual_fallback(
                character_name, selected_choice, self.genre_context
            ) 