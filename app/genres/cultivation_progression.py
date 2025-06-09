"""
Cultivation Progression genre for weak-to-strong martial arts stories.
"""
from typing import List, Tuple, Optional, Literal
import openai
import logging
from pydantic import Field
from app.models.models import Choice
from app.models.base_genre import BaseGenre, Genre
import os
import json
import random
from dotenv import load_dotenv
from ..services import AIService  # Fixed import using relative path

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

class CultivationProgression(Genre):
    """Cultivation progression story generator for martial arts weak-to-strong narratives."""
    
    genre_name_value: Literal["Cultivation Progression"] = "Cultivation Progression"
    genre_context_value: Literal["cultivation progression realm"] = "cultivation progression realm"
    
    def __init__(self):
        """Initialize the cultivation progression genre."""
        # We won't use a class attribute anymore
        pass
    
    @property
    def genre_name(self) -> str:
        """Get the genre name."""
        return self.genre_name_value
        
    @property 
    def genre_context(self) -> str:
        """Get the genre context."""
        return self.genre_context_value
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        character_origin: str = "normal",
        big_story_goal: str = None
    ) -> Tuple[str, List[Choice], Optional[str]]:
        """Generate a cultivation progression story opening."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Create character origin profile
        origin_prompt = BaseGenre.create_character_origin_profile(character_origin, "cultivation")
        
        # Add big story goal if provided
        big_goal_prompt = ""
        initial_arc_goal = None
        if big_story_goal:
            big_goal_prompt = f"\n\nMAIN CHARACTER GOAL: {character_name}'s ultimate goal is to {big_story_goal}"
            
            # Initialize memory with a story arc if this is a new story
            try:
                from ..services.story_planner import generate_new_arc_goal
                # Generate an arc goal to return to the caller
                initial_arc_goal = generate_new_arc_goal(big_story_goal, [])
                logger.info(f"Generated initial arc goal: {initial_arc_goal}")
            except Exception as e:
                logger.error(f"Error generating initial arc goal: {e}")
                # Provide a fallback arc goal
                initial_arc_goal = "Survive the sect's brutal outer disciple training."
                logger.info(f"Using fallback arc goal: {initial_arc_goal}")
        
        system_prompt = f"""You're an expert manga/manhwa creator specializing in dynamic visual storytelling, engaging plots, and vivid characters.

You will create a compelling, unpredictable chapter for an interactive cultivation manga. The chapter length is flexible (4–8 panels). Organize panels in the most visually interesting, logical, and emotionally impactful sequence possible.

Use {pronouns} pronouns for {character_name}.

{origin_prompt}{big_goal_prompt}

🔑 **MANDATORY STORY CLARITY RULES (Every Chapter MUST fulfill):**

1. **Clear Logical Sequence**:
   - Every event and action MUST have a logical cause-and-effect relationship clearly shown visually.
   - Explicitly describe how {character_name} moves from one location or situation to another logically and visually.

2. **Meaningful Payoff**:
   - When {character_name} completes a challenge or test, explicitly provide a clear, tangible reward or clear meaningful consequence.
   - Rewards must be visually and narratively clear (e.g., clearly described new cultivation techniques, breakthrough insights, powerful artifacts, allies, cultivation advancement).

3. **Clear Motivation & Intention**:
   - Clearly explain character motivations and dialogue context visually or through internal thought.
   - Do NOT use repetitive cryptic dialogues ("prove your worth") without explicitly clarifying what this means in the current cultivation situation.

4. **Explicit Scene Continuity**:
   - Clearly and logically transition from one chapter scene to the next, explicitly describing where {character_name} is and why they moved there.

🚫 **STRICTLY FORBIDDEN (Do NOT do this):**
- Unexplained scene transitions or location changes.
- Vague rewards or unclear outcomes after cultivation challenges.
- Repetitive cryptic dialogue without explicit clarity or meaningful context.
- Actions or outcomes that confuse readers about what exactly happened.

---

### 📌 MANDATORY STORY OBJECTIVES (Every Chapter MUST creatively fulfill ALL):

1. **Dynamic Scene Intro:**  
   - Set a clear visual location, mood, and initial action. Avoid generic or repetitive setups.

2. **Character Focus (Main character: {character_name}):**  
   - Clearly show personality via unique action or dialogue.
   - Clearly portray cultivation level or emotional state naturally.

3. **Engaging Conflict or Mystery:**  
   - Introduce a creative, unpredictable conflict, mystery, or challenge.
   - Conflict should NOT always be a rival disciple—vary situations (environmental, internal struggle, mysterious entity, mentor/student, political intrigue).

4. **Visual Cultivation Showcase:**  
   - Explicitly name and visually describe at least one cultivation technique.
   - Clearly describe Qi visually (colors, patterns, sensory effects).

5. **Believable Character Interactions:**  
   - Dialogue short (max 15 words per bubble), natural, emotionally expressive.
   - Characters must clearly reflect their personalities and motivations.

6. **Clear Consequences & Progression:**  
   - Visually show immediate consequences or reactions logically following events.
   - Ensure clear character growth, setbacks, or meaningful story shifts.

7. **Intriguing Ending:**  
   - End chapter visually and narratively intriguing, prompting curiosity or anticipation for next chapter.

---

### 📚 CREATIVE GUIDELINES (To ensure freshness and unpredictability):

- Vary conflict types significantly (environmental disasters, internal character struggles, new mentor lessons, unexpected ally arrivals, ancient secrets).
- Introduce unexpected twists or revelations occasionally (hidden identities, secret missions, lost techniques).
- Characters should have clear personal motivations and unique speech patterns or habits.
- Avoid repetitive trope usage (same rival encounter repeatedly, identical training sequences).
- Leverage sensory details (sound, sight, touch) to vividly engage readers visually and emotionally.

---

### 🚫 STRICTLY AVOID (To ensure creative storytelling):

- Predictable panel sequences or repetitive scenario setups.
- Overused clichés ("Rival shows up, mocks hero").
- Vague or abstract storytelling ("mysterious power" without specifics).
- Sudden unexplained character or event introductions.

---

### 🔑 MANDATORY RULES FOR CHOICE GENERATION:
At the conclusion of this chapter, clearly present exactly three visually distinctive and engaging manga/manhwa-style choices naturally arising directly from the current scenario and context.

For EACH CHOICE clearly provide:
- A vivid, visual, and concise description of exactly what {character_name} will do next.
- Clearly indicate how each choice logically connects and progresses from the immediate events just shown.
- Make each choice clearly unique, offering distinctly different narrative possibilities.

### 🎌 CREATIVITY REQUIREMENTS (MANDATORY):
- Choices must naturally match the current chapter's tone, situation, and character's personality.
- Avoid overly repetitive or predictable patterns.
- Use intriguing visual and sensory details to make each choice appealing.

### 🚫 STRICTLY FORBIDDEN IN CHOICES:
- Generic labels (do NOT say "aggressive," "strategic," or "risky/curious").
- Repetitive or vague wording ("fight aggressively," "plan strategically," "explore curiously").
- Abstract or unrelated actions not clearly tied to the current story scenario.

Now, explicitly generate these three compelling, visually engaging choices directly connected to the scene you've created.

FORMAT:
[STORY]
(Your dynamic, creative chapter - 4-8 panels organized for maximum visual and emotional impact)
[/STORY]

[CHOICES]
1. (First compelling choice naturally emerging from your story)
2. (Second unique choice based on the situation you created)
3. (Third distinctive choice offering different narrative path)
[/CHOICES]"""

        user_prompt = f"""Create the opening chapter for {character_name}'s cultivation journey with a {character_origin} background.

CREATIVE MANDATE:
- Make this chapter feel fresh and unpredictable
- Show {character_name}'s personality through actions and dialogue  
- Include a unique conflict or challenge (not just rival mockery)
- Name specific cultivation techniques with vivid qi descriptions
- Create believable character interactions with natural dialogue
- End with compelling choices that emerge naturally from your story

Remember: You have complete creative freedom in panel sequence and pacing. Focus on visual storytelling that would make readers eager for the next chapter."""

        try:
            logger.info(f"Generating cultivation progression story for {character_name}")
            
            # Generate content with retry logic
            story_content, choices = BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
            # Return the generated story, choices, and the initial arc goal
            return story_content, choices, initial_arc_goal
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        # Simple fallback
        return BaseGenre.create_fallback_story(
            character_name,
            f"{character_name} stood in the training grounds of the Iron Will Sect, watching other disciples practice advanced techniques. "
            f"As a {character_origin} disciple at Qi Gathering stage 2, they faced a crucial decision about their cultivation path.",
            [
                Choice(id="1", text="Challenge a rival disciple to test your current abilities"),
                Choice(id="2", text="Seek guidance from an elder about cultivation techniques"),
                Choice(id="3", text="Attempt to learn a forbidden technique in secret")
            ]
        )

    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        character_origin: str = None,
        big_story_goal: str = None,
        memory = None
    ) -> Tuple[str, List[Choice]]:
        """Continue a cultivation progression story."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Add big story goal if provided
        big_goal_prompt = ""
        if big_story_goal:
            big_goal_prompt = f"\n\nMAIN CHARACTER GOAL: {character_name}'s ultimate goal is to {big_story_goal}"
            
        # Add current arc goal if available in memory
        arc_goal_prompt = ""
        if memory and hasattr(memory, 'current_arc_goal') and memory.current_arc_goal:
            arc_goal_prompt = f"\n\nCURRENT ARC GOAL:\n- {memory.current_arc_goal}"
        
        # Format character information if it exists in the content
        character_section = ""
        if "Known characters so far:" in previous_content:
            try:
                # Extract the character section to remove it from the content
                characters_start = previous_content.find("Known characters so far:")
                characters_end = previous_content.find("Remember to:", characters_start)
                if characters_end > characters_start:
                    # Remove the character section from previous content
                    character_info = previous_content[characters_start:characters_end].strip()
                    previous_content = previous_content[:characters_start] + previous_content[characters_end:]
            except:
                pass  # If extraction fails, just continue
        
        system_prompt = f"""You're an expert manga/manhwa creator continuing a dynamic cultivation story.

Use {pronouns} pronouns for {character_name}.
{big_goal_prompt}{arc_goal_prompt}

You will create the next compelling chapter (4–8 panels) that builds meaningfully from the previous choice. Organize panels for maximum visual impact and emotional engagement.

🔑 **MANDATORY STORY CLARITY RULES (Every Chapter MUST fulfill):**

1. **Clear Logical Sequence**:
   - Every event and action MUST have a logical cause-and-effect relationship clearly shown visually.
   - Explicitly describe how {character_name} moves from one location or situation to another logically and visually.

2. **Meaningful Payoff**:
   - When {character_name} completes a challenge or test, explicitly provide a clear, tangible reward or clear meaningful consequence.
   - Rewards must be visually and narratively clear (e.g., clearly described new cultivation techniques, breakthrough insights, powerful artifacts, allies, cultivation advancement).

3. **Clear Motivation & Intention**:
   - Clearly explain character motivations and dialogue context visually or through internal thought.
   - Do NOT use repetitive cryptic dialogues ("prove your worth") without explicitly clarifying what this means in the current cultivation situation.

4. **Explicit Scene Continuity**:
   - Clearly and logically transition from one chapter scene to the next, explicitly describing where {character_name} is and why they moved there.

🚫 **STRICTLY FORBIDDEN (Do NOT do this):**
- Unexplained scene transitions or location changes.
- Vague rewards or unclear outcomes after cultivation challenges.
- Repetitive cryptic dialogue without explicit clarity or meaningful context.
- Actions or outcomes that confuse readers about what exactly happened.

---

### 📌 MANDATORY CONTINUATION OBJECTIVES (Every Chapter MUST creatively fulfill ALL):

1. **Immediate Consequence:**
   - Show the direct, logical result of the previous choice visually and emotionally with clear cause-and-effect.

2. **Character Development:**
   - Advance {character_name}'s cultivation journey, personality, or relationships meaningfully with explicit progress.

3. **Fresh Conflict or Discovery:**
   - Introduce new challenges, revelations, or plot developments with clear visual descriptions.
   - Avoid repetitive scenarios - create variety and progression.

4. **Visual Cultivation Elements:**
   - Include specific named techniques with vivid qi descriptions and clear visual effects.
   - Show cultivation progress, setbacks, or new abilities with tangible, explicit outcomes.

5. **Authentic Interactions:**
   - Natural dialogue (max 15 words per bubble) that reveals character with clear motivations.
   - Characters must clearly reflect their unique personalities and relationships.

6. **Emotional Journey:**
   - Show {character_name}'s emotional reactions to events with visual clarity.
   - Create moments of genuine emotion (triumph, uncertainty, determination, etc).

7. **Next Decision Point:**
   - End at a natural decision point with clear, visually interesting choices.
   - Each choice should offer a unique narrative direction with meaningful consequences.

---

### 📚 CREATIVE GUIDELINES (To ensure freshness and unpredictability):

- Show immediate consequences of the previous choice with clear causality and detail.
- Introduce a surprise element or twist to keep the story dynamic.
- Balance action, dialogue, introspection, and worldbuilding.
- Reveal new aspects of cultivation mechanics or world lore organically through action.
- Create visually striking panels with dynamic composition and emotional impact.

---

### 🚫 STRICTLY AVOID (For quality storytelling):

- Ignoring or glossing over the consequences of the previous choice.
- Generic "training montages" without specific technique details.
- Vague cultivation progress without clear benchmarks.
- Recycling the same conflicts or scenarios repeatedly.
- Overly complex or convoluted plot developments.

---

### 🔑 MANDATORY RULES FOR CHOICE GENERATION:
At the conclusion of this chapter, clearly present exactly three visually distinctive and engaging manga/manhwa-style choices naturally arising directly from the current scenario and context.

For EACH CHOICE clearly provide:
- A vivid, visual, and concise description of exactly what {character_name} will do next.
- Clearly indicate how each choice logically connects and progresses from the immediate events just shown.
- Make each choice clearly unique, offering distinctly different narrative possibilities.

FORMAT:
[STORY]
(Your dynamic, creative continuation chapter - 4-8 panels organized for maximum visual and emotional impact)
[/STORY]

[CHOICES]
1. (First compelling choice naturally emerging from your story)
2. (Second unique choice based on the situation you created)
3. (Third distinctive choice offering different narrative path)
[/CHOICES]"""

        user_prompt = f"""Continue {character_name}'s cultivation progression story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

Now, show the immediate consequences and progression that naturally follows from this choice with:
- Clear cause-and-effect relationship to the chosen action
- Specific cultivation techniques with vivid qi descriptions
- Character development and emotional reactions
- Fresh conflict or challenge
- Natural dialogue that reveals character

Remember: You have complete creative freedom in panel sequence and pacing. Focus on visual storytelling that would make readers eager for the next chapter."""

        try:
            logger.info(f"Continuing cultivation progression story for {character_name}")
            
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except Exception as e:
            logger.error(f"Error continuing cultivation progression story: {e}")
            return BaseGenre.create_contextual_fallback(character_name, selected_choice, self.genre_context) 