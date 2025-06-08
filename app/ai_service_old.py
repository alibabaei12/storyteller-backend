import os
import openai
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .models import Choice

# Import genre implementations
from .genres.cultivation_progression import CultivationProgression
from .genres.fantasy_adventure import FantasyAdventure
from .genres.academy_magic import AcademyMagic

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
    
    @staticmethod
    def generate_initial_story(
        character_name: str,
        character_gender: str,
        setting: str,
        tone: str,
        character_origin: str,
        story_length: str,
        language_complexity: str = "simple",
        manga_genre: str = None
    ) -> Tuple[str, List[Choice]]:
        """
        Generate the initial story content based on character parameters.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            print(f"[AI] Generating initial story for {character_name} in {setting} setting, manga genre: {manga_genre}")
            
            # Check if this is a manga-specific genre
            if manga_genre == "cultivation_progression":
                return CultivationProgression.generate_story(
                    character_name, character_gender, story_length, language_complexity
                )
            elif manga_genre == "fantasy_adventure":
                return FantasyAdventure.generate_story(
                    character_name, character_gender, story_length, language_complexity
                )
            elif manga_genre == "academy_magic":
                return AcademyMagic.generate_story(
                    character_name, character_gender, story_length, language_complexity
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
            
            # Create length-specific prompt addition
            length_prompt = ""
            if story_length == "short":
                length_prompt = "This should be a shorter story that could be completed in 5-8 interactions."
            elif story_length == "medium":
                length_prompt = "This should be a medium-length story that could be completed in 10-15 interactions."
            elif story_length == "long":
                length_prompt = "This should be a longer, more complex story that could extend to 20+ interactions."
            elif story_length == "infinite":
                length_prompt = "This should be an open-ended story that can continue indefinitely with new challenges and scenarios."
            
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
{length_prompt}
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
            
            # Parse the response
            story_content, choices = AIService._parse_story_response(response_text)
            
            print(f"[AI] Generated initial story: {len(story_content)} chars and {len(choices)} choices")
            
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error generating initial story: {e}")
            # Provide fallback content
            return (
                f"You, {character_name}, find yourself in a {setting} world. " 
                f"Your journey is about to begin...",
                [
                    Choice(id="1", text="Explore your surroundings"),
                    Choice(id="2", text="Seek guidance from others"),
                    Choice(id="3", text="Reflect on your abilities")
                ]
            )
    
    @staticmethod
    def continue_story(
        character_name: str,
        character_gender: str,
        setting: str,
        tone: str,
        story_length: str,
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
            print(f"[AI] Continuing story based on choice: {selected_choice}, manga genre: {manga_genre}")
            
            # Check for manga-specific continuation
            if manga_genre == "cultivation_progression":
                return CultivationProgression.continue_story(
                    character_name, character_gender, previous_content, selected_choice, language_complexity
                )
            elif manga_genre == "fantasy_adventure":
                return FantasyAdventure.continue_story(
                    character_name, character_gender, previous_content, selected_choice, language_complexity
                )
            elif manga_genre == "academy_magic":
                return AcademyMagic.continue_story(
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
            
            # Create length-specific prompt addition
            length_prompt = ""
            if story_length == "short":
                length_prompt = "This should be a shorter story that could be completed in 5-8 interactions."
            elif story_length == "medium":
                length_prompt = "This should be a medium-length story that could be completed in 10-15 interactions."
            elif story_length == "long":
                length_prompt = "This should be a longer, more complex story that could extend to 20+ interactions."
            elif story_length == "infinite":
                length_prompt = "This should be an open-ended story that can continue indefinitely with new challenges and scenarios."
            
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
{length_prompt}
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
            
            # Parse the response
            story_content, choices = AIService._parse_story_response(response_text)
            
            print(f"[AI] Generated continuation: {len(story_content)} chars and {len(choices)} choices")
            
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error continuing story: {e}")
            # Provide fallback content
            return (
                f"As {character_name}, you decided to {selected_choice.lower()}. " 
                f"Your journey continues...",
                [
                    Choice(id="1", text="Proceed cautiously"),
                    Choice(id="2", text="Take a bold approach"),
                    Choice(id="3", text="Reconsider your options")
                ]
            )
    
    @staticmethod
    def _parse_story_response(response_text: str) -> Tuple[str, List[Choice]]:
        """
        Parse the AI response into story content and choices.
        
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
            
            # Manga-specific system prompt
            system_prompt = f"""You are creating an opening chapter for a CULTIVATION PROGRESSION manga that hooks readers immediately.

CRITICAL SUCCESS FACTORS:
1. EMOTIONAL CONNECTION - Make readers care about the character personally within 3 sentences
2. CONCRETE DETAILS - Show, don't tell through specific scenes and sensory details
3. LOGICAL WORLD-BUILDING - Explain cultivation naturally through character experience
4. SLOWER EMOTIONAL PACING - Build attachment before revealing power systems
5. SPECIFIC STAKES - Clear, personal goals beyond just "getting stronger"

OPENING STRUCTURE:
- START WITH CHARACTER MOMENT: Show personality through a specific scene
- BUILD EMOTIONAL CONNECTION: Make readers sympathize with their struggle
- INTRODUCE WORLD NATURALLY: Cultivation system through character's perspective
- END WITH CLEAR STAKES: Specific goal that matters to the character

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
{character_name} is considered weak in a cultivation world where spiritual power determines everything. Give them a SPECIFIC backstory and clear motivation for wanting to get stronger.

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
1. Start with a CHARACTER MOMENT showing {character_name}'s personality in action
2. Give them a FRESH, SPECIFIC motivation from the examples above (not generic goals)
3. Include at least ONE named technique they're learning or want to learn
4. Introduce ONE rival with personality and ONE supportive character
5. Show visual qi descriptions with specific colors and effects
6. Hint at IMMEDIATE world stakes (demon beast attacks, sect wars, ancient ruins discovered)
7. Build to the path choices through natural story progression
8. Make reader think "I care about this character and want them to succeed!"

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

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=900,
            )
            
            response_text = response.choices[0].message.content
            story_content, choices = AIService._parse_story_response(response_text)
            
            print(f"[AI] Generated cultivation progression story: {len(story_content)} chars and {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error generating cultivation progression story: {e}")
            # Fallback for cultivation progression
            return (
                f"{character_name} stood at the bottom of the Outer Disciple rankings, mocked by all for having weak spiritual roots. "
                f"Determined to prove their worth and honor their family's memory, {character_name} faced a crucial decision about their cultivation path. "
                f"The upcoming sect trials offered a chance to advance, but other paths beckoned as well...",
                [
                    Choice(id="1", text="Train harder to improve cultivation base"),
                    Choice(id="2", text="Seek help from a senior disciple"),
                    Choice(id="3", text="Challenge a rival to prove worthiness")
                ]
            )

    @staticmethod
    def _continue_cultivation_progression_story(
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        language_complexity: str
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

PATH-SPECIFIC STORYTELLING:
- SECT PATH: Focus on trials, hierarchy, competition with other disciples
- MASTER PATH: Focus on personal training, secret techniques, one-on-one growth
- ACADEMY PATH: Focus on classes, academic competition, student relationships
- INDEPENDENT PATH: Focus on exploration, self-discovery, unique challenges

PACING REQUIREMENTS:
- Don't jump to legendary masters or ancient secrets immediately
- Build relationships and skills gradually over multiple chapters
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
1. (Creative choice - pick from: exploration, mystery, helping others, rule-breaking, etc.)
2. (Different approach - social, strategic, diplomatic, risky, etc.)
3. (Unique path - training, investigation, alliance-building, etc.)
[/CHOICES]

CRITICAL: Each choice must use a DIFFERENT approach type! No repetitive patterns!"""

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=900,
            )
            
            response_text = response.choices[0].message.content
            story_content, choices = AIService._parse_story_response(response_text)
            
            print(f"[AI] Generated cultivation progression continuation: {len(story_content)} chars and {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error continuing cultivation progression story: {e}")
            # Simple fallback
            return (
                f"As {character_name} made their choice, the path of cultivation opened before them, "
                f"revealing new challenges and opportunities for growth...",
                [
                    Choice(id="1", text="Focus on inner power cultivation"),
                    Choice(id="2", text="Seek guidance from a master"),
                    Choice(id="3", text="Explore ancient techniques")
                ]
            )

    @staticmethod
    def _parse_story_response(response_text: str) -> Tuple[str, List[Choice]]:
        """
        Parse the AI response into story content and choices.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            # Extract story content
            if "[STORY]" in response_text and "[/STORY]" in response_text:
                story_match = response_text.split("[STORY]")[1].split("[/STORY]")[0].strip()
            else:
                # If the story doesn't follow the format, use the whole text before [CHOICES]
                if "[CHOICES]" in response_text:
                    story_match = response_text.split("[CHOICES]")[0].strip()
                else:
                    story_match = response_text.strip()
            
            # Extra safety: Remove any [CHOICES] sections that might still be in the content
            if "[CHOICES]" in story_match:
                story_match = story_match.split("[CHOICES]")[0].strip()
                
            # Remove "[STORY]" or "[/STORY]" tags that might appear in the content itself
            story_match = story_match.replace("[STORY]", "").replace("[/STORY]", "").strip()
            
            # Extract choices
            choices = []
            if "[CHOICES]" in response_text and "[/CHOICES]" in response_text:
                choices_section = response_text.split("[CHOICES]")[1].split("[/CHOICES]")[0].strip()
                choice_lines = choices_section.split("\n")
                
                # Parse individual choices
                for i, line in enumerate(choice_lines):
                    if line.strip():
                        # Remove numbers and dots from the beginning (e.g., "1. ")
                        choice_text = line
                        for prefix in [f"{i+1}. ", f"{i+1} ", f"{i+1}."]:
                            if choice_text.startswith(prefix):
                                choice_text = choice_text[len(prefix):].strip()
                                break
                        
                        if choice_text:
                            choices.append(Choice(id=str(i+1), text=choice_text))
            
            # Ensure we have at least one choice
            if not choices:
                choices = [
                    Choice(id="1", text="Focus on improving your cultivation technique"),
                    Choice(id="2", text="Seek guidance from a senior disciple"),
                    Choice(id="3", text="Take on a challenging training task")
                ]
            
            return story_match, choices
            
        except Exception as e:
            print(f"[AI] Error parsing story response: {e}")
            # Provide fallback content and choices
            return (
                "Your adventure continues...",
                [
                    Choice(id="1", text="Continue your journey"),
                    Choice(id="2", text="Try a different approach"),
                    Choice(id="3", text="Reflect on your situation")
                ]
            )

    @staticmethod
    def _generate_fantasy_adventure_story(character_name: str, character_gender: str, story_length: str, language_complexity: str) -> Tuple[str, List[Choice]]:
        """Generate a fantasy adventure story optimized for manga-style progression."""
        
        # Create language complexity prompt addition
        language_prompt = ""
        if language_complexity == "simple":
            language_prompt = "Use simple, clear language that is easy to understand. Avoid complex vocabulary or long sentences."
        elif language_complexity == "moderate":
            language_prompt = "Use moderate language complexity with some advanced vocabulary, but keep it accessible."
        elif language_complexity == "complex":
            language_prompt = "Use rich, sophisticated language with advanced vocabulary and complex sentence structures."
        
        # Create gender-specific pronouns
        if character_gender == "male":
            pronouns = "he/him/his"
        elif character_gender == "female":
            pronouns = "she/her/hers"
        elif character_gender == "non-binary":
            pronouns = "they/them/their"
        else:
            pronouns = "they/them/their"
        
        system_prompt = f"""You are a master storyteller creating ENGAGING fantasy adventure stories in the style of popular manga/light novels like "That Time I Got Reincarnated as a Slime," "Overlord," and "KonoSuba."

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

FANTASY ADVENTURE STORY REQUIREMENTS:
🌟 IMMEDIATE HOOK: Start with {character_name} in a moment that shows their personality before explaining the fantasy world
🏰 WORLD IMMERSION: Create a vivid fantasy setting with unique magical elements, not generic "kingdom" or "village"
✨ CLEAR MAGIC SYSTEM: Establish how magic/powers work in this world with specific examples
🎯 PERSONAL STAKES: Give {character_name} a compelling reason to adventure (save someone, find truth, fulfill promise)
🌍 LIVING WORLD: Include specific locations, factions, or conflicts that feel real and lived-in

STORYTELLING EXCELLENCE:
- Show {character_name}'s personality through action/dialogue first
- Use specific, concrete details rather than vague descriptions
- Create immediate intrigue or mystery to hook readers
- Include sensory details to make the world feel real
- Build toward a clear goal or quest

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Exploration: Investigate, discover, venture into unknown
- Social: Interact, negotiate, form alliances
- Risk-taking: Bold action, dangerous gambles
- Strategic: Planning, preparation, clever solutions
- Magical: Use/experiment with powers or magic
- Protective: Help others, defend the innocent
- Mysterious: Follow clues, uncover secrets
- Diplomatic: Peaceful resolution, mediation
- Combat: Direct confrontation, fighting
- Cautious: Careful observation, safe approaches

Each choice must reference specific story elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and story-specific.

Generate a fantasy adventure opening that makes readers think: "This world is fascinating and I want to see what {character_name} does next!"

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

        user_prompt = f"""Create an engaging fantasy adventure story opening for {character_name}. Make it feel like the start of an epic magical journey with clear stakes and an intriguing world to explore.

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
            print(f"[AI] Generating fantasy adventure story for {character_name}")
            
            # Generate story with OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response to extract story and choices
            story_content, choices = AIService._parse_story_response(content)
            
            print(f"[AI] Generated fantasy adventure story: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error generating fantasy adventure story: {e}")
            # Fantasy adventure fallback
            return (
                f"{character_name} stood at the edge of the mystical Whispering Woods, clutching the ancient map their grandmother had hidden away. "
                f"The map showed the location of the lost Crystal of Eternal Dawn, said to grant one wish to whoever finds it. "
                f"With their village suffering from a mysterious curse that's been draining the life from everything, {character_name} knew this might be their only hope. "
                f"The forest ahead shimmered with magical energy, and they could hear the distant call of creatures unknown...",
                [
                    Choice(id="1", text="Enter the forest following the map's path carefully"),
                    Choice(id="2", text="Seek out a local guide or forest dweller for advice"),
                    Choice(id="3", text="Use magic to reveal hidden paths or dangers ahead")
                ]
            )
    
    @staticmethod
    def _continue_fantasy_adventure_story(character_name: str, character_gender: str, previous_content: str, selected_choice: str, language_complexity: str) -> Tuple[str, List[Choice]]:
        """Continue a fantasy adventure story."""
        
        # Create language complexity prompt addition
        language_prompt = ""
        if language_complexity == "simple":
            language_prompt = "Use simple, clear language that is easy to understand. Avoid complex vocabulary or long sentences."
        elif language_complexity == "moderate":
            language_prompt = "Use moderate language complexity with some advanced vocabulary, but keep it accessible."
        elif language_complexity == "complex":
            language_prompt = "Use rich, sophisticated language with advanced vocabulary and complex sentence structures."
        
        # Create gender-specific pronouns
        if character_gender == "male":
            pronouns = "he/him/his"
        elif character_gender == "female":
            pronouns = "she/her/hers"
        elif character_gender == "non-binary":
            pronouns = "they/them/their"
        else:
            pronouns = "they/them/their"
        
        system_prompt = f"""You are continuing an engaging fantasy adventure story in the style of popular manga/light novels.

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

FANTASY ADVENTURE CONTINUATION REQUIREMENTS:
🎯 ADVANCE THE QUEST: Show clear progress toward the goal or reveal new challenges
🌟 ESCALATE STAKES: Raise the tension or reveal bigger threats
✨ WORLD BUILDING: Add new magical elements, locations, or creatures
👥 CHARACTER MOMENTS: Show {character_name}'s growth or personality development
🎭 STORY DEPTH: Introduce new allies, rivals, or mysteries

STORYTELLING EXCELLENCE:
- Show immediate consequences of the previous choice
- Introduce new elements that expand the world
- Create moments of wonder or discovery
- Use vivid sensory details for magical elements
- Build toward the next major decision point

CHOICE VARIETY REQUIREMENTS:
Generate 3 DISTINCTLY DIFFERENT choices using these approach types:
- Exploration: Investigate, discover, venture into unknown
- Social: Interact, negotiate, form alliances  
- Risk-taking: Bold action, dangerous gambles
- Strategic: Planning, preparation, clever solutions
- Magical: Use/experiment with powers or magic
- Protective: Help others, defend the innocent
- Mysterious: Follow clues, uncover secrets
- Diplomatic: Peaceful resolution, mediation
- Combat: Direct confrontation, fighting
- Cautious: Careful observation, safe approaches

Each choice must reference specific story elements and lead to completely different scenarios.

CRITICAL: NO template or repetitive choices. Each choice should feel fresh and story-specific.

Continue the fantasy adventure in a way that makes readers eager to see what happens next!

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
            print(f"[AI] Continuing fantasy adventure story for {character_name}")
            
            # Generate story continuation with OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response to extract story and choices
            story_content, choices = AIService._parse_story_response(content)
            
            print(f"[AI] Continued fantasy adventure: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error continuing fantasy adventure story: {e}")
            # Fantasy adventure fallback
            return (
                f"Following the chosen path, {character_name} discovered something unexpected that changed everything. "
                f"The magical energies around them grew stronger, and new challenges emerged that would test their resolve...",
                [
                    Choice(id="1", text="Face the challenge head-on with determination"),
                    Choice(id="2", text="Seek creative solutions using available resources"),
                    Choice(id="3", text="Look for allies or help from unexpected sources")
                ]
            )

    @staticmethod
    def _generate_academy_magic_story(character_name: str, character_gender: str, story_length: str, language_complexity: str) -> Tuple[str, List[Choice]]:
        """Generate an academy magic story optimized for manga-style progression."""
        
        # Create language complexity prompt addition
        language_prompt = ""
        if language_complexity == "simple":
            language_prompt = "Use simple, clear language that is easy to understand. Avoid complex vocabulary or long sentences."
        elif language_complexity == "moderate":
            language_prompt = "Use moderate language complexity with some advanced vocabulary, but keep it accessible."
        elif language_complexity == "complex":
            language_prompt = "Use rich, sophisticated language with advanced vocabulary and complex sentence structures."
        
        # Create gender-specific pronouns
        if character_gender == "male":
            pronouns = "he/him/his"
        elif character_gender == "female":
            pronouns = "she/her/hers"
        elif character_gender == "non-binary":
            pronouns = "they/them/their"
        else:
            pronouns = "they/them/their"
        
        system_prompt = f"""You are a master storyteller creating ENGAGING magic academy stories in the style of popular manga/light novels like "A Returner's Magic Should Be Special," "The Irregular at Magic High School," and "Little Witch Academia."

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

MAGIC ACADEMY STORY REQUIREMENTS:
🌟 ACADEMY IMMERSION: Start with {character_name} in a specific academy moment that shows personality/abilities
🏫 SCHOOL POLITICS: Include class rankings, student hierarchies, or competitive systems
✨ UNIQUE MAGIC: Create a distinctive magic system with clear rules and progression paths
🎯 PERSONAL GOALS: Give {character_name} academy-specific motivation (prove worth, protect friends, uncover truth)
👥 SOCIAL DYNAMICS: Include rival students, potential allies, mysterious mentors, or secret groups

STORYTELLING EXCELLENCE:
- Show {character_name}'s academy life and magical abilities immediately
- Create intrigue around academy mysteries or competitions
- Include specific academy locations (training halls, dormitories, secret areas)
- Use concrete details about magical subjects and classes
- Build toward clear academy-related goals or conflicts

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

        user_prompt = f"""Create an engaging magic academy story opening for {character_name}. Make it feel like the start of an academy adventure with clear magical progression and social dynamics.

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
            print(f"[AI] Generating academy magic story for {character_name}")
            
            # Generate story with OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response to extract story and choices
            story_content, choices = AIService._parse_story_response(content)
            
            print(f"[AI] Generated academy magic story: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error generating academy magic story: {e}")
            # Academy magic fallback
            return (
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
    
    @staticmethod
    def _continue_academy_magic_story(character_name: str, character_gender: str, previous_content: str, selected_choice: str, language_complexity: str) -> Tuple[str, List[Choice]]:
        """Continue an academy magic story."""
        
        # Create language complexity prompt addition
        language_prompt = ""
        if language_complexity == "simple":
            language_prompt = "Use simple, clear language that is easy to understand. Avoid complex vocabulary or long sentences."
        elif language_complexity == "moderate":
            language_prompt = "Use moderate language complexity with some advanced vocabulary, but keep it accessible."
        elif language_complexity == "complex":
            language_prompt = "Use rich, sophisticated language with advanced vocabulary and complex sentence structures."
        
        # Create gender-specific pronouns
        if character_gender == "male":
            pronouns = "he/him/his"
        elif character_gender == "female":
            pronouns = "she/her/hers"
        elif character_gender == "non-binary":
            pronouns = "they/them/their"
        else:
            pronouns = "they/them/their"
        
        system_prompt = f"""You are continuing an engaging magic academy story in the style of popular manga/light novels.

{language_prompt}

CHARACTER PRONOUNS: Use {pronouns} pronouns for {character_name}.

ACADEMY MAGIC CONTINUATION REQUIREMENTS:
🎯 ACADEMY PROGRESS: Show advancement in classes, rankings, or magical abilities
🌟 RAISE STAKES: Introduce academy competitions, threats, or mysteries
✨ MAGICAL GROWTH: Demonstrate {character_name}'s developing powers or knowledge
👥 RELATIONSHIP DYNAMICS: Develop friendships, rivalries, or mentorships
🏫 SCHOOL DEPTH: Add new academy locations, subjects, or traditions

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
            print(f"[AI] Continuing academy magic story for {character_name}")
            
            # Generate story continuation with OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response to extract story and choices
            story_content, choices = AIService._parse_story_response(content)
            
            print(f"[AI] Continued academy magic: {len(story_content)} chars, {len(choices)} choices")
            return story_content, choices
            
        except Exception as e:
            print(f"[AI] Error continuing academy magic story: {e}")
            # Academy magic fallback
            return (
                f"Following the chosen path, {character_name} found themselves facing new challenges at the academy. "
                f"Their magical abilities continued to develop, but new obstacles and opportunities emerged that would test their resolve...",
                [
                    Choice(id="1", text="Focus on magical training to improve abilities"),
                    Choice(id="2", text="Seek guidance from a mentor or advanced student"),
                    Choice(id="3", text="Take on a challenge to prove academic worth")
                ]
            ) 