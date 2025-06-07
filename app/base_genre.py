"""
Base class for story genre implementations with shared functionality.
"""
from typing import List, Tuple
from abc import ABC, abstractmethod
from .models import Choice
import openai
import time
import logging

# Set up logger
logger = logging.getLogger(__name__)


class BaseGenre:
    """Base class for all story genres with shared functionality."""
    
    @staticmethod
    def create_language_prompt(language_complexity: str) -> str:
        """Create language complexity prompt based on user preference."""
        if language_complexity == "simple":
            return "Use simple, clear language that is easy to understand. Avoid complex vocabulary or long sentences."
        elif language_complexity == "moderate":
            return "Use moderate language complexity with some advanced vocabulary, but keep it accessible."
        elif language_complexity == "complex":
            return "Use rich, sophisticated language with advanced vocabulary and complex sentence structures."
        return ""
    
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
    def generate_story_with_openai(system_prompt: str, user_prompt: str, character_name: str, max_tokens: int = 1500, temperature: float = 0.8) -> str:
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
            
            return response.choices[0].message.content.strip()
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
        Parse the AI response into story content and choices with strict validation.
        Raises ValueError if parsing fails instead of falling back to generic choices.
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
                    raise ValueError("No [STORY] or [CHOICES] markers found in response")
            
            # Extra safety: Remove any [CHOICES] sections that might still be in the content
            if "[CHOICES]" in story_match:
                story_match = story_match.split("[CHOICES]")[0].strip()
                
            # Remove "[STORY]" or "[/STORY]" tags that might appear in the content itself
            story_match = story_match.replace("[STORY]", "").replace("[/STORY]", "").strip()
            
            if not story_match or len(story_match) < 50:
                raise ValueError(f"Story content too short: {len(story_match)} characters")
            
            # Extract choices
            choices = []
            if "[CHOICES]" in response_text and "[/CHOICES]" in response_text:
                choices_section = response_text.split("[CHOICES]")[1].split("[/CHOICES]")[0].strip()
                choice_lines = choices_section.split("\n")
                
                # Parse individual choices
                choice_count = 0
                for line in choice_lines:
                    if line.strip():
                        # Remove numbers and dots from the beginning (e.g., "1. ", "2. ", etc.)
                        choice_text = line.strip()
                        # Try to remove common numbering patterns
                        import re
                        choice_text = re.sub(r'^\d+\.\s*', '', choice_text)
                        choice_text = re.sub(r'^\d+\s+', '', choice_text)
                        
                        if choice_text and len(choice_text) > 5:
                            choice_count += 1
                            choices.append(Choice(id=str(choice_count), text=choice_text))
            else:
                raise ValueError("No [CHOICES] section found in response")
            
            # Validate we have exactly 3 meaningful choices
            if len(choices) < 3:
                raise ValueError(f"Not enough valid choices found: {len(choices)} (need 3)")
            
            # Validate choice quality - reject generic choices
            generic_phrases = [
                "continue your journey", "try a different approach", "reflect on your situation",
                "proceed cautiously", "take a bold approach", "reconsider your options",
                "focus on improving", "seek guidance", "take on a challenging"
            ]
            
            for choice in choices:
                choice_lower = choice.text.lower()
                if any(phrase in choice_lower for phrase in generic_phrases):
                    raise ValueError(f"Generic fallback choice detected: {choice.text}")
            
            return story_match, choices[:3]  # Take only first 3 choices
            
        except Exception as e:
            logger.warning(f"Story parsing failed: {e}")
            logger.debug(f"Response preview: {response_text[:200]}...")
            raise ValueError(f"Failed to parse story response: {e}")
    
    @staticmethod
    def generate_story_with_retry(system_prompt: str, user_prompt: str, character_name: str, max_retries: int = 3) -> Tuple[str, List[Choice]]:
        """
        Generate story with retry logic when parsing fails.
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for {character_name}")
                    time.sleep(1)  # Brief delay between retries
                
                # Generate content
                content = BaseGenre.generate_story_with_openai(system_prompt, user_prompt, character_name)
                
                # Parse with strict validation
                story_content, choices = BaseGenre.parse_story_response_strict(content)
                
                if attempt > 0:
                    logger.info(f"Retry successful on attempt {attempt}")
                
                return story_content, choices
                
            except ValueError as e:
                last_error = e
                logger.warning(f"Parsing attempt {attempt + 1} failed: {e}")
                continue
            except openai.OpenAIError as e:
                # For OpenAI API errors, don't retry unless it's rate limiting
                logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if "rate_limit" in str(e).lower() and attempt < max_retries:
                    logger.info(f"Rate limit detected, retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)  # Exponential backoff for rate limits
                    continue
                raise
            except Exception as e:
                # For other non-parsing errors, don't retry
                logger.error(f"Non-retryable error: {e}")
                raise
        
        # If all retries failed, raise the last parsing error
        logger.error(f"All {max_retries + 1} attempts failed for {character_name}")
        raise ValueError(f"Story generation failed after {max_retries + 1} attempts. Last error: {last_error}")


class Genre(ABC):
    """Abstract base class that all story genres must inherit from."""
    
    @abstractmethod
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        language_complexity: str
    ) -> Tuple[str, List[Choice]]:
        """Generate an initial story for this genre."""
        pass
    
    @abstractmethod
    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        language_complexity: str
    ) -> Tuple[str, List[Choice]]:
        """Continue a story for this genre based on the selected choice."""
        pass
    
    @property
    @abstractmethod
    def genre_name(self) -> str:
        """Return the human-readable name of this genre."""
        pass
    
    @property
    @abstractmethod
    def genre_context(self) -> str:
        """Return the context string used for fallbacks."""
        pass 