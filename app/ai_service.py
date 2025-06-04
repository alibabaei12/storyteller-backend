import os
import openai
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .models import Choice

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            
            # Create the system prompt
            system_prompt = f"""You are an expert storyteller specializing in interactive fiction with a focus on {setting} themes.
Create immersive, character-driven narratives with vivid descriptions and engaging dialogue.
Your stories should be written in second-person perspective, addressing the reader as "you".
The story should have a {tone} tone and take place in a {setting} world.
The main character (named {character_name}) has the origin: {character_origin} and uses {power_system} as their power system."""

            # Create the user prompt
            user_prompt = f"""Create the beginning of an interactive story for a character named {character_name}.
Start with an introduction to the character and their world, establishing:
1. Their {character_origin} background
2. The {setting} setting they're in
3. An initial situation that will lead to the first choice point

Write approximately 300-500 words, then provide exactly 3 distinct choices for how the protagonist might proceed.
The choices should be meaningfully different and lead the story in interesting directions.

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
            
            # Create the system prompt
            system_prompt = f"""You are an expert storyteller specializing in interactive fiction with a focus on {setting} themes.
Create immersive, character-driven narratives with vivid descriptions and engaging dialogue.
Your stories should be written in second-person perspective, addressing the reader as "you".
Maintain consistency with the previous parts of the story.
Your task is to continue the story based on the choice the user has made."""

            # Create the user prompt
            user_prompt = f"""Continue the story for {character_name} based on the previous content and the selected choice.

Previous content:
{previous_content}

Selected choice:
{selected_choice}

Write approximately 300-500 words continuing the story based on this choice, then provide exactly 3 new distinct choices for how the protagonist might proceed.
The choices should be meaningfully different and lead the story in interesting directions.

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
                story_match = response_text.split("[CHOICES]")[0].strip()
            
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