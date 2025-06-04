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
        setting: str,
        tone: str,
        character_origin: str,
        power_system: str
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
            if setting == "cultivation":
                setting_prompt = "Create a story set in a world where practitioners seek immortality and power through martial arts and spiritual cultivation."
            elif setting == "academy":
                setting_prompt = "Create a story set in a magical academy where students learn to control their abilities."
            elif setting == "gamelike":
                setting_prompt = "Create a story with RPG-like mechanics such as levels, skills, and quests."
            elif setting == "apocalypse":
                setting_prompt = "Create a story in a world facing an apocalyptic scenario where survival is a daily challenge."
            elif setting == "fantasy":
                setting_prompt = "Create a story in a magical fantasy world with mythical creatures and ancient powers."
            elif setting == "scifi":
                setting_prompt = "Create a story in a futuristic world with advanced technology and space exploration."
            elif setting == "modern":
                setting_prompt = "Create a story set in the modern world, possibly with hidden secrets or supernatural elements."
            
            # Create tone-specific prompt addition
            tone_prompt = ""
            if tone == "optimistic":
                tone_prompt = "The story should have a hopeful tone where challenges are overcome with perseverance and positivity."
            elif tone == "tragic":
                tone_prompt = "The story should have a bittersweet or sorrowful tone where loss, sacrifice, or downfall play key roles."
            elif tone == "epic":
                tone_prompt = "The story should have a grand, larger-than-life tone filled with heroism, trials, and major turning points."
            elif tone == "thrilling":
                tone_prompt = "The story should have a fast-paced, edge-of-your-seat tone full of danger, twists, and suspense."
            elif tone == "mystery":
                tone_prompt = "The story should be driven by secrets, hidden truths, and the uncovering of the unknown."
            elif tone == "romantic":
                tone_prompt = "The story should focus on relationships, love, and emotional connections, but with clear conflicts and plot progression."
            elif tone == "dark":
                tone_prompt = "The story should have a grim, morally complex tone where choices are hard and consequences are heavy."
            elif tone == "whimsical":
                tone_prompt = "The story should have a playful, imaginative tone filled with wonder, oddities, and a sense of magic."
            elif tone == "gritty":
                tone_prompt = "The story should have a realistic, tough tone where survival and resilience are constantly tested."
            elif tone == "philosophical":
                tone_prompt = "The story should be contemplative, focusing on self-discovery, existential questions, and deep themes."
            
            # Create the system prompt
            system_prompt = f"""You are an expert storyteller specializing in interactive fiction.
Create immersive, plot-driven narratives with meaningful choices and dynamic progression.
Your stories should be written in second-person perspective, addressing the reader as "you".

{setting_prompt}
{tone_prompt}

ESSENTIAL STORYTELLING RULES:
1. Set the scene quickly and efficiently (1-2 sentences maximum for setting or description).
2. Introduce a clear GOAL or CONFLICT for the main character within the first few sentences.
3. Create a sense of urgency, risk, or reward in every scene.
4. Focus on ACTION and PLOT over lengthy descriptions or passive feelings.
5. Include unexpected twists or complications to avoid predictability.
6. Make sure the character has agency and meaningful decisions to make.

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that lead to DIVERGENT outcomes (not looping back to the same scenario).
2. Include one RISKY choice, one SAFE choice, and one CLEVER/STRATEGIC choice.
3. Make each choice have clear implications and push the story in a new direction.
4. Avoid "false choices" where all paths lead to the same outcome.

The main character (named {character_name}) has the origin: {character_origin}.
"""

            # Add power system info if it's not "none"
            if power_system != "none":
                system_prompt += f"\nThe character will develop or use {power_system} as their special ability or power system."

            # Create the user prompt
            user_prompt = f"""Create the beginning of an interactive story for a character named {character_name}.

Start by QUICKLY establishing:
1. Their {character_origin} background (1-2 sentences)
2. The {setting} setting (1-2 sentences)
3. AN IMMEDIATE PROBLEM, GOAL OR CONFLICT they must address

Write 300-400 words focusing on PLOT and ACTION, then provide exactly 3 distinct choices that lead to different paths.

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
        setting: str,
        tone: str,
        previous_content: str,
        selected_choice: str
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
            if setting == "cultivation":
                setting_prompt = "This is a story set in a world where practitioners seek immortality and power through martial arts and spiritual cultivation."
            elif setting == "academy":
                setting_prompt = "This is a story set in a magical academy where students learn to control their abilities."
            elif setting == "gamelike":
                setting_prompt = "This is a story with RPG-like mechanics such as levels, skills, and quests."
            elif setting == "apocalypse":
                setting_prompt = "This is a story in a world facing an apocalyptic scenario where survival is a daily challenge."
            elif setting == "fantasy":
                setting_prompt = "This is a story in a magical fantasy world with mythical creatures and ancient powers."
            elif setting == "scifi":
                setting_prompt = "This is a story in a futuristic world with advanced technology and space exploration."
            elif setting == "modern":
                setting_prompt = "This is a story set in the modern world, possibly with hidden secrets or supernatural elements."
            
            # Create tone-specific prompt addition
            tone_prompt = ""
            if tone == "optimistic":
                tone_prompt = "Maintain a hopeful tone where challenges are overcome with perseverance and positivity."
            elif tone == "tragic":
                tone_prompt = "Maintain a bittersweet or sorrowful tone where loss, sacrifice, or downfall play key roles."
            elif tone == "epic":
                tone_prompt = "Maintain a grand, larger-than-life tone filled with heroism, trials, and major turning points."
            elif tone == "thrilling":
                tone_prompt = "Maintain a fast-paced, edge-of-your-seat tone full of danger, twists, and suspense."
            elif tone == "mystery":
                tone_prompt = "Continue driving the story with secrets, hidden truths, and the uncovering of the unknown."
            elif tone == "romantic":
                tone_prompt = "Keep focusing on relationships and emotional connections, but ensure strong plot progression and conflict."
            elif tone == "dark":
                tone_prompt = "Maintain a grim, morally complex tone where choices are hard and consequences are heavy."
            elif tone == "whimsical":
                tone_prompt = "Keep the playful, imaginative tone filled with wonder, oddities, and a sense of magic."
            elif tone == "gritty":
                tone_prompt = "Maintain a realistic, tough tone where survival and resilience are constantly tested."
            elif tone == "philosophical":
                tone_prompt = "Continue the contemplative approach, focusing on self-discovery, existential questions, and deep themes."
            
            # Create the system prompt
            system_prompt = f"""You are an expert storyteller specializing in interactive fiction.
Create immersive, plot-driven narratives with meaningful choices and dynamic progression.
Your stories should be written in second-person perspective, addressing the reader as "you".

{setting_prompt}
{tone_prompt}

ESSENTIAL STORYTELLING RULES:
1. After each choice, ESCALATE the situation - increase the danger, stakes, or complexity.
2. Never return to a safe or static situation - keep pushing the plot forward.
3. Focus on ACTION and PLOT over lengthy descriptions or passive feelings.
4. Include unexpected twists, complications, or surprises to maintain engagement.
5. Maintain consistency with previous story elements while introducing new developments.

CHOICE REQUIREMENTS:
1. Create 3 distinct choices that lead to DIVERGENT outcomes (not looping back to the same scenario).
2. Include one RISKY choice, one SAFE choice, and one CLEVER/STRATEGIC choice.
3. Make each choice have clear implications and push the story in a new direction.
4. Avoid "false choices" where all paths lead to the same outcome.

Maintain consistency with the previous parts of the story.
Your task is to continue the story based on the choice the user has made."""

            # Create the user prompt
            user_prompt = f"""Continue the story for {character_name} based on the previous content and the selected choice.

Previous content:
{previous_content}

Selected choice:
{selected_choice}

IMPORTANT:
1. ESCALATE the situation based on this choice - introduce new complications or raise the stakes
2. Focus on PLOT and ACTION, not just reactions or descriptions
3. Keep the story moving forward with clear progression
4. Introduce a new challenge, obstacle, or opportunity

Write 300-400 words continuing the story based on this choice, then provide exactly 3 new distinct choices that lead to different paths.

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