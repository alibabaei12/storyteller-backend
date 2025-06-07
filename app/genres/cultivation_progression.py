"""
Cultivation Progression genre implementation for manga-style progression stories.
"""
from typing import List, Tuple
import openai
import logging
from ..models import Choice
from ..base_genre import BaseGenre, Genre

# Set up logger
logger = logging.getLogger(__name__)


class CultivationProgression(Genre):
    """Cultivation progression story generator with manga-style weak-to-strong progression."""
    
    @property
    def genre_name(self) -> str:
        return "Cultivation Progression"
    
    @property 
    def genre_context(self) -> str:
        return "cultivation progression world"
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        language_complexity: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """
        Generate a manga-style cultivation progression story.
        
        This is optimized for manga readers who love:
        - Weak to strong progression
        - Hidden masters and secret techniques
        - Clear power systems and rankings
        - Fast-paced plot development
        """
        try:
            # Create gender-specific prompt addition
            gender_prompt = ""
            if character_gender == "male":
                gender_prompt = f"{character_name} is male. Use he/him pronouns."
            elif character_gender == "female":
                gender_prompt = f"{character_name} is female. Use she/her pronouns."
            elif character_gender == "non-binary":
                gender_prompt = f"{character_name} is non-binary. Use they/them pronouns."
            
            # Create language complexity prompt
            language_prompt = ""
            if language_complexity == "simple":
                language_prompt = "LANGUAGE: Use clear, simple language like popular manga. Short sentences, easy vocabulary. Perfect for fast reading."
            elif language_complexity == "moderate":
                language_prompt = "LANGUAGE: Use balanced language with some complex terms for cultivation concepts."
            elif language_complexity == "complex":
                language_prompt = "LANGUAGE: Use rich, sophisticated language with detailed cultivation terminology."
            
            # Import the origin profile method
            from app.ai_service import AIService
            
            # Create character origin profile with cultivation-specific context
            origin_prompt = AIService._create_character_origin_profile(character_origin, "cultivation")
            
            # Manga-specific system prompt
            system_prompt = f"""You are creating an opening chapter for a CULTIVATION PROGRESSION manga that hooks readers immediately.

CRITICAL SUCCESS FACTORS:
1. EMOTIONAL CONNECTION - Make readers care about the character personally within 3 sentences
2. CONCRETE DETAILS - Show, don't tell through specific scenes and sensory details
3. LOGICAL WORLD-BUILDING - Explain cultivation naturally through character experience
4. SLOWER EMOTIONAL PACING - Build attachment before revealing power systems
5. SPECIFIC STAKES - Clear, personal goals beyond just "getting stronger"

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

OPENING STRUCTURE:
- START WITH CHARACTER MOMENT: Show personality through a specific scene
- BUILD EMOTIONAL CONNECTION: Make readers sympathize with their struggle
- INTRODUCE WORLD NATURALLY: Cultivation system through character's perspective
- END WITH CLEAR STAKES: Specific goal that matters to the character

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

UNIQUE WORLD-BUILDING REQUIREMENTS:
- CREATIVE SECT NAMES: Avoid Azure/Jade/Golden - use unique names like "Thousand Stars Sect", "Iron Will Academy", "Shifting Sands Order"
- AUTHENTIC TECHNIQUES: Avoid Cloud/Dragon - use "Shattered Earth Palm", "Whisper Step", "Molten Forge Breathing"
- STAGE NAMES with levels (Qi Gathering 1-9 → Foundation Building 1-9 → Core Formation)
- VISUAL QI DESCRIPTIONS (specific colors: crimson, violet, silver, etc. with unique patterns)
- SECT HIERARCHY (Outer Disciple → Inner Disciple → Core Disciple → Elder)
- COMPETITIVE DYNAMICS (monthly rankings, seasonal trials, rival disciples with personalities)
- IMMEDIATE WORLD STAKES (sect wars brewing, ancient ruins discovered, demon beast invasions)

CHARACTER IMMERSION REQUIREMENTS:
- SPECIFIC APPEARANCE (not just hair/eyes - scars, height, build, distinctive clothing)
- CONCRETE DAILY SCENES (specific training failures, exact bullying incidents, meal struggles)
- PERSONAL EMOTIONAL STAKES (not parents' death - maybe protecting a younger friend, proving a teacher wrong, earning enough to buy medicine)
- UNIQUE PERSONALITY MOMENTS (how they react to mockery, what small things bring them joy)
- ORIGIN-DRIVEN ABILITIES: Let {character_name}'s {character_origin} background directly affect their cultivation style and capabilities

{gender_prompt}
{language_prompt}

PACING RULES:
- Start with CHARACTER MOMENT (show personality first)
- Add ONE world detail at a time through character's eyes
- Build emotional investment BEFORE explaining power systems
- End with clear personal stakes, not just power choices

AVOID:
- Generic sect names (Azure/Jade/Golden/Cloud/Sky/Heaven anything)
- Dead parents motivation (overused)
- Starting with power level explanations
- Exposition dumps about the world
- Mysterious heritage/bloodline reveals

Your goal: Create an opening that makes readers think "I'm already invested in this character and want to see them succeed!\""""

            # User prompt for cultivation progression
            user_prompt = f"""Create an opening chapter for a cultivation progression story featuring {character_name}.

CHARACTER SETUP:
{character_name} has a {character_origin} origin in a cultivation world where spiritual power determines everything. Use this origin to create a SPECIFIC backstory and clear motivation for wanting to get stronger that directly relates to their {character_origin} background.

WORLD-BUILDING REQUIREMENTS:
1. Define SPECIFIC cultivation stages (e.g., Qi Gathering 1-9 → Foundation Building → Core Formation)
2. Establish sect hierarchy (Outer Disciples → Inner Disciples → Core Disciples → Elders)
3. Give logical reasons for {character_name}'s current situation
4. Show where {character_name} fits in the power structure (current stage, sect rank)
5. Introduce competitive dynamics (rival disciples, ranking competitions, sect politics)

STORY STRUCTURE (SLOWER EMOTIONAL PACING):
- Start with a SPECIFIC SCENE showing {character_name}'s personality (not weakness first)
- Build EMOTIONAL CONNECTION through their daily struggles and small moments
- Gradually introduce ONE cultivation concept at a time through their experience
- Give them a FRESH, SPECIFIC motivation (not generic "prove worth" or dead parents)
- Include at least ONE named technique they're trying to learn
- Build to the major choice naturally through story events

DYNAMIC CHOICE GENERATION:
Based on the story you've written, create 3 meaningful choices that:
- Flow naturally from the story events and character's situation
- Offer genuinely different paths forward (not just different ways to do the same thing)
- Match the character's current power level and circumstances
- Appeal to different motivations (bold vs careful, social vs solo, etc.)
- Lead to different story developments in future chapters

CHOICE VARIETY REQUIREMENTS:
Create 3 choices that are COMPLETELY DIFFERENT in approach and motivation:

CHOICE APPROACHES (pick 3 DIFFERENT types for variety):
- EXPLORATION: Investigate mysteries, explore locations, discover secrets
- SOCIAL: Form alliances, build relationships, help others
- RISK-TAKING: Attempt dangerous techniques, take bold actions
- STRATEGIC: Gather intelligence, plan carefully, observe politics
- RULE-BREAKING: Defy authority, break restrictions, rebel
- DIPLOMATIC: Mediate conflicts, negotiate, find peaceful solutions
- TRAINING: Improve skills, practice techniques, strengthen weaknesses
- MYSTERIOUS: Follow clues, investigate strange phenomena
- BOLD: Volunteer for danger, make dramatic gestures
- PROTECTIVE: Defend others, guard secrets, prevent harm

AVOID REPETITIVE PATTERNS - Don't use the same choice types or structure!

WRITE 350-400 words that:
1. Start with a CHARACTER MOMENT showing {character_name}'s {character_origin} nature in action
2. Give them a FRESH, SPECIFIC motivation that stems from their {character_origin} background
3. Include at least ONE named technique they're learning that relates to their origin
4. Show how other characters react to {character_name} based on their {character_origin} nature
5. Show visual qi descriptions with specific colors and effects influenced by their origin
6. Hint at IMMEDIATE world stakes (demon beast attacks, sect wars, ancient ruins discovered)
7. Build to the path choices through natural story progression
8. Make reader think "I care about this {character_origin} character and want them to succeed!"

FRESH MOTIVATION EXAMPLES for orphaned characters:
- "Earn enough spirit stones to buy medicine for a sickly younger disciple he protects"
- "Become strong enough to find and rescue his missing sister" 
- "Prove a beloved teacher wrong who said he'd never amount to anything"
- "Master cultivation to help defend the sect from demon beast attacks that orphaned him"
- "Rise high enough to change the sect's cruel treatment of weak disciples"

Include MANGA ELEMENTS: Clear power levels, potential rivals, visual descriptions, technique names!

Format:
[STORY]
(Your story here)
[/STORY]

[CHOICES]
1. (First dynamic choice based on your story)
2. (Second dynamic choice based on your story)
3. (Third dynamic choice based on your story)
[/CHOICES]"""

            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating cultivation progression story: {e}")
            # Fallback for cultivation progression
        except Exception as e:
            logger.error(f"Unexpected error generating cultivation progression story: {e}")
            # Fallback for cultivation progression
            return BaseGenre.create_fallback_story(
                character_name,
                f"{character_name} stood at the bottom of the Outer Disciple rankings, mocked by all for having weak spiritual roots. "
                f"Determined to prove their worth and honor their family's memory, {character_name} faced a crucial decision about their cultivation path. "
                f"The upcoming sect trials offered a chance to advance, but other paths beckoned as well...",
                [
                    Choice(id="1", text="Train harder to improve cultivation base"),
                    Choice(id="2", text="Seek help from a senior disciple"),
                    Choice(id="3", text="Challenge a rival to prove worthiness")
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
        """
        Continue a cultivation progression story with manga pacing.
        """
        try:
            # Gender prompt
            gender_prompt = ""
            if character_gender == "male":
                gender_prompt = f"{character_name} is male. Use he/him pronouns."
            elif character_gender == "female":
                gender_prompt = f"{character_name} is female. Use she/her pronouns."
            elif character_gender == "non-binary":
                gender_prompt = f"{character_name} is non-binary. Use they/them pronouns."
            
            # Language complexity
            language_prompt = ""
            if language_complexity == "simple":
                language_prompt = "LANGUAGE: Use clear, simple language like popular manga. Keep it fast and engaging."
            elif language_complexity == "moderate":
                language_prompt = "LANGUAGE: Use balanced language with cultivation terminology."
            elif language_complexity == "complex":
                language_prompt = "LANGUAGE: Use rich language with detailed cultivation concepts."
            
            system_prompt = f"""You are continuing a CULTIVATION PROGRESSION manga story. Focus on logical progression and meaningful character development.

CONTINUATION CORE PRINCIPLES:
1. LOGICAL CONSEQUENCES - Show realistic results of their path choice
2. SLOWER PACING - One significant development per chapter, don't rush
3. VISIBLE PROGRESSION - Show tangible power-ups, new techniques, stage advancement
4. RIVALRY DYNAMICS - Include competitive relationships, jealous disciples, sect politics
5. WORLD CONSISTENCY - Maintain established cultivation rules and social structures
6. PATH-SPECIFIC CONTENT - Different paths should feel genuinely different
7. ESCALATING STAKES - Gradually introduce bigger threats and challenges

STRUCTURE:
- ARC-BASED PROGRESSION: Structure stories around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc)
- Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc
- No fixed end — the story evolves indefinitely based on player choices

PATH-SPECIFIC STORYTELLING:
- SECT PATH: Focus on trials, hierarchy, competition with other disciples
- MASTER PATH: Focus on personal training, secret techniques, one-on-one growth
- ACADEMY PATH: Focus on classes, academic competition, student relationships
- INDEPENDENT PATH: Focus on exploration, self-discovery, unique challenges

PACING REQUIREMENTS:
- Don't jump to legendary masters or ancient secrets immediately
- Build relationships and skills gradually over multiple interactions
- Show the character earning their progress through effort
- Let readers understand the cultivation system through experience

CULTIVATION PROGRESSION ELEMENTS:
- Clear STAGE ADVANCEMENT (show when MC moves from Qi Gathering 3 → 4, etc.)
- NAMED TECHNIQUES that characters learn (Flowing River Palm, Crane Step, etc.)
- Rival relationships that drive competition and growth
- VISUAL QI DESCRIPTIONS (silver qi, crackling energy, glowing auras)
- Concrete obstacles that match the character's current level
- Hints at larger threats beyond immediate training (sect conflicts, ancient enemies)

{gender_prompt}
{language_prompt}

AVOID:
- Rushing to high-level content too quickly
- Skipping logical steps in progression
- Introducing overpowered mentors without proper setup
- Repetitive "mysterious dark forces" plots

Your goal: Create compelling progression that feels earned and logical within the chosen path."""

            user_prompt = f"""Continue the cultivation progression story, showing the logical consequences of {character_name}'s path choice.

Previous story:
{previous_content}

Selected choice:
{selected_choice}

CONTINUATION APPROACH:
Analyze the choice {character_name} made and develop the story along that specific path. Each path should feel unique:

- SECT PATH: Show trials, meeting other disciples, learning sect rules and hierarchy
- MASTER PATH: Show the search for or training with a personal mentor
- ACADEMY PATH: Show entrance procedures, classes, academic and social dynamics
- INDEPENDENT PATH: Show solo exploration, self-discovery, unique challenges

PACING REQUIREMENTS:
1. ONE major development this chapter (don't rush through multiple stages)
2. Show logical, step-by-step progression appropriate to their current level
3. Introduce path-specific characters and challenges gradually
4. Build anticipation for the next logical step in their journey

CHARACTER DEVELOPMENT:
- Show {character_name} learning and adapting to their chosen path
- Display realistic challenges and small victories
- Demonstrate growing understanding of cultivation principles
- Create believable relationships with new characters

WRITE 300-350 words that:
1. Show realistic consequences of their path choice
2. Introduce appropriate characters (masters, rivals, fellow disciples) for their chosen path
3. Include ONE tangible progression marker (new technique learned, stage advancement, ability gained)
4. Present one significant challenge or learning opportunity
5. Add competitive dynamics (rivals, rankings, sect politics)
6. Use VISUAL descriptions (qi colors, energy effects, physical manifestations)
7. Build toward the next logical step in their progression
8. Hint at larger stakes or conflicts beyond immediate training

Focus on MANGA ELEMENTS: visible power-ups, named techniques, rivalry dynamics, visual descriptions!

Format:
[STORY]
(Your continuation here)
[/STORY]

[CHOICES]
1. [First specific choice based on your story - must be detailed and actionable]
2. [Second specific choice based on your story - must be detailed and actionable]
3. [Third specific choice based on your story - must be detailed and actionable]
[/CHOICES]

CRITICAL: Each choice must be SPECIFIC to your story content, not generic templates. Use concrete actions, people, places, and objects from your story. Each choice should be at least 12 words long and lead to different story directions."""

            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error continuing cultivation progression story: {e}")
            # Contextual fallback based on the selected choice
        except Exception as e:
            logger.error(f"Unexpected error continuing cultivation progression story: {e}")
            # Contextual fallback based on the selected choice
            return BaseGenre.create_contextual_fallback(
                character_name, selected_choice, self.genre_context
            ) 