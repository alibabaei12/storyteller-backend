import os
import openai
import logging
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .models import Choice

# Set up logger
logger = logging.getLogger(__name__)

# Import genre implementations
from .genres.cultivation_progression import CultivationProgression
from .genres.fantasy_adventure import FantasyAdventure
from .genres.academy_magic import AcademyMagic
from .base_genre import BaseGenre

# Load environment variables
load_dotenv()

# Initialize OpenAI client
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except TypeError:
    # Fallback for older versions of the library
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1")

class AIService:
    """Service for generating story content using OpenAI API."""
    
    # Genre mapping for modular genre system
    # 🚀 TO ADD A NEW GENRE:
    # 1. Create a new file in app/genres/ (e.g., my_new_genre.py)
    # 2. Create a class that inherits from Genre (from base_genre.py)
    # 3. Implement the required methods: generate_story(), continue_story()
    # 4. Add properties: genre_name and genre_context
    # 5. Add your genre to this GENRE_MAP dictionary
    # 6. That's it! The system will automatically handle everything else.
    #
    # Example:
    # from .genres.my_new_genre import MyNewGenre
    # GENRE_MAP = {
    #     ...existing genres...
    #     "my_new_genre": MyNewGenre(),
    # }
    GENRE_MAP = {
        "cultivation_progression": CultivationProgression(),
        "fantasy_adventure": FantasyAdventure(),
        "academy_magic": AcademyMagic(),
        # Add new genres here following the pattern above
    }
    
    @staticmethod
    def generate_initial_story(
        character_name: str,
        character_gender: str,
        setting: str,
        tone: str,
        character_origin: str,
        language_complexity: str = "simple",
        manga_genre: str = None
    ) -> Tuple[str, List[Choice]]:
        """
        Generate the initial story content based on character parameters.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            logger.info(f"Generating initial story for {character_name} in {setting} setting, manga genre: {manga_genre}")
            
            # Check if this is a manga-specific genre using dynamic mapping
            if manga_genre and manga_genre in AIService.GENRE_MAP:
                selected_genre = AIService.GENRE_MAP[manga_genre]
                return selected_genre.generate_story(
                    character_name, character_gender, language_complexity, character_origin
                )
            
            # Fallback to original system for non-manga genres
            # Create setting-specific prompt addition
            setting_prompt = ""
            if setting == "modern":
                setting_prompt = "Create a story set in the modern world - contemporary cities, towns, everyday life with hidden secrets or mysteries."
            elif setting == "fantasy":
                setting_prompt = "Create a story in a magical fantasy world with wizards, dragons, enchanted forests, and mystical powers."
            elif setting == "scifi":
                setting_prompt = "Create a story in a futuristic world with advanced technology, space travel, and scientific wonders."
            elif setting == "academy":
                setting_prompt = "Create a story set in an educational setting - school, university, magical academy, or boarding school."
            elif setting == "historical":
                setting_prompt = "Create a story set in a past historical era - medieval times, ancient civilizations, Victorian era, or any historical period."
            elif setting == "gamelike":
                setting_prompt = "Create a story in a video game-inspired world with levels, skills, quests, and RPG mechanics."
            elif setting == "cultivation":
                setting_prompt = "Create a story set in an Eastern fantasy world where practitioners seek immortality through martial arts and spiritual cultivation."
            elif setting == "apocalypse":
                setting_prompt = "Create a story in a post-apocalyptic world where civilization has collapsed and survival is everything."
            
            # Create tone-specific prompt addition
            tone_prompt = ""
            if tone == "romantic":
                tone_prompt = "This is a ROMANCE story. Focus on love, relationships, emotional connections, sweet moments, and romantic tension. Avoid action, violence, or thriller elements."
            elif tone == "mystery":
                tone_prompt = "This is a MYSTERY story. Focus on puzzles to solve, secrets to uncover, clues to discover, and surprising revelations. Build intrigue and suspense around solving mysteries."
            elif tone == "adventure":
                tone_prompt = "This is an ADVENTURE story. Focus on exciting journeys, exploration, quests, and discovery. Include thrilling but not scary moments."
            elif tone == "thriller":
                tone_prompt = "This is a THRILLER story. Focus on suspense, danger, fast-paced action, and edge-of-your-seat tension. Create excitement through high stakes and unexpected twists."
            elif tone == "comedy":
                tone_prompt = "This is a COMEDY story. Focus on humor, amusing situations, funny characters, and light-hearted moments. Keep things fun and entertaining."
            elif tone == "drama":
                tone_prompt = "This is a DRAMA story. Focus on deep emotions, character development, meaningful relationships, and realistic conflicts with emotional weight."
            elif tone == "horror":
                tone_prompt = "This is a HORROR story. Focus on scary atmosphere, supernatural elements, dark themes, and spine-chilling moments that create fear and tension."
            elif tone == "slice-of-life":
                tone_prompt = "This is a SLICE OF LIFE story. Focus on realistic everyday moments, ordinary situations, character interactions, and the beauty in simple experiences."
            elif tone == "epic":
                tone_prompt = "This is an EPIC FANTASY story. Focus on grand heroic tales, larger-than-life adventures, epic quests, and legendary challenges."
            elif tone == "shonen":
                tone_prompt = "This is a SHONEN story. Focus on character growth, training arcs, overcoming limits, and progression from weak to strong. Include determination, friendship bonds, challenging opponents, and the drive to become better."
            elif tone == "philosophical":
                tone_prompt = "This is a DEEP & THOUGHTFUL story. Focus on contemplation, life's big questions, meaningful choices, and exploring existential themes."
            
            # Arc-based progression structure
            structure_prompt = "STRUCTURE: Arc-based progression - stories are organized around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc). Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc. No fixed end — the story evolves indefinitely based on player choices."
            
            # Create gender-specific prompt addition
            gender_prompt = ""
            if character_gender == "male":
                gender_prompt = "The main character is male. Use appropriate pronouns (he/him) when referencing the character."
            elif character_gender == "female":
                gender_prompt = "The main character is female. Use appropriate pronouns (she/her) when referencing the character."
            elif character_gender == "non-binary":
                gender_prompt = "The main character is non-binary. Use appropriate pronouns (they/them) when referencing the character."
            
            # Create language complexity prompt addition
            language_prompt = ""
            if language_complexity == "simple":
                language_prompt = "LANGUAGE STYLE: Use simple, clear language like manga or light novels. Keep sentences short and vocabulary accessible. Perfect for non-native speakers or casual reading."
            elif language_complexity == "moderate":
                language_prompt = "LANGUAGE STYLE: Use balanced language with some complex vocabulary, like popular fantasy novels. Accessible but engaging."
            elif language_complexity == "complex":
                language_prompt = "LANGUAGE STYLE: Use rich, sophisticated language with advanced vocabulary like classic literature. Be eloquent and beautiful in your prose."
            
            # Create character origin profile with detailed background influence
            origin_prompt = AIService._create_character_origin_profile(character_origin, setting)

            # Create the system prompt
            system_prompt = f"""You are creating an engaging manga/manhwa-style interactive story using clear visual storytelling, immediate stakes, and concise, impactful dialogue. Avoid verbose narration or overly descriptive language.

MANGA/MANHWA STORYTELLING RULES:
- Style: Visual, panel-based storytelling like manga/manhwa
- Pacing: Immediate, dynamic, visually clear scenes
- Dialogue: Short, impactful exchanges that showcase distinct personalities
- Visuals: Provide vivid visual descriptions - think manga panels
- Stakes: Establish clear and urgent challenges or threats immediately

{setting_prompt}
{tone_prompt}
{structure_prompt}
{gender_prompt}
{language_prompt}

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

🎌 PANEL-BASED STORYTELLING STRUCTURE:
Write exactly 6 panels that flow like manga/manhwa:

Panel 1 (Visual Scene Setup):
- Concise, vivid scene setup with specific location
- Immediate action or clear activity happening right now

Panel 2 (Character Introduction):
- {character_name} clearly introduced with appearance/position
- Short dialogue or internal thought (italicize thoughts)

Panel 3 (Immediate Conflict):
- Quick introduction of problem or rival character
- Tension through dialogue or immediate stakes

Panel 4 (Character Action):
- {character_name}'s skill-related action or ability attempt
- Brief dialogue or internal thought showing strategy

Panel 5 (Unexpected Development):
- Brief, visually striking unexpected event
- Short reactionary dialogue from characters

Panel 6 (Choice Setup):
- Lead directly into meaningful choice moment
- End with immediate decision needed

✅ REQUIRED FOR EACH PANEL:
- Clear visual positioning of characters
- Concise, punchy dialogue (max 2 sentences per character)
- Immediate, real-time action (no summaries)
- Visual details that readers can imagine as manga panels
- Named characters with distinct speaking styles

❌ STRICTLY AVOID:
- Passive voice or indirect narration
- Abstract descriptions ("mysterious energy", "profound truths")
- Overly literary language or poetic phrasing
- Internal reflections longer than one sentence
- Time skips or summary statements
- Verbose descriptions longer than 2 sentences per panel

🎯 DIALOGUE RULES:
- Keep character speech under 15 words per line
- Use distinct speaking patterns for each character
- Include character actions in parentheses when speaking
- Show personality through word choice and tone
- Use italics for internal thoughts only"""

            # Create the user prompt  
            user_prompt = f"""Create an engaging manga/manhwa-style opening scene using the 6-panel structure.

Character: {character_name} with {character_origin} origin
Setting: {setting}
Tone: {tone}

🎌 MANGA/MANHWA PANEL STRUCTURE (Follow Strictly):

Panel 1 (Setting & Visual Intro):
- Visually vivid scene setup (specific, concise location)
- Immediate action or clear activity happening right now

Panel 2 (Character Introduction - {character_name}):
- {character_name} clearly introduced (appearance, position, visual distinctiveness)  
- Short dialogue or clear internal thought (italicize internal thoughts)

Panel 3 (Immediate Conflict or Challenge):
- Quick introduction of clear problem or rival character
- Tension through dialogue or immediate stakes

Panel 4 ({character_name}'s Reaction & Skill):
- {character_name}'s skill-related action or ability attempt
- Brief dialogue or internal thought showing strategy/intelligence

Panel 5 (Unexpected Development):
- Brief, visually striking unexpected event
- Short reactionary dialogue from {character_name} or other characters

Panel 6 (Immediate Choices):
Provide three clear, meaningful manga/manhwa-style choices:
- Aggressive/action-oriented option  
- Smart, strategic, or intelligent approach
- Risky, mysterious, or curiosity-driven choice

📝 SETTING-SPECIFIC REQUIREMENTS FOR {setting.upper()}:
""" + ("""
🏫 ACADEMY SCENE REQUIREMENTS:
- Panel 1: Specific trial/test location (training room, examination hall, arena)
- Panel 2: Ali's current rank/level mentioned in dialogue
- Panel 3: Named instructor/rival with clear challenge
- Panel 4: Ali demonstrates specific skill or technique
- Panel 5: Trial complication or unexpected test element
- Panel 6: Choices affecting advancement/ranking
""" if setting == "academy" else """
⚡ CULTIVATION SCENE REQUIREMENTS:
- Panel 1: Specific cultivation location (beneath Wisdom Tree, training ground, sect hall)
- Panel 2: Ali practicing named technique or studying Qi patterns
- Panel 3: Named master/rival/senior disciple interrupts with challenge
- Panel 4: Ali attempts specific cultivation technique (name it clearly)
- Panel 5: Sudden sect emergency or mysterious cultivation event
- Panel 6: Choices affecting cultivation progress or sect standing

🔥 Required Cultivation Elements:
- Name specific techniques (e.g., "Whispering Wind Technique", "Qi Circle Formation")
- Show current cultivation stage/rank clearly
- Include Qi, spiritual energy, or cultivation-specific terms
- Visual cultivation effects (glowing, energy patterns, etc.)
""" if setting == "cultivation" else f"""
🌍 {setting.upper()} SCENE REQUIREMENTS:
- Panel 1: Specific location relevant to {setting} world
- Panel 2: Ali using {character_origin} background in this setting
- Panel 3: Setting-appropriate challenge or conflict
- Panel 4: Ali's unique skills/knowledge applied
- Panel 5: Unexpected development fitting the {setting} world
- Panel 6: Choices that advance the {setting} story
""") + f"""

✅ REQUIRED ELEMENTS (Every Panel Must Have):
- Clear visual positioning and character actions
- Concise, punchy dialogue (under 15 words per line)
- Visual details imaginable as manga panels
- Named characters with distinct personalities
- Immediate, real-time action only

❌ ABSOLUTELY FORBIDDEN:
- Passive voice or indirect narration
- Abstract descriptions ("mysterious energy", "profound truths")  
- Literary/poetic language longer than necessary
- Time skips ("later", "after hours", "the next day")
- Summary statements ("Ali had learned", "weeks of training")
- Internal monologues longer than one sentence

🎨 EXAMPLE PANEL FORMAT:
Panel 1:
Ali sits cross-legged beneath the massive Wisdom Tree, eyes tracing glowing Qi patterns in the air.

Panel 2:  
Ali (adjusting glasses, pencil behind ear): "If I adjust the Qi flow here, it should—"

Panel 3:
Rival Disciple (arms crossed, smirking): "Still stuck on theory, Ali? Some genius you are."

🚨 RESPONSE FORMAT (Use Exactly):
[STORY]
Panel 1:
(Your panel 1 text - 1-2 sentences max)

Panel 2:
(Your panel 2 text with dialogue - 1-2 sentences max)

Panel 3:
(Your panel 3 text with conflict - 1-2 sentences max)

Panel 4:
(Your panel 4 text with Ali's action - 1-2 sentences max)

Panel 5:
(Your panel 5 text with unexpected event - 1-2 sentences max)

Panel 6:
(Brief setup for choices - 1 sentence)
[/STORY]

[CHOICES]
1. (Aggressive/action choice - specific to your story)
2. (Strategic/smart choice - specific to your story)  
3. (Risky/mysterious choice - specific to your story)
[/CHOICES]"""

            # Call the OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            
            # Extract the content from the response
            response_text = response.choices[0].message.content
            
            # Parse the response with retry logic for better choice generation
            try:
                story_content, choices = AIService._parse_story_response_improved(response_text)
                logger.info(f"Generated initial story: {len(story_content)} chars and {len(choices)} choices")
                return story_content, choices
            except ValueError as parse_error:
                logger.warning(f"Initial story parsing failed, retrying: {parse_error}")
                # If parsing fails, try to regenerate with stricter instructions
                return AIService._retry_initial_story_generation_with_better_format(
                    system_prompt, user_prompt, character_name, setting
                )
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating initial story: {e}")
            return AIService._create_initial_story_fallback(character_name, setting)
        except Exception as e:
            logger.error(f"Unexpected error generating initial story: {e}")
            return AIService._create_initial_story_fallback(character_name, setting)

    @staticmethod
    def continue_story(
        character_name: str,
        character_gender: str,
        setting: str,
        tone: str,
        previous_content: str,
        selected_choice: str,
        language_complexity: str = "simple",
        manga_genre: str = None,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """
        Continue the story based on the selected choice.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            logger.info(f"Continuing story based on choice: {selected_choice}, manga genre: {manga_genre}")
            logger.debug(f"Previous content length: {len(previous_content)} chars")
            logger.debug(f"Character: {character_name}, Setting: {setting}, Tone: {tone}")
            
            # Check for manga-specific continuation using dynamic mapping
            if manga_genre and manga_genre in AIService.GENRE_MAP:
                logger.info(f"Using specialized genre handler: {manga_genre}")
                selected_genre = AIService.GENRE_MAP[manga_genre]
                return selected_genre.continue_story(
                    character_name, character_gender, previous_content, selected_choice, language_complexity, character_origin
                )
            
            # Fallback to original system for non-manga genres
            # Create setting-specific prompt addition
            setting_prompt = ""
            if setting == "modern":
                setting_prompt = "This is a story set in the modern world - contemporary cities, towns, everyday life with hidden secrets or mysteries."
            elif setting == "fantasy":
                setting_prompt = "This is a story in a magical fantasy world with wizards, dragons, enchanted forests, and mystical powers."
            elif setting == "scifi":
                setting_prompt = "This is a story in a futuristic world with advanced technology, space travel, and scientific wonders."
            elif setting == "academy":
                setting_prompt = "This is a story set in an educational setting - school, university, magical academy, or boarding school."
            elif setting == "historical":
                setting_prompt = "This is a story set in a past historical era - medieval times, ancient civilizations, Victorian era, or any historical period."
            elif setting == "gamelike":
                setting_prompt = "This is a story in a video game-inspired world with levels, skills, quests, and RPG mechanics."
            elif setting == "cultivation":
                setting_prompt = "This is a story set in an Eastern fantasy world where practitioners seek immortality through martial arts and spiritual cultivation."
            elif setting == "apocalypse":
                setting_prompt = "This is a story in a post-apocalyptic world where civilization has collapsed and survival is everything."
            
            # Create tone-specific prompt addition
            tone_prompt = ""
            if tone == "romantic":
                tone_prompt = "Continue the ROMANCE story. Keep focusing on love, relationships, emotional connections, sweet moments, and romantic development. Avoid action, violence, or thriller elements."
            elif tone == "mystery":
                tone_prompt = "Continue the MYSTERY story. Keep focusing on puzzles, secrets, clues, and revelations. Build intrigue around solving mysteries and uncovering truths."
            elif tone == "adventure":
                tone_prompt = "Continue the ADVENTURE story. Keep focusing on exciting journeys, exploration, quests, and discovery. Maintain thrilling but not scary elements."
            elif tone == "thriller":
                tone_prompt = "Continue the THRILLER story. Keep focusing on suspense, danger, fast-paced action, and tension. Maintain excitement through high stakes and twists."
            elif tone == "comedy":
                tone_prompt = "Continue the COMEDY story. Keep focusing on humor, amusing situations, funny moments, and light-hearted entertainment."
            elif tone == "drama":
                tone_prompt = "Continue the DRAMA story. Keep focusing on deep emotions, character development, meaningful relationships, and realistic emotional conflicts."
            elif tone == "horror":
                tone_prompt = "Continue the HORROR story. Keep focusing on scary atmosphere, supernatural elements, dark themes, and spine-chilling tension."
            elif tone == "slice-of-life":
                tone_prompt = "Continue the SLICE OF LIFE story. Keep focusing on realistic everyday moments, ordinary situations, and character interactions."
            elif tone == "epic":
                tone_prompt = "Continue the EPIC FANTASY story. Keep focusing on grand heroic tales, larger-than-life adventures, and legendary challenges."
            elif tone == "shonen":
                tone_prompt = "Continue the SHONEN story. Keep focusing on character growth, training, overcoming limits, and progression from weak to strong. Include determination, friendship bonds, and challenging obstacles."
            elif tone == "philosophical":
                tone_prompt = "Continue the DEEP & THOUGHTFUL story. Keep focusing on contemplation, life's big questions, and meaningful existential themes."
            
            # Arc-based progression structure
            structure_prompt = "STRUCTURE: Arc-based progression - stories are organized around sequential Arcs (e.g., Training Arc, Tournament Arc, Exploration Arc). Each Arc naturally lasts ~5–10 interactions, then transitions to a new Arc. No fixed end — the story evolves indefinitely based on player choices."
            
            # Create gender-specific prompt addition
            gender_prompt = ""
            if character_gender == "male":
                gender_prompt = "The main character is male. Use appropriate pronouns (he/him) when referencing the character."
            elif character_gender == "female":
                gender_prompt = "The main character is female. Use appropriate pronouns (she/her) when referencing the character."
            elif character_gender == "non-binary":
                gender_prompt = "The main character is non-binary. Use appropriate pronouns (they/them) when referencing the character."
            
            # Create language complexity prompt addition
            language_prompt = ""
            if language_complexity == "simple":
                language_prompt = "LANGUAGE STYLE: Use simple, clear language like manga or light novels. Keep sentences short and vocabulary accessible. Perfect for non-native speakers or casual reading."
            elif language_complexity == "moderate":
                language_prompt = "LANGUAGE STYLE: Use balanced language with some complex vocabulary, like popular fantasy novels. Accessible but engaging."
            elif language_complexity == "complex":
                language_prompt = "LANGUAGE STYLE: Use rich, sophisticated language with advanced vocabulary like classic literature. Be eloquent and beautiful in your prose."
            
            # Create character origin profile for continuation
            origin_prompt = AIService._create_character_origin_profile(character_origin, setting)
            
            # Create the system prompt
            system_prompt = f"""You are a light novel/manga storytelling genius who creates IMMERSIVE, DETAILED interactive fiction that hooks readers immediately.

{setting_prompt}
{tone_prompt}
{structure_prompt}
{gender_prompt}
{language_prompt}

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

🎯 SCENE-BASED STORYTELLING RULES:
1. SHOW SPECIFIC SCENES - Don't summarize, show what's happening right now
2. IMMEDIATE TENSION - Every passage needs conflict, challenge, or discovery
3. CONCRETE DETAILS - Specific locations, characters, dialogue, and actions
4. NO TIME SKIPS - Focus on the current moment and immediate consequences
5. VISUAL STORYTELLING - Help readers SEE and FEEL what's happening

🚫 FORBIDDEN PRACTICES:
- Time skipping ("weeks passed", "months later", "semester ended")
- Summarizing events ("Ali mastered the technique", "he became respected")
- Vague descriptions ("mysterious power", "ancient knowledge")
- Passive voice ("Ali was known for", "rumors circulated")
- Generic scenarios (just "training" or "studying")

✅ REQUIRED ELEMENTS:
- SPECIFIC CURRENT SCENE with clear setting and action
- IMMEDIATE STAKES that matter right now
- CONCRETE CHARACTERS with names and personalities
- DIALOGUE and direct character interaction
- SENSORY DETAILS (what Ali sees, hears, feels)
- CLEAR PROGRESSION markers (specific skills, ranks, achievements)

PACING MASTERY:
- Start with Ali in a SPECIFIC situation requiring immediate decision
- Show the challenge/conflict happening RIGHT NOW
- Include at least one other character Ali interacts with
- End with a choice that affects the immediate situation
- Make every word count toward building tension or character

Your goal: Make readers think "I need to know what happens next!" after every single passage.

WRITING APPROACH:
- CHANGE SOMETHING SIGNIFICANT - location, characters, situation, or knowledge
- BUILD ON PREVIOUS CHOICES - show how decisions shape the story path
- CREATE NEW INTRIGUE - introduce fresh mysteries or challenges
- AVOID REPETITION - don't rehash the same scenario or conflict
- PROGRESS THE NARRATIVE - move closer to resolution or deeper into complexity

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that unlock DIFFERENT story paths and content
2. Each choice should lead to new locations, characters, or plot developments
3. Offer meaningful alternatives that appeal to different story approaches
4. Avoid choices that all lead back to similar scenarios or conflicts

Your goal: Make readers think "This story keeps getting more interesting!" after every choice."""

            # Create the user prompt with BULLETPROOF formatting
            user_prompt = f"""Continue the story by showing a SPECIFIC SCENE with immediate consequences of {character_name}'s choice.

Previous content:
{previous_content}

Selected choice:
{selected_choice}

🎬 SCENE-BASED CONTINUATION RULES:
Show {character_name} in a SPECIFIC location dealing with the IMMEDIATE results of their choice:
- WHERE exactly is this happening? (specific room, area, location)
- WHO is present? (specific named characters, not generic people)
- WHAT is the immediate challenge or conflict they face?
- HOW does their {character_origin} background help or hinder in this moment?

🚫 ABSOLUTELY FORBIDDEN:
- Time skipping ("hours later", "the next day", "weeks passed")
- Summarizing ("Ali had learned", "Ali became known for")
- Vague outcomes ("Ali grew stronger", "his reputation improved")
- Generic descriptions ("mystical energy", "ancient power")
- Starting with exposition or background info

✅ REQUIRED ELEMENTS:
- SPECIFIC LOCATION: Where this scene is happening
- NAMED CHARACTERS: At least one other person Ali interacts with
- IMMEDIATE CHALLENGE: What Ali must handle right now
- DIALOGUE: Actual conversation between characters
- SENSORY DETAILS: What Ali sees, hears, feels
- CLEAR STAKES: Specific consequences for success/failure
- PROGRESSION: One concrete skill, ability, or understanding Ali gains

WRITE 250-300 words showing this ONE specific scene:
1. The immediate result of Ali's choice happening right now
2. A named character reacting to or causing this result
3. A new challenge or opportunity emerging from this
4. Clear progression (specific skill learned, rank gained, secret discovered)
5. Dialogue and sensory details that make it vivid

Make me feel like I'm watching this specific scene happen right now!

🚨 ABSOLUTELY CRITICAL FORMATTING RULES 🚨
You MUST follow this EXACT format. Any deviation will cause system failure.

1. Write exactly "STORY:" (with colon)
2. Write your 200-300 word story continuation
3. Write exactly "CHOICES:" (with colon)  
4. Write exactly three choices, each starting with "1.", "2.", "3."
5. Each choice must be specific to your story and at least 12 words long

EXACT FORMAT EXAMPLE:
STORY:
{character_name} stepped forward, drawing upon their {character_origin} background as they faced the consequences of their decision. The mysterious door creaked open, revealing a chamber filled with ancient artifacts that seemed to pulse with otherworldly energy...

CHOICES:
1. Examine the glowing crystal in the center of the chamber that seems to react to your presence
2. Approach the ancient scrolls scattered on the stone table to decipher their mysterious symbols  
3. Investigate the shadowy figure you glimpsed moving between the towering shelves of artifacts

🚫 FORBIDDEN WORDS/PHRASES (NEVER USE):
- "continue your journey"
- "choose your path" 
- "what will you do"
- "(exploration)" or "(strategic)" or any parentheses
- "→" arrows
- "reflect on" or "consider your options"
- "move forward" or "proceed with"

✅ REQUIRED:
- Each choice must contain specific story elements from your narrative
- Each choice must be actionable and detailed
- Each choice must lead to different story directions
- Use STORY: and CHOICES: labels exactly as shown

Write your response now using the exact format above."""

            # Call the OpenAI API
            logger.info(f"🔥 CALLING OPENAI API FOR STORY CONTINUATION")
            logger.debug(f"System prompt length: {len(system_prompt)} chars")
            logger.debug(f"User prompt length: {len(user_prompt)} chars")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1200,  # ✅ INCREASED FROM 800
                stop=["[/STORY]", "[/CHOICES]"]  # ✅ ADDED STOP TOKENS
            )
            
            # Extract the content from the response
            response_text = response.choices[0].message.content
            
            # ✅ LOG THE FULL RESPONSE TO SEE WHAT GPT ACTUALLY RETURNS
            logger.info(f"📝 FULL AI RESPONSE ({len(response_text)} chars):")
            logger.info("=" * 80)
            logger.info(response_text)
            logger.info("=" * 80)
            
            # Parse the response with improved logic to prevent generic choices
            try:
                story_content, choices = AIService._parse_story_response_improved(response_text)
                logger.info(f"Generated continuation: {len(story_content)} chars and {len(choices)} choices")
                return story_content, choices
            except ValueError as parse_error:
                logger.warning(f"Story parsing failed, retrying: {parse_error}")
                logger.debug(f"Failed response text: {response_text[:1000]}...")
                # Try one retry with better formatting, but don't fail completely
                try:
                    return AIService._retry_story_generation_with_better_format(
                        system_prompt, user_prompt, character_name, setting, selected_choice
                    )
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    # Instead of using fallback, try to extract what we can from original response
                    logger.info("Attempting to salvage content from original GPT response")
                    try:
                        # Use the emergency parsing from the original response
                        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                        
                        # Find substantial content
                        story_candidates = [line for line in lines if len(line) > 30 and not line.startswith(('1.', '2.', '3.'))]
                        if story_candidates:
                            salvaged_story = ' '.join(story_candidates[:2])  # Take first couple lines
                        else:
                            salvaged_story = f"{character_name} follows through with their choice. The consequences begin to unfold..."
                        
                        # Find any numbered choices
                        import re
                        salvaged_choices = []
                        for line in lines:
                            if re.match(r'^\d+[\.\)]\s*', line) and len(line) > 15:
                                choice_text = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                                if choice_text:
                                    salvaged_choices.append(Choice(id=str(len(salvaged_choices) + 1), text=choice_text))
                        
                        # Fill to 3 choices
                        while len(salvaged_choices) < 3:
                            num = len(salvaged_choices) + 1
                            salvaged_choices.append(Choice(id=str(num), text=f"Explore this situation further (Option {num})"))
                        
                        logger.info(f"Salvaged content: {len(salvaged_story)} chars, {len(salvaged_choices)} choices")
                        return salvaged_story, salvaged_choices[:3]
                    except Exception as salvage_error:
                        logger.error(f"Content salvage failed: {salvage_error}")
                        # Only now fall back to contextual fallback as last resort
                        return AIService._create_contextual_api_fallback(character_name, setting, selected_choice)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error continuing story: {e}")
            return AIService._create_contextual_api_fallback(character_name, setting, selected_choice)
        except Exception as e:
            logger.error(f"Unexpected error continuing story: {e}")
            return AIService._create_contextual_api_fallback(character_name, setting, selected_choice)

    @staticmethod
    def _retry_story_generation_with_better_format(
        system_prompt: str, 
        user_prompt: str, 
        character_name: str, 
        setting: str, 
        selected_choice: str
    ) -> Tuple[str, List[Choice]]:
        """
        Multiple retry attempts with different prompting strategies.
        """
        # ATTEMPT 1: Ultra-simple format
        try:
            simple_prompt = f"""Continue this story: {character_name} decided to {selected_choice}.

Write a 200-word story continuation, then write exactly 3 choices.

Use this EXACT format:
STORY:
Your story here...

CHOICES:
1. First specific choice (at least 12 words)
2. Second specific choice (at least 12 words)  
3. Third specific choice (at least 12 words)

Each choice must be specific and actionable, not generic."""

            logger.info(f"Retry attempt 1: Ultra-simple format for {character_name}")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative storyteller. Follow the format exactly."},
                    {"role": "user", "content": simple_prompt}
                ],
                temperature=0.7,
                max_tokens=1200,
            )
            
            response_text = response.choices[0].message.content
            story_content, choices = AIService._parse_story_response_improved(response_text)
            
            logger.info(f"Retry attempt 1 successful: {len(choices)} choices")
            return story_content, choices
            
        except Exception as e1:
            logger.warning(f"Retry attempt 1 failed: {e1}")
            
            # ATTEMPT 2: Alternative format with different instructions
            try:
                alt_prompt = f"""You are continuing an interactive story. The character chose: {selected_choice}

Write what happens next in 200 words, then provide 3 specific choices.

Format:
STORY:
[Write continuation here]

CHOICES:  
1. [Detailed choice option]
2. [Detailed choice option]
3. [Detailed choice option]

Make each choice specific to the story - no generic phrases."""

                logger.info(f"Retry attempt 2: Alternative format for {character_name}")
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You write engaging interactive fiction. Be specific and creative."},
                        {"role": "user", "content": alt_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=800,
                )
                
                response_text = response.choices[0].message.content
                story_content, choices = AIService._parse_story_response_improved(response_text)
                
                logger.info(f"Retry attempt 2 successful: {len(choices)} choices") 
                return story_content, choices
                
            except Exception as e2:
                logger.warning(f"Retry attempt 2 failed: {e2}")
                
                # ATTEMPT 3: Last resort with super explicit instructions
                try:
                    explicit_prompt = f"""Continue this story where {character_name} chose: {selected_choice}

INSTRUCTIONS:
1. Write "STORY:" then write 200 words continuing the story
2. Write "CHOICES:" then write exactly 3 numbered choices
3. Each choice must be at least 15 words and relate to your story

EXAMPLE FORMAT:
STORY:
Character does something interesting based on their choice...

CHOICES:
1. Take a specific action related to what just happened in the story above
2. Try a different specific approach to handle the situation described
3. Investigate or explore something mentioned in the story content

NOW WRITE YOUR RESPONSE:"""

                    logger.info(f"Retry attempt 3: Explicit format for {character_name}")
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Follow the format exactly. Be creative and specific."},
                            {"role": "user", "content": explicit_prompt}
                        ],
                        temperature=0.6,
                        max_tokens=800,
                    )
                    
                    response_text = response.choices[0].message.content
                    story_content, choices = AIService._parse_story_response_improved(response_text)
                    
                    logger.info(f"Retry attempt 3 successful: {len(choices)} choices")
                    return story_content, choices
                    
                except Exception as e3:
                    logger.error(f"All retry attempts failed: {e1}, {e2}, {e3}")
                    # Final fallback to contextual choices
                    return AIService._create_contextual_api_fallback(character_name, setting, selected_choice)
    
    @staticmethod
    def _create_contextual_api_fallback(
        character_name: str, 
        setting: str, 
        selected_choice: str
    ) -> Tuple[str, List[Choice]]:
        """
        Create high-quality contextual fallback content that creates compelling, specific choices.
        This is a last resort but should still produce engaging story content.
        """
        # Extract key actions/themes from the selected choice
        choice_lower = selected_choice.lower()
        
        # Create a more detailed story continuation based on the choice
        if "explore" in choice_lower or "investigate" in choice_lower:
            story_content = f"{character_name} moves forward with purpose, their footsteps echoing in the mysterious space. " \
                           f"As they investigate deeper, strange details emerge - symbols carved into surfaces, " \
                           f"the faint scent of something otherworldly, and shadows that seem to move independently. " \
                           f"The air itself feels charged with potential, as if this place holds secrets that could " \
                           f"change everything they thought they knew about their world..."
            
            if setting in ["fantasy", "cultivation"]:
                choices = [
                    Choice(id="1", text="Channel your magical senses to detect the source of the otherworldly energy emanating from deeper within"),
                    Choice(id="2", text="Examine the carved symbols more closely to decipher their ancient meaning and origin"),
                    Choice(id="3", text="Follow the moving shadows cautiously to discover what intelligent force might be controlling them")
                ]
            elif setting in ["scifi", "gamelike"]:
                choices = [
                    Choice(id="1", text="Activate advanced scanning protocols to analyze the technological anomalies you've discovered here"),
                    Choice(id="2", text="Interface with the mysterious symbols to determine if they're part of an alien communication system"),
                    Choice(id="3", text="Track the movement patterns using motion sensors to identify the artificial intelligence behind them")
                ]
            else:
                choices = [
                    Choice(id="1", text="Document everything you've found and search for additional clues about this place's true purpose"),
                    Choice(id="2", text="Test your theories about the symbols by interacting with them in different ways"),
                    Choice(id="3", text="Set up surveillance to monitor the area and gather more information about these phenomena")
                ]
                
        elif "social" in choice_lower or "alliance" in choice_lower or "talk" in choice_lower:
            story_content = f"{character_name} takes a deep breath and approaches the situation with diplomatic intentions. " \
                           f"The initial conversation reveals layers of complexity - hidden motivations, unspoken tensions, " \
                           f"and the delicate balance of competing interests. Each word carries weight, and {character_name} " \
                           f"realizes that this social interaction could either open doors to powerful new alliances or " \
                           f"create dangerous enemies depending on how carefully they navigate these treacherous waters..."
            
            if setting in ["fantasy", "cultivation"]:
                choices = [
                    Choice(id="1", text="Demonstrate your cultivation abilities tactfully to establish credibility without appearing threatening"),
                    Choice(id="2", text="Share knowledge of rare techniques or ancient lore to prove your value as a potential ally"),
                    Choice(id="3", text="Propose a formal alliance ceremony bound by spiritual oaths that neither party can easily break")
                ]
            elif setting in ["academy", "modern"]:
                choices = [
                    Choice(id="1", text="Organize a private meeting with key decision-makers to discuss mutually beneficial arrangements"),
                    Choice(id="2", text="Leverage your reputation and past achievements to gain the trust and respect you need"),
                    Choice(id="3", text="Propose a collaborative project that showcases everyone's strengths while building lasting relationships")
                ]
            else:
                choices = [
                    Choice(id="1", text="Offer concrete assistance with their current challenges to demonstrate your commitment and reliability"),
                    Choice(id="2", text="Reveal strategic information that proves your trustworthiness while maintaining necessary secrets"),
                    Choice(id="3", text="Arrange a formal agreement that benefits all parties while protecting your own interests")
                ]
                
        elif "train" in choice_lower or "practice" in choice_lower or "technique" in choice_lower:
            story_content = f"{character_name} dedicates themselves to intensive training, pushing their limits in ways they never have before. " \
                           f"The familiar becomes challenging as they discover new depths to abilities they thought they understood. " \
                           f"Sweat beads on their forehead as breakthrough moments alternate with frustrating plateaus. " \
                           f"Yet through persistence and focused effort, {character_name} begins to sense transformations occurring - " \
                           f"not just in their capabilities, but in their understanding of their own potential..."
            
            if setting in ["fantasy", "cultivation"]:
                choices = [
                    Choice(id="1", text="Attempt to break through to the next cultivation realm by channeling all your accumulated spiritual energy"),
                    Choice(id="2", text="Master an advanced combat technique that combines multiple elements in a way others consider impossible"),
                    Choice(id="3", text="Seek out a legendary training ground rumored to enhance abilities beyond normal limitations")
                ]
            elif setting in ["academy", "gamelike"]:
                choices = [
                    Choice(id="1", text="Challenge yourself with the most difficult advanced curriculum to accelerate your learning exponentially"),
                    Choice(id="2", text="Develop an innovative training method that maximizes efficiency while minimizing traditional limitations"),
                    Choice(id="3", text="Form an elite training group with other exceptional students to push each other beyond normal boundaries")
                ]
            else:
                choices = [
                    Choice(id="1", text="Design a personalized training regimen that targets your specific weaknesses while enhancing your natural strengths"),
                    Choice(id="2", text="Seek mentorship from a master practitioner who can guide your development to unprecedented levels"),
                    Choice(id="3", text="Experiment with unconventional training methods that others might consider risky or unorthodox")
                ]
                
        elif "confront" in choice_lower or "challenge" in choice_lower or "fight" in choice_lower:
            story_content = f"{character_name} steps forward with unwavering resolve, ready to face whatever challenge awaits. " \
                           f"The tension in the air is palpable as opposing forces size each other up, each looking for " \
                           f"weaknesses and advantages. This confrontation represents more than just a simple conflict - " \
                           f"it's a test of will, skill, and determination that could reshape {character_name}'s entire future. " \
                           f"The outcome will depend not just on raw power, but on strategy, timing, and the courage to act decisively..."
            
            if setting in ["fantasy", "cultivation"]:
                choices = [
                    Choice(id="1", text="Unleash your most powerful cultivation technique in a decisive first strike to end the conflict quickly"),
                    Choice(id="2", text="Engage in prolonged combat to test your abilities while looking for your opponent's weaknesses"),
                    Choice(id="3", text="Use psychological warfare and tactical maneuvering to gain advantage without relying solely on brute force")
                ]
            elif setting in ["academy", "modern"]:
                choices = [
                    Choice(id="1", text="Present overwhelming evidence and logical arguments to discredit your opponent's position completely"),
                    Choice(id="2", text="Rally support from influential allies who can apply pressure through official channels"),
                    Choice(id="3", text="Engage in a public debate or competition where the outcome will be witnessed by many")
                ]
            else:
                choices = [
                    Choice(id="1", text="Take immediate decisive action to gain the upper hand before your opponent can properly respond"),
                    Choice(id="2", text="Engage strategically while gathering intelligence about your opponent's true capabilities and intentions"),
                    Choice(id="3", text="Attempt to turn the confrontation into an opportunity for mutual benefit rather than mutual destruction")
                ]
        else:
            # Default high-quality fallback for any other choices
            story_content = f"{character_name} commits fully to their chosen path, understanding that this decision will " \
                           f"have far-reaching consequences. As they move forward, new opportunities and challenges emerge " \
                           f"that they hadn't anticipated. The world around them seems to respond to their determination, " \
                           f"presenting both rewards for their boldness and tests of their resolve. Each step forward " \
                           f"reveals more about both the external world and their own inner capabilities..."
            
            if setting in ["fantasy", "cultivation"]:
                choices = [
                    Choice(id="1", text="Harness the mystical energies you've awakened to explore previously inaccessible realms of power"),
                    Choice(id="2", text="Seek guidance from ancient spirits or powerful cultivators who might recognize your potential"),
                    Choice(id="3", text="Venture into legendary locations where you can test your abilities against formidable challenges")
                ]
            elif setting in ["scifi", "gamelike"]:
                choices = [
                    Choice(id="1", text="Interface with advanced systems to unlock new technological capabilities that match your ambitions"),
                    Choice(id="2", text="Collaborate with other exceptional individuals to achieve goals that require combined expertise"),
                    Choice(id="3", text="Accept a high-risk mission that could lead to extraordinary rewards or catastrophic failure")
                ]
            else:
                choices = [
                    Choice(id="1", text="Pursue ambitious goals that others consider impossible but that align perfectly with your vision"),
                    Choice(id="2", text="Build the relationships and resources necessary to support your increasingly complex objectives"),
                    Choice(id="3", text="Take calculated risks that could either elevate you to new heights or teach you valuable lessons")
                ]
        
        logger.info(f"Created high-quality contextual fallback for {character_name} based on choice: {selected_choice}")
        return story_content, choices

    @staticmethod
    def _retry_initial_story_generation_with_better_format(
        system_prompt: str, 
        user_prompt: str, 
        character_name: str, 
        setting: str
    ) -> Tuple[str, List[Choice]]:
        """
        Retry initial story generation with stricter formatting instructions.
        """
        try:
            # Enhanced user prompt with stricter formatting requirements
            enhanced_prompt = f"""{user_prompt}

CRITICAL FORMATTING REQUIREMENTS:
- Your response MUST include [STORY] and [/STORY] tags around the story content
- Your response MUST include [CHOICES] and [/CHOICES] tags around the choices
- Each choice MUST be on a separate line, numbered (1. , 2. , 3. )
- Choices MUST be specific to the story content, not generic
- Example format:

[STORY]
Your story content here...
[/STORY]

[CHOICES]
1. Specific choice related to the story
2. Another specific choice related to the story  
3. Third specific choice related to the story
[/CHOICES]"""

            logger.info(f"Retrying initial story generation with enhanced formatting for {character_name}")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            
            response_text = response.choices[0].message.content
            story_content, choices = AIService._parse_story_response_improved(response_text)
            
            logger.info(f"Initial story retry successful: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            logger.error(f"Initial story retry failed: {e}")
            # Use contextual fallback as last resort
            return AIService._create_initial_story_fallback(character_name, setting)
    
    @staticmethod
    def _create_initial_story_fallback(
        character_name: str, 
        setting: str
    ) -> Tuple[str, List[Choice]]:
        """
        Create contextual fallback content for initial stories.
        """
        # Create setting-appropriate initial story content
        if setting in ["fantasy", "cultivation"]:
            story_content = f"Welcome to your adventure, {character_name}. You find yourself in a world where " \
                           f"magic and mystery shape every moment. Ancient powers stir, and destiny calls to those " \
                           f"brave enough to answer. Your journey begins now, and the choices you make will determine " \
                           f"whether you rise to greatness or fall to the challenges ahead..."
            
            choices = [
                Choice(id="1", text="Embrace the magical energies and begin training"),
                Choice(id="2", text="Seek out a wise mentor to guide your journey"),
                Choice(id="3", text="Explore the ancient mysteries of this world")
            ]
        elif setting in ["scifi", "gamelike"]:
            story_content = f"Welcome to your adventure, {character_name}. In this world of advanced technology " \
                           f"and digital possibilities, you stand at the threshold of something extraordinary. " \
                           f"Systems analyze, data flows, and opportunities await those who can navigate " \
                           f"the complexities of this high-tech realm..."
            
            choices = [
                Choice(id="1", text="Access the advanced systems and begin your mission"),
                Choice(id="2", text="Analyze the available data before making a move"),
                Choice(id="3", text="Connect with other users in this digital realm")
            ]
        elif setting in ["academy", "modern"]:
            story_content = f"Welcome to your adventure, {character_name}. In this familiar yet extraordinary " \
                           f"world, ordinary life hides remarkable secrets. Whether in academic halls or city " \
                           f"streets, your story is about to unfold in ways you never imagined..."
            
            choices = [
                Choice(id="1", text="Focus on your studies and academic pursuits"),
                Choice(id="2", text="Build connections with friends and peers"),
                Choice(id="3", text="Investigate the mysteries hidden in plain sight")
            ]
        else:
            story_content = f"Welcome to your adventure, {character_name}. Your journey begins in a world " \
                           f"filled with possibilities and challenges. Every choice will shape your path, " \
                           f"and destiny awaits those bold enough to seize it..."
            
            choices = [
                Choice(id="1", text="Begin your adventure with confidence"),
                Choice(id="2", text="Carefully observe your surroundings first"),
                Choice(id="3", text="Seek guidance before making important decisions")
            ]
        
        logger.info(f"Created initial story fallback for {character_name} in {setting} setting")
        return story_content, choices

    @staticmethod
    def _create_character_origin_profile(character_origin: str, setting: str) -> str:
        """
        Create detailed character origin profile that influences story, abilities, and interactions.
        """
        
        origin_profiles = {
            "reincarnated": {
                "core_traits": [
                    "Retains memories from their previous life in a different world/time",
                    "Has knowledge of events, people, or techniques from before",
                    "May recognize places, people, or situations from past life",
                    "Often struggles with identity - who were they vs who are they now?",
                    "Possesses wisdom beyond their apparent age or experience"
                ],
                "unique_abilities": [
                    "Knowledge of future events or patterns",
                    "Skills or techniques from their previous life",
                    "Ability to predict people's actions based on past experience",
                    "Understanding of hidden truths or connections others miss",
                    "Mental resistance to illusions or manipulation due to dual life experience"
                ],
                "social_dynamics": [
                    "Others may sense something 'different' about them",
                    "Some may be suspicious of their unusual knowledge or insights",
                    "Old enemies or allies from previous life may recognize them",
                    "Struggles to form new relationships while carrying old memories",
                    "May slip up and reveal knowledge they shouldn't have"
                ],
                "internal_conflicts": [
                    "Torn between old identity and new life",
                    "Guilt over mistakes from previous life",
                    "Fear of repeating past failures",
                    "Longing for people or places from their past life",
                    "Uncertainty about their purpose in this new life"
                ]
            },
            
            "weak": {
                "core_traits": [
                    "Significantly weaker than others in terms of raw power/ability",
                    "Often underestimated or dismissed by others",
                    "Has to rely on intelligence, strategy, and determination",
                    "May have hidden potential waiting to be unlocked",
                    "Often faces ridicule or pity from stronger individuals"
                ],
                "unique_abilities": [
                    "Exceptional strategic thinking to overcome disadvantages",
                    "Ability to find creative solutions others miss",
                    "High empathy and understanding of fellow underdogs",
                    "Determination and resilience beyond normal limits",
                    "Talent for inspiring others who feel powerless"
                ],
                "social_dynamics": [
                    "Frequently bullied or looked down upon",
                    "Forms strong bonds with other outcasts or kind individuals",
                    "Surprises people when they overcome challenges despite weakness",
                    "May have protectors who see their potential",
                    "Often has to prove their worth repeatedly"
                ],
                "internal_conflicts": [
                    "Deep insecurity about their lack of power",
                    "Jealousy towards those naturally stronger",
                    "Fear of being a burden to others",
                    "Determination to prove their worth",
                    "Struggling with self-doubt while maintaining hope"
                ]
            },
            
            "hidden": {
                "core_traits": [
                    "Conceals their true identity, power, or background",
                    "Lives a double life or maintains a false persona",
                    "Has powerful abilities or connections they must keep secret",
                    "May be royalty, nobility, or have dangerous enemies",
                    "Constantly vigilant about maintaining their cover"
                ],
                "unique_abilities": [
                    "Exceptional acting and deception skills",
                    "Access to powerful abilities they rarely use",
                    "Knowledge of high society, politics, or secret organizations",
                    "Ability to blend in and gather information unnoticed",
                    "Hidden resources, wealth, or influential connections"
                ],
                "social_dynamics": [
                    "Forms relationships while maintaining emotional distance",
                    "Others may sense they're hiding something",
                    "Risk of being discovered by enemies or rivals",
                    "Struggles with trust and genuine intimacy",
                    "May have loyal retainers or guardians watching over them"
                ],
                "internal_conflicts": [
                    "Longing for authentic relationships vs. need for secrecy",
                    "Guilt over deceiving people they care about",
                    "Fear of their true identity being discovered",
                    "Responsibility for protecting others by staying hidden",
                    "Questioning whether their hidden life is worth living"
                ]
            },
            
            "normal": {
                "core_traits": [
                    "Appears completely ordinary with no special background",
                    "Has to work hard for everything they achieve",
                    "Represents the 'everyman' in extraordinary circumstances",
                    "Often underestimated but has hidden depths",
                    "Grounded perspective that others lack"
                ],
                "unique_abilities": [
                    "Strong sense of empathy and understanding of common people",
                    "Practical problem-solving without relying on special powers",
                    "Ability to unite different types of people",
                    "Common sense that proves invaluable in complex situations",
                    "Determination to succeed despite lack of advantages"
                ],
                "social_dynamics": [
                    "Easily relates to ordinary people and gains their trust",
                    "May be overlooked by those seeking powerful allies",
                    "Often becomes the heart of a group due to their humanity",
                    "Bridges gaps between different social classes or factions",
                    "Proves that ordinary people can achieve extraordinary things"
                ],
                "internal_conflicts": [
                    "Feeling inadequate compared to special individuals",
                    "Pressure to prove they belong among the extraordinary",
                    "Fear of being left behind as others grow in power",
                    "Maintaining humility while achieving great things",
                    "Questioning their purpose in a world of heroes and legends"
                ]
            },
            
            "genius": {
                "core_traits": [
                    "Possesses exceptional intelligence or learning ability",
                    "Learns new skills and concepts at an extraordinary rate",
                    "Often bored by things that challenge others",
                    "May struggle with social connections due to intellectual gap",
                    "Has innovative approaches to problems others find impossible"
                ],
                "unique_abilities": [
                    "Rapid mastery of new techniques or knowledge",
                    "Ability to see patterns and connections others miss",
                    "Innovative problem-solving and creative thinking",
                    "Eidetic memory or perfect recall of information",
                    "Intuitive understanding of complex systems"
                ],
                "social_dynamics": [
                    "Often isolated due to intellectual superiority",
                    "May be sought after as a valuable ally or advisor",
                    "Struggles to explain concepts in terms others understand",
                    "Can accidentally make others feel stupid or inadequate",
                    "May be envied or resented for their natural gifts"
                ],
                "internal_conflicts": [
                    "Loneliness from being intellectually isolated",
                    "Pressure to live up to their potential",
                    "Boredom with challenges that don't engage their full abilities",
                    "Guilt over advantages others don't have",
                    "Fear that their intelligence is all they're valued for"
                ]
            },
            
            "fallen": {
                "core_traits": [
                    "Once held high status, power, or position but lost it",
                    "Carries the memories and skills of their former glory",
                    "May be seeking redemption, revenge, or restoration",
                    "Often bitter about their current circumstances",
                    "Still possesses the bearing and knowledge of their past position"
                ],
                "unique_abilities": [
                    "Refined skills and training from their former high position",
                    "Knowledge of high society, politics, or powerful organizations",
                    "Leadership abilities and strategic thinking",
                    "Understanding of both privilege and loss",
                    "Connections to their former world (both allies and enemies)"
                ],
                "social_dynamics": [
                    "May be recognized by former associates",
                    "Struggles with loss of respect and status",
                    "Some may pity them while others may gloat",
                    "Has to prove their worth without their former advantages",
                    "May encounter those responsible for their fall"
                ],
                "internal_conflicts": [
                    "Grief over their lost status and identity",
                    "Anger at those who caused their downfall",
                    "Pride preventing them from accepting help",
                    "Determination to regain what they've lost",
                    "Learning to find value beyond power and status"
                ]
            }
        }
        
        if character_origin not in origin_profiles:
            return f"{character_origin.capitalize()} origin - integrate this background naturally into the story."
        
        profile = origin_profiles[character_origin]
        
        # Create setting-specific adaptations
        setting_adaptations = {
            "fantasy": "magical abilities, ancient bloodlines, mystical knowledge",
            "cultivation": "spiritual techniques, martial arts mastery, qi manipulation",
            "scifi": "advanced technology, genetic modifications, space-age knowledge",
            "academy": "academic achievements, student politics, special talents",
            "modern": "professional skills, family connections, personal history",
            "gamelike": "special stats, unique classes, system knowledge",
            "historical": "period-appropriate skills, social status, historical knowledge",
            "apocalypse": "survival skills, pre-disaster knowledge, adaptation abilities"
        }
        
        setting_context = setting_adaptations.get(setting, "appropriate abilities")
        
        return f"""
{character_origin.upper()} CHARACTER PROFILE:

CORE TRAITS TO WEAVE INTO STORY:
{chr(10).join(f'• {trait}' for trait in profile['core_traits'])}

UNIQUE ABILITIES TO SHOWCASE:
{chr(10).join(f'• {ability}' for ability in profile['unique_abilities'])}
• Adapt these to {setting} context: {setting_context}

SOCIAL DYNAMICS TO INCLUDE:
{chr(10).join(f'• {dynamic}' for dynamic in profile['social_dynamics'])}

INTERNAL CONFLICTS TO EXPLORE:
{chr(10).join(f'• {conflict}' for conflict in profile['internal_conflicts'])}

CRITICAL: This {character_origin} origin should drive the plot, create unique opportunities and challenges, and make the character distinctly different from others. Show, don't tell - let their origin emerge through actions, reactions, and consequences."""

    @staticmethod
    def _parse_story_response_improved(response_text: str) -> Tuple[str, List[Choice]]:
        """
        Parse the AI response into story content and choices with bulletproof logic.
        Handles both [STORY]/[CHOICES] and STORY:/CHOICES: formats, plus fallback parsing.
        """
        try:
            story_content = ""
            choices = []
            
            # Clean up the response text
            response_text = response_text.strip()
            logger.debug(f"Parsing response text (first 500 chars): {response_text[:500]}")
            
            # METHOD 1: Try the new STORY:/CHOICES: format first
            if "STORY:" in response_text and "CHOICES:" in response_text:
                logger.debug("Using STORY:/CHOICES: format parsing")
                # Extract story content
                story_start = response_text.find("STORY:") + 6
                choices_start = response_text.find("CHOICES:")
                story_content = response_text[story_start:choices_start].strip()
                
                # Extract choices section
                choices_section = response_text[choices_start + 8:].strip()
                choice_lines = choices_section.split("\n")
                
                choice_count = 0
                for line in choice_lines:
                    line = line.strip()
                    if line and (line.startswith("1.") or line.startswith("2.") or line.startswith("3.")):
                        choice_text = line[2:].strip()  # Remove "1.", "2.", "3."
                        if choice_text and len(choice_text) > 8:  # More lenient minimum length
                            choice_count += 1
                            choices.append(Choice(id=str(choice_count), text=choice_text))
                            if choice_count >= 3:
                                break
            
            # METHOD 2: Try the old [STORY]/[CHOICES] format
            elif "[STORY]" in response_text and "[/STORY]" in response_text:
                logger.debug("Using [STORY]/[CHOICES] format parsing")
                story_content = response_text.split("[STORY]")[1].split("[/STORY]")[0].strip()
                
                if "[CHOICES]" in response_text and "[/CHOICES]" in response_text:
                    choices_section = response_text.split("[CHOICES]")[1].split("[/CHOICES]")[0].strip()
                    choice_lines = choices_section.split("\n")
                    
                    choice_count = 0
                    for line in choice_lines:
                        line = line.strip()
                        if line:
                            import re
                            choice_text = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                            if choice_text and len(choice_text) > 8:  # More lenient minimum length
                                choice_count += 1
                                choices.append(Choice(id=str(choice_count), text=choice_text))
                                if choice_count >= 3:
                                    break
            
            # METHOD 3: Smart fallback parsing for any response format
            if len(choices) < 3 or not story_content:
                logger.debug("Using smart fallback parsing")
                import re
                lines = response_text.split('\n')
                
                # Find story content (everything before numbered choices)
                story_lines = []
                choice_lines = []
                found_numbered_line = False
                
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    # Look for numbered choices (1., 2., 3., 1), 2), 3), etc.)
                    if re.match(r'^\d+[\.\)]\s*', line_stripped) and len(line_stripped) > 10:
                        if not found_numbered_line:
                            found_numbered_line = True
                        choice_lines.append(line_stripped)
                    elif not found_numbered_line:
                        # Skip common formatting markers
                        if line_stripped and not re.match(r'^(STORY|CHOICES|\\[/?STORY\\]|\\[/?CHOICES\\]):?$', line_stripped):
                            story_lines.append(line)
                
                # Extract story content if not found yet
                if not story_content and story_lines:
                    story_content = '\n'.join(story_lines).strip()
                    # Clean up common formatting artifacts
                    story_content = re.sub(r'^(STORY|\\[STORY\\]):?\s*', '', story_content, flags=re.IGNORECASE)
                    story_content = re.sub(r'(\\[/STORY\\]|CHOICES:).*$', '', story_content, flags=re.DOTALL | re.IGNORECASE)
                    story_content = story_content.strip()
                
                # Extract choices if not found yet
                if len(choices) < 3 and choice_lines:
                    choices = []
                    for line in choice_lines:
                        choice_text = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                        if choice_text and len(choice_text) > 8:
                            choices.append(Choice(id=str(len(choices) + 1), text=choice_text))
            
            # Validate story content with more lenient requirements
            if not story_content or len(story_content) < 20:  # More lenient minimum
                logger.warning(f"Story content too short: {len(story_content)} characters")
                # Try to extract any substantial text from the response
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                potential_story = []
                for line in lines:
                    if (len(line) > 30 and 
                        not re.match(r'^\d+[\.\)]\s*', line) and
                        not re.match(r'^(STORY|CHOICES|\\[/?STORY\\]|\\[/?CHOICES\\]):?$', line, re.IGNORECASE)):
                        potential_story.append(line)
                
                if potential_story:
                    story_content = ' '.join(potential_story[:3])  # Take first few substantial lines
                    logger.info(f"Extracted story from unformatted response: {len(story_content)} chars")
            
            # Validate choices with more lenient requirements
            if len(choices) < 2:  # Accept even 2 choices if that's all we have
                logger.warning(f"Not enough choices found: {len(choices)}")
                # Don't fail immediately - let's see if we have at least some content
                if not story_content:
                    raise ValueError(f"Both story content and choices are insufficient")
            
            # Fill in missing choices if we have fewer than 3
            while len(choices) < 3:
                choice_num = len(choices) + 1
                generic_choice = f"Take action based on the current situation (Option {choice_num})"
                choices.append(Choice(id=str(choice_num), text=generic_choice))
                logger.info(f"Added generic choice {choice_num}")
            
            # Less strict validation - only check for completely generic phrases
            forbidden_phrases = ["(exploration)", "(strategic)", "→"]
            for choice in choices:
                choice_lower = choice.text.lower()
                if any(phrase in choice_lower for phrase in forbidden_phrases):
                    logger.warning(f"Forbidden phrase detected in choice: {choice.text}")
                    # Replace rather than fail
                    choice.text = f"Take a different approach to the situation"
            
            # Return only the first 3 valid choices
            final_choices = choices[:3]
            logger.info(f"Successfully parsed: story={len(story_content)} chars, choices={len(final_choices)}")
            return story_content, final_choices
            
        except Exception as e:
            logger.error(f"Improved parsing failed with error: {e}")
            logger.debug(f"Full response text: {response_text}")
            
            # Last resort: try to extract ANYTHING useful from the response
            try:
                # Split into lines and find anything that looks like content
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                
                # Find the longest lines as potential story content
                story_candidates = [line for line in lines if len(line) > 50]
                if story_candidates:
                    story_content = story_candidates[0]
                else:
                    story_content = "The story continues as you make your choice..."
                
                # Find any lines that could be choices
                choice_candidates = []
                import re
                for line in lines:
                    if (len(line) > 15 and len(line) < 200):  # Reasonable choice length
                        clean_line = re.sub(r'^[\d\-\*\•]\s*[\.\)]*\s*', '', line).strip()
                        if clean_line and len(clean_line) > 10:
                            choice_candidates.append(clean_line)
                
                # Take up to 3 choice candidates
                parsed_choices = []
                for i, choice_text in enumerate(choice_candidates[:3]):
                    parsed_choices.append(Choice(id=str(i+1), text=choice_text))
                
                # Fill with generic choices if needed
                while len(parsed_choices) < 3:
                    choice_num = len(parsed_choices) + 1
                    parsed_choices.append(Choice(id=str(choice_num), text=f"Consider your options carefully (Choice {choice_num})"))
                
                logger.info(f"Emergency parsing extracted: story={len(story_content)} chars, choices={len(parsed_choices)}")
                return story_content, parsed_choices[:3]
                
            except Exception as e2:
                logger.error(f"Emergency parsing also failed: {e2}")
                raise ValueError(f"Complete parsing failure: {e}, {e2}")

 