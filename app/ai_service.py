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
                    character_name, character_gender, language_complexity
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
            
            # Create the system prompt
            system_prompt = f"""You are a storytelling genius who creates BINGE-WORTHY interactive fiction that readers devour in one sitting.

{setting_prompt}
{tone_prompt}
{structure_prompt}
{gender_prompt}
{language_prompt}

STORY MASTERY RULES:
1. CONTEXT FIRST - Give readers enough background to care about what happens
2. INTRIGUE over action - Create mysteries, secrets, or goals that drive the plot
3. MEANINGFUL CHOICES - Each decision shapes the story direction significantly
4. PLOT MOMENTUM - Something important should happen or be revealed every chapter
5. EMOTIONAL HOOKS - Make readers invested in the character's goals and relationships

WRITING APPROACH:
- Start with a SITUATION, not an action scene
- Establish CLEAR STAKES - what the character wants/needs
- Create IMMEDIATE INTRIGUE - questions that need answers
- Use CONCRETE DETAILS - specific, relatable scenarios
- ADVANCE THE PLOT - don't just describe the same scene

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that lead to DIFFERENT story paths and outcomes
2. Each choice should unlock new plot elements, characters, or revelations
3. Avoid combat-heavy or repetitive scenario choices
4. Include choices that appeal to different player motivations (social, strategic, bold)

The main character (named {character_name}) has the origin: {character_origin}.
Your goal: Make readers think "I'm hooked - this story is going somewhere interesting!" after every passage."""

            # Create the user prompt  
            user_prompt = f"""Create a COMPELLING opening that immediately hooks the reader with an intriguing situation.

Character: {character_name} with {character_origin} background
Setting: {setting}
Tone: {tone}

OPENING STRATEGY:
- Start with a specific, intriguing SITUATION that sets up the story
- Give enough context so readers understand what's happening and why it matters
- Create a clear goal, mystery, or conflict that drives the plot forward
- End with a meaningful choice that will shape the story's direction

AVOID:
- Generic action sequences or combat
- Vague mystical/dramatic descriptions  
- Starting mid-fight with no explanation
- Overly long atmospheric writing

WRITE 200-300 words that:
1. Establish a clear, interesting situation
2. Give the character a goal or problem to solve
3. Create immediate intrigue about what happens next
4. Present a meaningful choice with real consequences

Make me want to keep reading because I'm invested in this character and curious about their story!

Format your response as follows:
[STORY]
(Your story text here)
[/STORY]

[CHOICES]
1. (First choice text)
2. (Second choice text)  
3. (Third choice text)
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
                story_content, choices = BaseGenre.parse_story_response_strict(response_text)
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
        manga_genre: str = None
    ) -> Tuple[str, List[Choice]]:
        """
        Continue the story based on the selected choice.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            logger.info(f"Continuing story based on choice: {selected_choice}, manga genre: {manga_genre}")
            
            # Check for manga-specific continuation using dynamic mapping
            if manga_genre and manga_genre in AIService.GENRE_MAP:
                selected_genre = AIService.GENRE_MAP[manga_genre]
                return selected_genre.continue_story(
                    character_name, character_gender, previous_content, selected_choice, language_complexity
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
            
            # Create the system prompt
            system_prompt = f"""You are a storytelling genius who creates BINGE-WORTHY interactive fiction that readers devour in one sitting.

{setting_prompt}
{tone_prompt}
{structure_prompt}
{gender_prompt}
{language_prompt}

STORY PROGRESSION RULES:
1. ADVANCE THE PLOT - Each chapter should introduce new elements, characters, or revelations
2. CONSEQUENCES MATTER - Show clear results from the previous choice 
3. VARIETY IS KEY - Change locations, introduce new characters, reveal secrets
4. STORY MOMENTUM - Always move toward solving mysteries or achieving goals
5. MEANINGFUL DEVELOPMENT - Character growth or world-building in every passage

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

            # Create the user prompt
            user_prompt = f"""Continue the story by showing the consequences of {character_name}'s choice and advancing the plot.

Previous content:
{previous_content}

Selected choice:
{selected_choice}

CONTINUATION STRATEGY:
- Show immediate results of this choice
- Introduce NEW story elements (characters, locations, information, conflicts)
- Move the plot forward significantly - don't stay in the same scenario
- Create fresh intrigue that builds on what came before

PLOT ADVANCEMENT REQUIREMENTS:
1. Change something significant about the situation
2. Introduce new characters, locations, or revelations
3. Move closer to resolving mysteries or achieving goals
4. Create new questions or challenges for the reader

WRITE 200-300 words that:
1. Show clear consequences of the previous choice
2. Introduce new elements that advance the story
3. Create compelling intrigue about what happens next
4. End with choices that offer genuinely different story directions

Keep the story moving forward - I want to see real progress and development!

Format your response as follows:
[STORY]
(Your continuation text here)
[/STORY]

[CHOICES]
1. (First choice text)
2. (Second choice text)
3. (Third choice text)
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
                story_content, choices = BaseGenre.parse_story_response_strict(response_text)
                logger.info(f"Generated continuation: {len(story_content)} chars and {len(choices)} choices")
                return story_content, choices
            except ValueError as parse_error:
                logger.warning(f"Story parsing failed, retrying: {parse_error}")
                # If parsing fails, try to regenerate with stricter instructions
                return AIService._retry_story_generation_with_better_format(
                    system_prompt, user_prompt, character_name, setting, selected_choice
                )
            
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
        Retry story generation with stricter formatting instructions.
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

            logger.info(f"Retrying story generation with enhanced formatting for {character_name}")
            
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
            story_content, choices = BaseGenre.parse_story_response_strict(response_text)
            
            logger.info(f"Retry successful: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            # Use contextual fallback as last resort
            return AIService._create_contextual_api_fallback(character_name, setting, selected_choice)
    
    @staticmethod
    def _create_contextual_api_fallback(
        character_name: str, 
        setting: str, 
        selected_choice: str
    ) -> Tuple[str, List[Choice]]:
        """
        Create contextual fallback content that references the actual selected choice.
        """
        # Create contextual story content based on the selected choice
        story_content = f"{character_name} takes a deep breath and decides to {selected_choice.lower()}. " \
                       f"The path ahead in this {setting} world remains uncertain, but {character_name}'s " \
                       f"determination grows stronger. Every choice shapes the journey ahead, and this " \
                       f"decision will have consequences that ripple through their adventure..."
        
        # Create setting-appropriate choices that relate to the story context
        if setting in ["fantasy", "cultivation"]:
            choices = [
                Choice(id="1", text=f"Continue following through on the decision to {selected_choice.lower()}"),
                Choice(id="2", text="Seek guidance from wise mentors about the next steps"),
                Choice(id="3", text="Take time to reflect on the consequences of this choice")
            ]
        elif setting in ["scifi", "gamelike"]:
            choices = [
                Choice(id="1", text=f"Analyze the results of choosing to {selected_choice.lower()}"),
                Choice(id="2", text="Use available technology to assess the situation"),
                Choice(id="3", text="Gather data about the effects of this decision")
            ]
        elif setting in ["academy", "modern"]:
            choices = [
                Choice(id="1", text=f"Continue with the plan to {selected_choice.lower()}"),
                Choice(id="2", text="Discuss the decision with friends or mentors"),
                Choice(id="3", text="Study the implications of this choice carefully")
            ]
        else:
            choices = [
                Choice(id="1", text=f"Follow through on the decision to {selected_choice.lower()}"),
                Choice(id="2", text="Consider the consequences of this choice"),
                Choice(id="3", text="Adjust the approach based on new circumstances")
            ]
        
        logger.info(f"Created contextual fallback for {character_name} with choice reference")
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
            story_content, choices = BaseGenre.parse_story_response_strict(response_text)
            
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

 