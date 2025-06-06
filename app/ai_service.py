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
            system_prompt = f"""You are a master storyteller who creates ADDICTIVE interactive fiction that readers can't put down.
Write in gripping second-person perspective that makes readers feel like the protagonist.

{setting_prompt}
{tone_prompt}
{length_prompt}
{gender_prompt}
{language_prompt}

HOOK MASTERY RULES:
1. NEVER start with introductions - drop readers into the action
2. Every sentence should raise stakes or deepen intrigue
3. Use sensory details that make scenes feel visceral and real
4. Create immediate emotional investment through conflict
5. End every passage on a cliffhanger that compels the next choice

WRITING STYLE:
- Short, punchy sentences for action sequences
- Rich sensory details (what they see, hear, feel, smell)
- Internal tension through urgent thoughts
- Show character background through actions, not exposition
- Use unexpected details that surprise and delight

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that lead to DIVERGENT outcomes (not looping back to the same scenario).
2. Include one RISKY choice, one SAFE choice, and one CLEVER/STRATEGIC choice.
3. Make each choice have clear implications and push the story in a new direction.
4. Avoid "false choices" where all paths lead to the same outcome.

The main character (named {character_name}) has the origin: {character_origin}.
Your goal: Make readers think "I NEED to know what happens next!" after every single passage.
"""

            # Create the user prompt
            user_prompt = f"""Create an EXPLOSIVE opening for an interactive story. The character's name is {character_name}, they have a {character_origin} background.

CRITICAL RULES:
- NO character introductions ("You are..." or "Your name is...")
- START IN THE MIDDLE OF ACTION or at a crucial moment
- Create immediate TENSION, DANGER, or high stakes
- Drop the reader into a gripping scene that demands instant decisions
- Make them feel the urgency and excitement from the first sentence

WRITE 300-400 words that:
1. Open with action, conflict, or a moment of crisis
2. Weave in the {character_origin} background naturally through actions/thoughts (not exposition)
3. Show the {setting} world through vivid, immediate details
4. End on a cliffhanger that makes the reader NEED to choose

Create a story so engaging that someone would immediately want to know what happens next.

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
            system_prompt = f"""You are a master storyteller who creates ADDICTIVE interactive fiction that keeps readers hooked.
Write in gripping second-person perspective that makes readers feel like the protagonist.

{setting_prompt}
{tone_prompt}
{length_prompt}
{gender_prompt}
{language_prompt}

CONTINUATION MASTERY RULES:
1. ESCALATE immediately - raise stakes, add complications, introduce new dangers
2. Build on the previous choice with UNEXPECTED consequences or twists
3. Use vivid sensory details that make scenes feel visceral and real
4. Create internal tension through urgent thoughts and reactions
5. End every passage on a cliffhanger that compels the next choice

WRITING STYLE:
- Short, punchy sentences for action sequences
- Rich sensory details (what they see, hear, feel, smell)
- Show emotions through actions, not exposition
- Surprise the reader with unexpected developments
- Keep momentum building - never slow down

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that lead to DIVERGENT outcomes (not looping back to the same scenario).
2. Include one RISKY choice, one SAFE choice, and one CLEVER/STRATEGIC choice.
3. Make each choice have clear implications and push the story in a new direction.
4. Avoid "false choices" where all paths lead to the same outcome.

Your goal: Make readers think "I NEED to know what happens next!" after every single passage."""

            # Create the user prompt
            user_prompt = f"""Build on the momentum and create an even MORE thrilling continuation based on {character_name}'s choice.

Previous content:
{previous_content}

Selected choice:
{selected_choice}

ESCALATION REQUIREMENTS:
- This choice must have immediate, dramatic CONSEQUENCES
- Introduce a NEW complication, threat, or opportunity that raises the stakes
- Create a moment of high tension or revelation
- NO repetitive patterns or safe outcomes - surprise the reader!

WRITE 300-400 words that:
1. Show the dramatic results of this choice immediately
2. Introduce unexpected twists or complications
3. Use vivid action and sensory details
4. Build to an even bigger cliffhanger than before
5. Make the reader desperate to know what happens next

Keep the adrenaline pumping - this should be even more exciting than what came before!

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