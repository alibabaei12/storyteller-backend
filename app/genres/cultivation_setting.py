"""
Cultivation setting for weak-to-strong martial arts stories.
"""
import logging
from typing import List, Tuple, Optional, Literal, Any

import openai
from dotenv import load_dotenv
import re
import os

from app.models.base_genre import BaseGenre, Genre
from app.models.models import Choice
from ..services.story_planner import generate_new_arc_goal, add_character_to_memory, extract_characters_from_content
# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# Get the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Common prompt templates
CLARITY_RULES_TEMPLATE = """
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
"""

STORY_OBJECTIVES_TEMPLATE = """
## Story Objectives & Character Elements

1. **Character Growth:** Show {character_name}'s progression toward both personal development (values, emotions, wisdom) and power development (cultivation techniques, skills, abilities) in this chapter.

2. **World Elements:** Weave in cultivation system aspects (qi/energy types, cultivation techniques, martial arts), sect politics, mystical creatures, or spiritual treasures that enrich your world.

3. **Connected Plot:** Advance the main narrative toward the {arc_goal_text} through meaningful events, discoveries, or conflicts that show clear progress.

4. **Supporting Characters:** Maintain continuity with existing characters. Remember their relationships to {character_name} and reference their previous interactions. If introducing new characters, make them distinctive and memorable.

5. **{style} Tone:** Infuse the chapter with {style} elements in the descriptions, dialogue tone, and overall mood.

6. **Arc Pacing Guidance:** 
If this is **not** the final chapter of the arc:
- This chapter should build tension, deepen mystery, develop relationships, or evolve a technique. 
- Avoid resolving major conflicts or unlocking core secrets too soon.

If this **is** the final chapter of the arc:
- Deliver a satisfying resolution to the arc’s core challenge or mystery.
- Include a key transformation in {character_name}, emotionally or in cultivation.
- Hint at a new opportunity, challenge, or threat that sets up the next arc without fully starting it.

### 🎯 Long-Term Goal & Arc Progression Alignment:

- Every chapter must clearly reflect how the current arc relates to {character_name}’s ultimate goal: {big_goal_prompt}.
- Treat each arc as a **chapter in a long journey** toward that goal — not a distraction.
- This chapter’s events should contribute meaningfully to the arc's immediate purpose, while subtly reinforcing the protagonist’s deeper motivation.
- Avoid arcs or scenes that feel disconnected or episodic — everything should feel like it’s building toward something bigger.
"""

CHOICE_GUIDANCE_TEMPLATE = """
🎲 **CHOICE GENERATION RULES**

At the end of the chapter, generate **3 distinct, meaningful player choices**.

Each choice must:
- Be **vivid**, visual, and clearly describe the action the protagonist will take next
- Logically follow from the **chapter’s ending situation**
- Offer emotionally and strategically different directions (e.g., bold, cautious, diplomatic, mysterious)
- Help the player progress the **current arc goal** in varied ways — without resolving the full arc

Creativity Guidelines:
- At least one choice should open up a new strategy, ally, route, or clue
- One choice can be personal or introspective (e.g., training, reflection, forging bonds)
- Use immersive language: sights, sounds, emotions, not vague plans

🚫 Forbidden:
- Generic verbs like "fight aggressively," "explore curiously," "train harder"
- Repeating a line or phrase from the chapter verbatim
- Choices that end the entire arc too early or skip logical progression
- Starting a choice with “{character_name} decides to...” or “chooses to...”

Present the choices as cleanly formatted numbered items (1, 2, 3).
"""

# Replace the existing FORMAT_TEMPLATE with a combined version
FORMAT_TEMPLATE = """
⚠️ **CRITICAL FORMAT REQUIREMENT**:
You MUST use the EXACT format shown below:

[STORY]
(Your dynamic, creative {story_type} - 4-8 panels organized for maximum visual and emotional impact. Use '---' on a new line to separate panels, but do NOT include "Panel X:" labels or numbers. Each panel should flow naturally into the next with clear visual transitions.)
[/STORY]

[CHOICES]
1. (First compelling choice naturally emerging from your story)
2. (Second unique choice based on the situation you created)
3. (Third distinctive choice offering different narrative path)
[/CHOICES]

Failure to follow this exact format will result in errors. Do not use any other format or tags.
"""

# Add this new template for arc pacing
ARC_PACING_TEMPLATE = """
### Current Story Arc ({arc_progress})
Arc Goal → **{current_arc_goal}**

You are writing **Chapter {current_chapter} of {chapters_per_arc}** for this arc.  
**Do NOT resolve the arc goal in this chapter unless it's the final chapter ({chapters_per_arc}) of the arc.**  
Instead, show **incremental progress** (e.g., discover a clue, gain a partial remedy, suffer a setback).  
The arc goal should only be completed in Chapter {chapters_per_arc}.
"""

# Add this new template for forbidden completion
FORBIDDEN_COMPLETION_TEMPLATE = """
- The ultimate goal is for the ENTIRE story's completion, not a single chapter
- A chapter may show progress or small victories, but the main journey CANNOT be completed yet
- Completing the current arc goal before its final chapter.
- Resolving the main story goal ({big_story_goal}) prematurely.
"""

PANEL_STRUCTURE_TEMPLATE = """
📘 **MANDATORY PANEL STRUCTURE (Use 6 to 8 panels per chapter):**

- Each chapter should advance the current arc slightly — not conclude it.
- Avoid rushing events; focus on pacing, emotion, and momentum.

🪜 Panel Guidelines (Slow Burn Pacing):

1. **Panel 1 – Status Check or Quiet Start**
   - Continue naturally from last chapter
   - Set the tone, show calm before action or hint at tension

2. **Panel 2 – Minor Event, Challenge, or Movement**
   - Introduce a small obstacle, discovery, or new location (within reason)
   - Keep new characters minimal — only if necessary for arc

3. **Panel 3 – Character Interaction or Thought**
   - Include *either* internal monologue or conversation with someone from previous chapters
   - Advance emotional depth or build tension

4. **Panel 4 – Midpoint Turn**
   - Something shifts: mood, info, enemy appears, interruption
   - Not always dramatic, but forward-moving

5. **Panel 5 – Small Action or Reaction**
   - A decision is made or an action taken — but don’t resolve the issue yet

6. **Panel 6 – Build Toward Conflict or Clue Drop**
   - Lay groundwork for a major moment *2–3 chapters away*
   - Optional: show small reveal or thematic callback

7. **(Optional) Panel 7 – Atmosphere / Lore / Foreshadowing**
   - Expand world subtly — a legend mentioned, a rune glows strangely, someone observes from afar

8. **Panel 8 – Cliffhanger or Emotional Hook**
   - Don’t resolve the situation — raise a question, hint danger, or create anticipation

📏 **Formatting Rule:**
After each panel, insert a horizontal line with three dashes (---), followed by a new line.
"""

INTROSPECTION_RULE = """
Include a short emotional reflection moment tied to the protagonist's character origin.

- This reflection can express ambition, insecurity, determination, guilt, pressure, or a memory — depending on their origin.
- It should feel **natural** in the scene (not forced) and add emotional weight to the chapter.
- Use the CHARACTER BACKGROUND info provided to inspire the tone of this reflection.

Keep it brief (1–3 sentences) and consistent with the story’s pacing and mood.
"""

DIALOGUE_RULE = """
💬 **DIALOGUE REQUIREMENT**

Each important character in the chapter (especially rivals, allies, mentors, or enemies) should speak at least once using direct dialogue.

- Use natural, emotionally expressive lines — not just exposition
- Allow for teasing, rivalry, doubt, admiration, or fear
- Do not summarize key character interactions; let them speak in their own words
- Dialogue should match the tone (e.g., dramatic, playful, tense)

If the protagonist speaks, they may also include internal thoughts in response.
"""

class CultivationSetting(Genre):
    """Cultivation progression story generator for martial arts weak-to-strong narratives."""

    genre_name_value: Literal["Cultivation Progression"] = "Cultivation"
    genre_context_value: Literal["cultivation progression realm"] = "cultivation realm"

    def __init__(self):
        """Initialize the cultivation genre."""
        # We won't use a class attribute anymore
        pass

    @staticmethod
    def _clean_panel_labels(story_content: str) -> str:
        """Remove panel numbering and labels from story content."""
        # Clean up any panel or scene numbering/labels that might appear
        story_content = re.sub(r'Panel \d+:', '', story_content)
        story_content = re.sub(r'Panel \d+', '', story_content)
        story_content = re.sub(r'Scene \d+:', '', story_content)
        story_content = re.sub(r'Scene \d+', '', story_content)
        # Also remove any numbered items at the start of each section
        story_content = re.sub(r'^\d+\.\s*', '', story_content, flags=re.MULTILINE)
        return story_content

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
            style: str = "normal",
            big_story_goal: str = None
    ) -> tuple[str, list[Choice], str, list[str]]:
        """Generate a cultivation story opening."""

        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)

        # Create character origin profile
        origin_prompt = BaseGenre.create_character_origin_profile(character_origin, character_name) 

        # Add big story goal if provided
        big_goal_prompt = ""
        arc_goals = []
        if big_story_goal:
            big_goal_prompt = f"\n\nMAIN CHARACTER GOAL: {character_name}'s ultimate goal is to {big_story_goal}"

            # Initialize memory with a story arc if this is a new story
            # Generate multiple arc goals to return to the caller
            arc_goals = generate_new_arc_goal(big_story_goal, [])
            initial_arc_goal = arc_goals[0] if arc_goals else "Survive the sect's brutal outer disciple training."
            logger.info(f"Generated {len(arc_goals)} arc goals. Initial arc goal: {initial_arc_goal}")

        # Add emotional and flaw prompts
        emotional_flaw_prompt = ""
        if big_story_goal:
            from ..services.story_planner import build_emotional_and_flaw_injection
            emotional_flaw_prompt = build_emotional_and_flaw_injection(big_story_goal)

        # Create story arc awareness section with arc pacing
        arc_awareness = ""
        if arc_goals and len(arc_goals) > 0:
            arc_progress = f"1/{len(arc_goals)} chapters"
            arc_awareness = f"""
## Story Arc Structure
This is a multi-arc story with a total of {len(arc_goals)} planned story arcs, all working toward the ultimate goal of: **{big_story_goal}**.

{ARC_PACING_TEMPLATE.format(
    arc_progress=arc_progress,
    current_arc_goal=initial_arc_goal,
    current_chapter=1,
    chapters_per_arc=7
)}

### Future Story Arcs (these will come later, but can be foreshadowed):
{', '.join([f'"{arc}"' for arc in arc_goals[1:]])}

Each arc will span approximately 7 chapters, with the story progressing meaningfully through each chapter and arc."""

        # Build the system prompt using shared templates
        clarity_rules = CLARITY_RULES_TEMPLATE.format(character_name=character_name)
        
        # Add origin integration to clarity rules for initial story
        origin_integration = f"""
5. **Origin Integration**:
   - The **{origin_prompt}** must be actively reflected and demonstrated through {character_name}'s actions, thoughts, problem-solving approaches, and interactions within the chapter. It should directly influence the plot's progression or a key moment.
"""
        clarity_rules += origin_integration
        

        # Format story objectives with the initial arc goal
        story_objectives = STORY_OBJECTIVES_TEMPLATE.format(
            character_name=character_name,
            style=style,
            arc_goal_text=initial_arc_goal,
            big_goal_prompt=big_goal_prompt
        )
        
        # Add intriguing ending requirement for first chapter
        story_objectives += """
7. **Intriguing Ending:**  
   - End chapter visually and narratively intriguing, prompting curiosity or anticipation for next chapter, Setting up next step in current arc
"""
        
        # Add creative enhancements specific to first chapter
        creative_enhancements = """
---

### 📚 Creative Enhancements. (To ensure freshness and unpredictability):

- Vary conflict types significantly (environmental disasters, internal character struggles, new mentor lessons, unexpected ally arrivals, ancient secrets, new test or tornoment) while staying true to the overall tone and typical scenarios of the {style} genre.".
- Introduce unexpected twists or revelations occasionally (hidden identities, secret missions, lost techniques) that serve the current arc's progression
- Characters should have clear personal motivations and unique speech patterns or habits.
- Avoid repetitive trope usage (same rival encounter repeatedly, identical training sequences).
- Leverage sensory details (sound, sight, touch) to vividly engage readers visually and emotionally.

---

## Global Prohibitions & Anti-Patterns

🚫 **STRICTLY FORBIDDEN (Do NOT do this):**
- Unexplained scene transitions or location changes.
- Vague rewards or unclear outcomes after cultivation challenges.
- Repetitive cryptic dialogue without explicit clarity or meaningful context.
- Actions or outcomes that confuse readers about what exactly happened.
- Including choice prompts or choice options within the [STORY] section. 
- All three choices must be narrowly focused on the immediate scene (e.g. only three fight variations). At least one must shift the method or context of arc progression.

"""

        # Add the forbidden completion rules
        if big_story_goal:
            creative_enhancements += FORBIDDEN_COMPLETION_TEMPLATE.format(big_story_goal=big_story_goal)

        creative_enhancements += """
---

### 🚫 STRICTLY AVOID (To ensure creative storytelling):

- Predictable panel sequences or repetitive scenario setups.
- Overused clichés ("Rival shows up, mocks hero").
- Vague or abstract storytelling ("mysterious power" without specifics).
- Sudden unexplained character or event introductions.
- Introducing a new overarching story problem or concluding a major arc within a single chapter.
- Making choices look like they are the continuation of the story
- Including any "Panel X:" or numbered panel labels - ONLY use '---' on a new line to separate panels.
"""
        
        # Choice guidance with initial arc reference
        initial_choice_guidance = f"""
### 🔑 MANDATORY RULES FOR CHOICE GENERATION:
At the conclusion of this chapter, clearly present exactly three visually distinctive and engaging manga/manhwa-style choices naturally arising directly from the current scenario and context. These choices should move {character_name} forward within the current arc (working towards {initial_arc_goal}).
"""
        
        choice_guidance = initial_choice_guidance + CHOICE_GUIDANCE_TEMPLATE.format(
            character_name=character_name,
            style=style
        )
        
        # Add specific initial chapter requirements
        choice_guidance += """
- Each choice has to be inside of the [CHOICES] section.
"""
        
        # Format template specifying this is the opening chapter
        format_section = FORMAT_TEMPLATE.format(
            story_type="opening chapter"
        )

        # Assemble the full system prompt
        system_prompt = f"""You're an expert manga/manhwa creator specializing in dynamic visual storytelling, engaging plots, and vivid characters.
You will create a compelling, unpredictable chapter for an interactive cultivation manga/manhwa. The chapter length is flexible (4–8 panels). Organize panels in the most visually interesting, logical, and emotionally impactful sequence possible. Use '---' on a new line to separate panels, but DO NOT include any "Panel X:" labels or numbering.

## 1. Role & Story Setup.
Use {pronouns} pronouns for {character_name}.
**Story Style/Genre:** {style} - Ensure every aspect of the chapter (plot, character interactions, conflict, mood) aligns perfectly with this genre.

{origin_prompt} {big_goal_prompt}

{arc_awareness}

{clarity_rules}

{story_objectives}

{creative_enhancements}

{choice_guidance}

{emotional_flaw_prompt}

{PANEL_STRUCTURE_TEMPLATE}

{INTROSPECTION_RULE}

{DIALOGUE_RULE}

{format_section}"""

        user_prompt = f"""Create the opening chapter for {character_name}'s cultivation journey with a {character_origin} background.

**Big Goal for the entire story:** {big_story_goal}
**Current Arc Goal (First of {len(arc_goals)}):** {initial_arc_goal}

CREATIVE MANDATE:
- Make this chapter feel fresh and unpredictable
- Show {character_name}'s personality through actions and dialogue  
- Include a unique conflict or challenge (not just rival mockery) that serves the Current Arc Goal
- Name specific cultivation techniques with vivid qi descriptions
- Create believable character interactions with natural dialogue
- End with compelling choices that emerge naturally from your story and lead to the next step within the current arc
"""

        user_prompt += """

Remember: You have complete creative freedom in panel sequence and pacing. Focus on visual storytelling that would make readers eager for the next chapter. Use '---' on a new line to separate panels, but DO NOT include any 'Panel X:' labels or numbering.

After your story but before the choices, please identify any NEW characters you introduced in THIS chapter. Format them like this:

[NEW CHARACTERS]
Name: [Character's actual name]
Relationship: [Their relationship to the protagonist - Friend, Rival, Mentor, etc.]
Sect: [Their sect or organization if applicable]
Role: [Their role or position if applicable]

// Add additional characters with the same format if there are multiple
[/NEW CHARACTERS]

If no new characters were introduced in this chapter, simply omit this section.
"""

        # Generate content
        logger.info(f"Generating cultivation progression story for {character_name}")
        story_content, choices = BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
        
        # Clean up any panel or scene numbering/labels that might still appear
        story_content = self._clean_panel_labels(story_content)
        
        # Return the generated story, choices, initial arc goal, and all arc goals
        return story_content, choices, initial_arc_goal, arc_goals

    def continue_story(
            self,
            character_name: str,
            character_gender: str,
            previous_content: str,
            selected_choice: str,
            character_origin: str = None,
            big_story_goal: str = None,
            memory=None,
            style: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """Continue a cultivation progression story."""

        # Create gender-specific pronouns
        pronouns = BaseGenre.create_gender_pronouns(character_gender)

        # Create character origin profile
        origin_prompt = ""
        if character_origin:
            origin_prompt = BaseGenre.create_character_origin_profile(character_origin, character_name)

        # Add big story goal if provided
        big_goal_prompt = ""
        if big_story_goal:
            big_goal_prompt = f"\n\nMAIN CHARACTER GOAL: {character_name}'s ultimate goal is to {big_story_goal}"

        # Add emotional and flaw prompts
        emotional_flaw_prompt = ""
        if big_story_goal:
            from ..services.story_planner import build_emotional_and_flaw_injection
            emotional_flaw_prompt = build_emotional_and_flaw_injection(big_story_goal)

        # Create arc progression awareness
        arc_progression = ""
        current_arc_goal = ""
        if memory and hasattr(memory, 'arcs') and memory.arcs and len(memory.arcs) > memory.current_arc_index:
            current_arc_goal = memory.arcs[memory.current_arc_index]
            total_arcs = len(memory.arcs)
            current_arc_num = memory.current_arc_index + 1
            current_chapter = memory.chapters_completed + 1
            total_chapters = memory.chapters_per_arc
            
            # Calculate overall story progress
            total_story_chapters = total_arcs * total_chapters
            current_story_chapter = ((memory.current_arc_index) * total_chapters) + current_chapter
            story_progress_percent = round((current_story_chapter / total_story_chapters) * 100)
            
            # Create arc progress format for pacing
            arc_progress = f"{current_chapter}/{total_chapters}"
            
            arc_progression = f"""
## Story Arc Structure & Progression
This is a multi-arc story with a total of {total_arcs} story arcs, all working toward the ultimate goal: **{big_story_goal}**.

{ARC_PACING_TEMPLATE.format(
    arc_progress=arc_progress,
    current_arc_goal=current_arc_goal,
    current_chapter=current_chapter,
    chapters_per_arc=total_chapters
)}

**Overall Story Progress:** Chapter {current_story_chapter} of {total_story_chapters} ({story_progress_percent}% complete)
"""

            # Add transition guidance for specific arc positions
            if current_chapter == 1:
                # First chapter of arc (except first arc)
                if current_arc_num > 1:
                    previous_arc = memory.arcs[memory.current_arc_index - 1]
                    arc_progression += f"""
### Arc Transition Guidance:
- This is the FIRST CHAPTER of a NEW ARC.
- Previous arc ("{previous_arc}") has been completed.
- Now focus on establishing the beginning of the new arc goal: "{current_arc_goal}"
- Show how this arc builds upon achievements/lessons from the previous arc.
- Introduce new challenges, settings, or characters related to this new arc.
"""
            elif current_chapter == total_chapters:
                # Final chapter of current arc
                arc_progression += f"""
### Arc Transition Guidance:
- This is the FINAL CHAPTER of the current arc.
- You must resolve the current arc goal: "{current_arc_goal}" in a satisfying way.
- Show meaningful achievement/growth/resolution related to this arc goal.
"""
                # If not the final arc, provide transition setup
                if current_arc_num < total_arcs:
                    next_arc = memory.arcs[memory.current_arc_index + 1]
                    arc_progression += f"""
- Begin setting up/foreshadowing the next arc: "{next_arc}"
- End with choices that can lead toward this upcoming challenge.
"""
            elif current_chapter == total_chapters - 1:
                # Penultimate chapter - begin setting up conclusion
                arc_progression += f"""
### Arc Progression Guidance:
- This is the SECOND-TO-LAST CHAPTER of the current arc.
- Begin moving toward the conclusion of the current arc goal: "{current_arc_goal}"
- Create rising action or a significant challenge that will lead to the arc's climax.
- Choices should set up the final chapter of this arc.
"""
            else:
                # Middle chapter - continue developing arc
                arc_progression += f"""
### Arc Progression Guidance:
- This is a MIDDLE CHAPTER of the current arc.
- Continue developing progress toward the arc goal: "{current_arc_goal}"
- Deepen complications, character development, or challenges related to this arc.
"""

        # Add current arc goal if available in memory
        arc_goal_prompt = ""
        if memory and hasattr(memory, 'arcs') and memory.arcs and len(memory.arcs) > memory.current_arc_index:
            current_arc_goal = memory.arcs[memory.current_arc_index]
            arc_goal_prompt = f"\n\nCURRENT ARC GOAL:\n- {current_arc_goal}"
            
            # Add progress info if available
            if hasattr(memory, 'chapters_completed') and hasattr(memory, 'chapters_per_arc'):
                arc_goal_prompt += f" (Chapter {memory.chapters_completed + 1} of {memory.chapters_per_arc})"
                
            # If this is the final chapter of the arc, mention it
            if memory.chapters_completed == memory.chapters_per_arc - 1:
                arc_goal_prompt += "\nThis is the FINAL CHAPTER of the current arc. Conclude this arc goal in a satisfying way."

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
                
        # Build the system prompt using shared templates
        clarity_rules = CLARITY_RULES_TEMPLATE.format(character_name=character_name)
        
        # Add continuation-specific origin integration to clarity rules
        origin_integration = f"""
5. **Origin Integration**:
   - If there are unique aspects to {character_name}'s background, they must be actively reflected and demonstrated through {character_name}'s actions and dialogue.
"""
        clarity_rules += origin_integration
        
    
        
        # Format story objectives with the current arc goal
        arc_goal_reference = current_arc_goal if current_arc_goal else "current arc goal"
        story_objectives = STORY_OBJECTIVES_TEMPLATE.format(
            character_name=character_name,
            style=style,
            arc_goal_text=arc_goal_reference,
            big_goal_prompt=big_goal_prompt
        )   
        
        # Format choice guidance for continuation
        choice_guidance = CHOICE_GUIDANCE_TEMPLATE.format(
            character_name=character_name,
            style=style
        )

        # Add creative enhancements for continuation
        creative_enhancements = """
---

### 📚 Creative Enhancements (To ensure freshness and unpredictability):

- Vary conflict types significantly (environmental disasters, internal character struggles, new mentor lessons, unexpected ally arrivals, ancient secrets, new test or tornoment) while staying true to the overall tone and typical scenarios of the {style} genre.".
- Introduce unexpected twists or revelations occasionally (hidden identities, secret missions, lost techniques) that serve the current arc's progression
- Characters should have clear personal motivations and unique speech patterns or habits.
- Avoid repetitive trope usage (same rival encounter repeatedly, identical training sequences).
- Leverage sensory details (sound, sight, touch) to vividly engage readers visually and emotionally.

---

## Global Prohibitions & Anti-Patterns

🚫 **STRICTLY FORBIDDEN (Do NOT do this):**
- Unexplained scene transitions or location changes.
- Vague rewards or unclear outcomes after cultivation challenges.
- Repetitive cryptic dialogue without explicit clarity or meaningful context.
- Actions or outcomes that confuse readers about what exactly happened.
- Including choice prompts or choice options within the [STORY] section. 
- All three choices must be narrowly focused on the immediate scene (e.g. only three fight variations). At least one must shift the method or context of arc progression.
"""

        # Add the forbidden completion rules
        if big_story_goal:
            creative_enhancements += FORBIDDEN_COMPLETION_TEMPLATE.format(big_story_goal=big_story_goal)

        creative_enhancements += """
---

### 🚫 STRICTLY AVOID (To ensure creative storytelling):

- Predictable panel sequences or repetitive scenario setups.
- Overused clichés ("Rival shows up, mocks hero").
- Vague or abstract storytelling ("mysterious power" without specifics).
- Sudden unexplained character or event introductions.
- Introducing a new overarching story problem or concluding a major arc within a single chapter.
- Making choices look like they are the continuation of the story
- Including any "Panel X:" or numbered panel labels - ONLY use '---' on a new line to separate panels.
"""
        
        # Choice guidance with current arc reference
        arc_reference = current_arc_goal if current_arc_goal else "current arc"
        initial_choice_guidance = f"""
### 🔑 MANDATORY RULES FOR CHOICE GENERATION:
At the conclusion of this chapter, clearly present exactly three visually distinctive and engaging manga/manhwa-style choices naturally arising directly from the current scenario and context. These choices should move {character_name} forward within the current arc (working towards {arc_reference}).
"""
        
        choice_guidance = initial_choice_guidance + CHOICE_GUIDANCE_TEMPLATE.format(
            character_name=character_name,
            style=style
        )
        
        # Add specific continuation chapter requirements
        choice_guidance += """
- Each choice has to be inside of the [CHOICES] section.
"""
        
        # Format template specifying this is a continuation chapter
        format_section = FORMAT_TEMPLATE.format(
            story_type="continuation chapter"
        )

        # Assemble the full system prompt
        system_prompt = f"""You're an expert manga/manhwa creator continuing a dynamic cultivation story.

Use {pronouns} pronouns for {character_name}.
**Story Style/Genre:** {style} - Ensure every aspect of the chapter (plot, character interactions, conflict, mood) aligns perfectly with this genre.
{origin_prompt} {big_goal_prompt}

{arc_progression}

You will create the next compelling chapter (4–8 panels) that builds meaningfully from the previous choice. Organize panels for maximum visual impact and emotional engagement. Use '---' on a new line to separate panels, but DO NOT include any "Panel X:" labels or numbering.

{clarity_rules}

{story_objectives}

{creative_enhancements}

{choice_guidance}

{emotional_flaw_prompt}

{PANEL_STRUCTURE_TEMPLATE}

{INTROSPECTION_RULE}

{DIALOGUE_RULE}

{format_section}"""

        user_prompt = f"""Continue {character_name}'s cultivation progression story:

PREVIOUS STORY:
{previous_content}

CHOSEN ACTION:
{selected_choice}

{arc_goal_prompt}

Now, show the immediate consequences and progression that naturally follows from this choice with:
- Clear cause-and-effect relationship to the chosen action
- Specific cultivation techniques with vivid qi descriptions
- Character development and emotional reactions
- Fresh conflict or challenge
- Natural dialogue that reveals character
"""

        user_prompt += """

Remember: You have complete creative freedom in panel sequence and pacing. Focus on visual storytelling that would make readers eager for the next chapter. Use '---' on a new line to separate panels, but DO NOT include any 'Panel X:' labels or numbering.

After your story but before the choices, please identify any NEW characters you introduced in THIS chapter. Format them like this:

[NEW CHARACTERS]
Name: [Character's actual name]
Relationship: [Their relationship to the protagonist - Friend, Rival, Mentor, etc.]
Sect: [Their sect or organization if applicable]
Role: [Their role or position if applicable]

// Add additional characters with the same format if there are multiple
[/NEW CHARACTERS]

If no new characters were introduced in this chapter, simply omit this section.
"""

        # Generate content
        logger.info(f"Continuing cultivation progression story for {character_name} with style: {style}")
        story_content, choices = BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
        
        # Clean up any panel or scene numbering/labels that might still appear
        story_content = self._clean_panel_labels(story_content)
        
        # Extract characters from the generated content if memory is available
        if memory:
            memory = self.extract_characters_from_content(
                memory=memory,
                story_content=story_content,
                character_name=character_name
            )
        
        return story_content, choices

    def add_character_to_memory(self, memory: Any, name: str, relationship: str, sect: Optional[str] = None, role: Optional[str] = None) -> Any:
        """
        Add or update a character in the story memory.
        
        Args:
            memory: The StoryMemory object to update
            name: The character's name
            relationship: The character's relationship to the protagonist
            sect: The character's sect or organization (optional)
            role: The character's role or position (optional)
            
        Returns:
            The updated StoryMemory object
            
        Validation:
            - Rejects empty or very short names (< 2 chars)
            - Rejects names with non-alphabetic characters
            - Updates existing characters rather than creating duplicates
        """
        # Validate inputs
        if not name or not isinstance(name, str) or len(name) < 2:
            logger.warning(f"Invalid character name: '{name}' - too short or empty")
            return memory
        
        # Check if name contains mostly alphabetic characters (allow spaces)
        if not re.match(r'^[A-Za-z\s]+$', name) or name.isspace():
            logger.warning(f"Invalid character name: '{name}' - contains invalid characters")
            return memory
        
        # Common names that might be used incorrectly
        common_words = ["The", "And", "But", "This", "That", "Where", "When", "Who", "What", "Why", "How"]
        if name in common_words:
            logger.warning(f"Rejected common word as character name: '{name}'")
            return memory
        
        # Validate relationship
        if not relationship or not isinstance(relationship, str) or len(relationship) < 2:
            logger.warning(f"Invalid relationship: '{relationship}' - too short or empty")
            return memory
        
        # Validate sect if provided
        if sect is not None and (not isinstance(sect, str) or len(sect) < 2):
            logger.warning(f"Invalid sect: '{sect}' - too short or empty")
            sect = None
        
        # Validate role if provided
        if role is not None and (not isinstance(role, str) or len(role) < 2):
            logger.warning(f"Invalid role: '{role}' - too short or empty")
            role = None
        
        # Initialize characters list if needed
        if not hasattr(memory, 'characters') or memory.characters is None:
            # Import here to avoid circular imports
            from ..models.models import Character
            memory.characters = []
        
        # Import Character class
        from ..models.models import Character
        
        # Avoid duplicates — check if character already exists
        existing_char = None
        for i, character in enumerate(memory.characters):
            if character.name == name:
                existing_char = character
                # Remove from list to replace with updated version
                memory.characters.pop(i)
                break
        
        # If character exists, update with new info
        if existing_char:
            logger.info(f"Updating character: {name}")
            
            # Only update fields if new values are provided
            if relationship:
                existing_char.relationship = relationship
            if sect:
                existing_char.sect = sect
            if role:
                existing_char.role = role
            
            # Add updated character back to list
            memory.characters.append(existing_char)
        else:
            # Create and add new character
            logger.info(f"Adding new character: {name} ({relationship})")
            new_char = Character(
                name=name,
                relationship=relationship,
                sect=sect,
                role=role
            )
            memory.characters.append(new_char)
        
        return memory

    def extract_characters_from_content(self, memory, story_content: str, character_name: str):
        """
        Extract characters from story content and add them to memory.
        Overrides the base class method to use the story_planner's extract_characters_from_content function.
        
        Args:
            memory: The StoryMemory object to update
            story_content: The story content to extract characters from
            character_name: The protagonist's name to avoid adding them
            
        Returns:
            The updated memory object
        """
        try:
            from ..services.story_planner import extract_characters_from_content as planner_extract_characters
            memory = planner_extract_characters(
                memory=memory,
                story_content=story_content,
                protagonist_name=character_name
            )
            logger.info(f"Extracted characters from story content for {character_name}")
            return memory
        except Exception as e:
            logger.error(f"Error extracting characters from content: {e}")
            return memory
