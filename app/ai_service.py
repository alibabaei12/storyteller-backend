import os
import openai
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .models import Choice

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
        language_complexity: str = "simple"
    ) -> Tuple[str, List[Choice]]:
        """
        Generate the initial story content based on character parameters.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            print(f"[AI] Generating initial story for {character_name} in {setting} setting")
            
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
        language_complexity: str = "simple"
    ) -> Tuple[str, List[Choice]]:
        """
        Continue the story based on the selected choice.
        
        Returns:
            Tuple containing story content and list of choices
        """
        try:
            print(f"[AI] Continuing story based on choice: {selected_choice}")
            
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
                    Choice(id="1", text="Continue your journey"),
                    Choice(id="2", text="Try a different approach"),
                    Choice(id="3", text="Reflect on your situation")
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