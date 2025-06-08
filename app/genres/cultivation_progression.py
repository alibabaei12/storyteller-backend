"""
Cultivation Progression genre for weak-to-strong martial arts stories.
"""
from typing import List, Tuple
import openai
import logging
from ..models import Choice
from ..base_genre import BaseGenre, Genre

# Set up logger
logger = logging.getLogger(__name__)

class CultivationProgression(Genre):
    """Cultivation progression story generator for martial arts weak-to-strong narratives."""
    
    @property
    def genre_name(self) -> str:
        return "Cultivation Progression"
    
    @property 
    def genre_context(self) -> str:
        return "cultivation progression realm"
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Generate a cultivation progression story opening."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        # Import the origin profile method
        from app.ai_service import AIService
        
        # Create character origin profile
        origin_prompt = AIService._create_character_origin_profile(character_origin, "cultivation")
        
        system_prompt = f"""You're an expert manga/manhwa creator specializing in dynamic visual storytelling, engaging plots, and vivid characters.

You will create a compelling, unpredictable chapter for an interactive cultivation manga. The chapter length is flexible (4–8 panels). Organize panels in the most visually interesting, logical, and emotionally impactful sequence possible.

Use {pronouns} pronouns for {character_name}.

{origin_prompt}

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
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
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
        character_origin: str = None
    ) -> Tuple[str, List[Choice]]:
        """Continue a cultivation progression story."""
        
        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)
        
        system_prompt = f"""You're an expert manga/manhwa creator continuing a dynamic cultivation story.

Use {pronouns} pronouns for {character_name}.

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
   - Believable relationships and character motivations explicitly shown.

6. **Story Progression:**
   - Move the narrative forward meaningfully with clear logical progression.
   - Build toward character growth or new story developments with explicit outcomes.

7. **Compelling Setup:**
   - End with choices that naturally arise from your new developments with clear logical connections.

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

---

### 📚 CREATIVE CONTINUATION GUIDELINES:

- Build logically from previous events while introducing fresh elements
- Vary conflict types and scenarios to maintain unpredictability  
- Show character growth through actions and dialogue
- Use vivid sensory details for immersive visual storytelling
- Avoid repetitive patterns or predictable outcomes

---

### 🚫 CONTINUATION PITFALLS TO AVOID:

- Ignoring the consequences of the previous choice
- Repeating similar scenarios or conflicts
- Generic character interactions or dialogue
- Predictable story progression

FORMAT:
[STORY]
(Your dynamic continuation chapter - 4-8 panels sequenced for optimal storytelling impact)
[/STORY]

[CHOICES]
1. (First compelling choice naturally emerging from your story)
2. (Second unique choice based on the situation you created)
3. (Third distinctive choice offering different narrative path)
[/CHOICES]"""

        user_prompt = f"""Continue {character_name}'s cultivation story based on their previous choice.

PREVIOUS CHAPTER:
{previous_content}

PLAYER'S CHOICE:
{selected_choice}

CREATIVE MANDATE:
- Show immediate consequences of the choice visually and emotionally
- Advance the story with fresh developments or revelations  
- Include cultivation techniques with specific qi descriptions
- Create authentic character interactions and dialogue
- Build toward meaningful character or plot progression
- End with choices that emerge naturally from your story developments

Remember: Focus on dynamic visual storytelling that surprises and engages readers. Avoid predictable patterns."""

        try:
            logger.info(f"Continuing cultivation story for {character_name}")
            
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except Exception as e:
            logger.error(f"Error continuing cultivation story: {e}")
            return BaseGenre.create_contextual_fallback(character_name, selected_choice, self.genre_context) 