"""
Base class for story genre implementations with shared functionality.
"""
import logging
import time
from abc import abstractmethod
from typing import List, Tuple

import openai
from pydantic import BaseModel

from app.models.models import Choice

# Set up logger
logger = logging.getLogger(__name__)


class BaseGenre:
    """Base class for all story genres with shared functionality."""
    
    @staticmethod
    def create_gender_pronouns(character_gender: str) -> str:
        """Get appropriate pronouns for character gender."""
        if character_gender == "male":
            return "he/him/his"
        elif character_gender == "female":
            return "she/her/hers"
        elif character_gender == "non-binary":
            return "they/them/their"
        else:
            return "they/them/their"
            
    @staticmethod
    def create_character_origin_profile(character_origin: str, setting: str) -> str:
        """Create character origin profile for prompt engineering."""
        if character_origin == "reincarnated":
            return f"The character was reincarnated from another world with knowledge of their past life."
        elif character_origin == "weak":
            return f"The character starts with major disadvantages and is considered weak in this world."
        elif character_origin == "hidden":
            return f"The character has hidden talents or a secret background not apparent to others."
        elif character_origin == "genius":
            return f"The character is naturally talented and learns much faster than others."
        elif character_origin == "fallen":
            return f"The character once had high status but has fallen from grace and must rebuild."
        else:  # normal/ordinary
            return f"The character has a normal background with no special advantages or disadvantages."
    
    @staticmethod
    def create_character_origin_profile(character_origin: str, character_name: str) -> str:
        """Create character origin profile for prompt engineering."""
        if character_origin == "reincarnated":
            return f"""The character was reincarnated from another world with extensive knowledge and unique
             perspectives from their past life. This past life experience should constantly provide {character_name} 
             with unconventional solutions, advanced insights into cultivation techniques, or surprising foresight,
              often setting them apart from others. Showcase how this past knowledge gives {character_name}
               an edge or creates unique internal conflicts."""
        elif character_origin == "weak":
            return f"""The character starts with major disadvantages and is considered weak in this world.
             This 'weakness' should be a constant challenge, forcing {character_name} to rely on cunning, sheer grit, 
             resourcefulness, or unconventional training methods to overcome obstacles. Emphasize their struggle and 
             their journey to defy expectations, making small gains feel significant."""
        elif character_origin == "hidden":
            return f"""The character has hidden talents or a secret background not apparent to others. 
            This hidden aspect should be hinted at, subtly influencing {character_name}'s abilities or decision-making.
             Occasionally, this hidden power or background should manifest unexpectedly, surprising both {character_name} 
             and other characters, and potentially drawing unwanted attention."""
        elif character_origin == "genius":
            return f"""The character is naturally talented and learns much faster than others.
             This genius should be consistently demonstrated through rapid comprehension of complex techniques, 
             intuitive problem-solving, or groundbreaking discoveries. While gifted, ensure {character_name}
              still faces challenges, perhaps due to jealousy, lack of experience, or overconfidence,
               rather than just raw power."""
        elif character_origin == "fallen":
            return f"""The character once had high status but has fallen from grace and must rebuild. 
            This 'fallen' status should influence {character_name}'s current challenges, motivations 
            (e.g., reclaiming honor, seeking revenge, protecting someone), and interactions with others 
            (some might scorn them, others might secretly support). Showcase the struggle to regain their standing 
            and the internal conflict of their past versus present."""
        else:  # normal/ordinary
            return f"""The character has a normal background with no special advantages or disadvantages. 
            Their progression should primarily come from hard work, mentorship, and relatable growth, making their 
            achievements feel earned and grounded. Focus on their perseverance and gradual mastery of challenges 
            through dedication."""

    @staticmethod
    def generate_story_with_openai(system_prompt: str, user_prompt: str, character_name: str, max_tokens: int = 1200, temperature: float = 0.8) -> str:
        """Generate story content using OpenAI API."""
        try:
            logger.info(f"Generating story for {character_name}")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # ✅ LOG THE FULL RESPONSE FOR GENRE DEBUGGING  
            logger.info(f"🎭 GENRE GPT RESPONSE ({len(response_text)} chars):")
            logger.info("=" * 60)
            logger.info(response_text)
            logger.info("=" * 60)
            
            return response_text
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating story for {character_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating story for {character_name}: {e}")
            raise
    
    @staticmethod
    def create_fallback_story(character_name: str, fallback_content: str, fallback_choices: List[Choice]) -> Tuple[str, List[Choice]]:
        """Create fallback story content when AI generation fails."""
        return fallback_content, fallback_choices
    
    @staticmethod
    def create_contextual_fallback(character_name: str, selected_choice: str, genre_context: str) -> Tuple[str, List[Choice]]:
        """Create contextual fallback content based on the previous choice and genre."""
        
        # Create contextual story content based on the selected choice
        story_content = f"{character_name} takes a deep breath and decides to {selected_choice.lower()}. " \
                       f"The path ahead remains uncertain, but {character_name}'s determination grows stronger. " \
                       f"In this {genre_context}, every choice shapes the journey that lies ahead..."
        
        # Create contextual choices based on the genre
        if "cultivation" in genre_context.lower():
            choices = [
                Choice(id="1", text="Focus on inner spiritual energy and meditation"),
                Choice(id="2", text="Seek wisdom from experienced cultivators"),  
                Choice(id="3", text="Challenge oneself with intensive training")
            ]
        elif "fantasy" in genre_context.lower():
            choices = [
                Choice(id="1", text="Explore the magical energies in this realm"),
                Choice(id="2", text="Search for allies in this mystical world"),
                Choice(id="3", text="Investigate the source of mysterious phenomena")  
            ]
        elif "academy" in genre_context.lower():
            choices = [
                Choice(id="1", text="Study advanced magical theory and techniques"),
                Choice(id="2", text="Build relationships with fellow students"),
                Choice(id="3", text="Participate in academy challenges and competitions")
            ]
        else:
            # Generic but still contextual fallback
            choices = [
                Choice(id="1", text="Carefully analyze the current situation"),
                Choice(id="2", text="Take action based on instinct and courage"),
                Choice(id="3", text="Seek additional information before proceeding")
            ]
        
        return story_content, choices
    
    @staticmethod
    def parse_story_response_strict(response_text: str) -> Tuple[str, List[Choice]]:
        """
        Parse the AI response into story content and choices with robust parsing.
        Now uses the same improved logic as the main AI service.
        """
        try:
            logger.debug(f"Parsing genre response ({len(response_text)} chars): {response_text[:200]}...")
            
            story_content = ""
            choices = []
            
            # Clean up the response text
            response_text = response_text.strip()
            
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
                        if choice_text and len(choice_text) > 8:
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
                            if choice_text and len(choice_text) > 8:
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
                    # Look for numbered choices
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
                            if len(choices) >= 3:
                                break
                
                # If still no choices found, try to extract any lines that look like choices
                if len(choices) < 3:
                    all_lines = [line.strip() for line in lines if line.strip()]
                    for line in all_lines[-10:]:  # Look in the last 10 lines
                        if (len(line) > 15 and 
                            not re.match(r'^(STORY|CHOICES|\\[/?STORY\\]|\\[/?CHOICES\\]):?$', line, re.IGNORECASE) and
                            len(choices) < 3):
                            # Remove any leading numbers or bullets
                            clean_line = re.sub(r'^[\d\-\*\•]\s*[\.\)]*\s*', '', line).strip()
                            if len(clean_line) > 10:
                                choices.append(Choice(id=str(len(choices) + 1), text=clean_line))
            
            # Validate story content with more lenient requirements
            if not story_content or len(story_content) < 20:
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
                else:
                    raise ValueError(f"Story content too short or missing: {len(story_content)} characters")
            
            # Validate choices with more lenient requirements
            if len(choices) < 2:
                raise ValueError(f"Not enough choices found: {len(choices)} (need at least 2)")
            
            # Fill in missing choices if we have fewer than 3
            while len(choices) < 3:
                choice_num = len(choices) + 1
                generic_choice = f"Take action based on the current situation (Option {choice_num})"
                choices.append(Choice(id=str(choice_num), text=generic_choice))
                logger.info(f"Added generic choice {choice_num}")
            
            # Return only the first 3 valid choices
            final_choices = choices[:3]
            logger.info(f"Successfully parsed genre response: story={len(story_content)} chars, choices={len(final_choices)}")
            return story_content, final_choices
        
        except Exception as e:
            logger.error(f"Error parsing genre response: {e}")
            # Return a very basic fallback in case of parsing error
            return (
                "The adventure continues...",
                [
                    Choice(id="1", text="Continue forward cautiously"),
                    Choice(id="2", text="Take a bold approach to the situation"),
                    Choice(id="3", text="Look for alternative options")
                ]
            )
    
    @staticmethod
    def generate_story_with_retry(system_prompt: str, user_prompt: str, character_name: str, max_retries: int = 3) -> Tuple[str, List[Choice]]:
        """Generate story content with retry logic for error handling."""
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                # Generate content with OpenAI
                response_text = BaseGenre.generate_story_with_openai(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    character_name=character_name
                )
                
                # Parse the response
                return BaseGenre.parse_story_response_strict(response_text)
            except Exception as e:
                attempt += 1
                last_error = e
                logger.warning(f"Story generation attempt {attempt} failed: {e}")
                time.sleep(1)  # Brief pause before retrying
        
        # If we've reached here, all attempts failed
        logger.error(f"All {max_retries} story generation attempts failed: {last_error}")
        return BaseGenre.create_fallback_story(
            character_name,
            f"The story begins with {character_name} facing an important decision...",
            [
                Choice(id="1", text="Proceed with determination"),
                Choice(id="2", text="Seek more information first"),
                Choice(id="3", text="Consider alternative approaches")
            ]
        )


class Genre(BaseModel):
    """Base class for story genres."""
    
    @abstractmethod
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Generate a story opening for the given character."""
        pass
    
    @abstractmethod
    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Continue a story based on the previous content and selected choice."""
        pass
    
    @property
    @abstractmethod
    def genre_name(self) -> str:
        """Get the genre name."""
        pass
    
    @property
    @abstractmethod
    def genre_context(self) -> str:
        """Get the genre context for fallback stories."""
        pass

    def get_prompt_rules(self) -> str:
        """Get genre-specific prompt rules."""
        return ""
    
    def get_prompt_style(self) -> str:
        """Get genre-specific prompt style."""
        return "" 