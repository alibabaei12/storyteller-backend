"""
Cultivation Progression genre implementation for manga-style progression stories.
"""
from typing import List, Tuple
import openai
import logging
from ..models import Choice
from ..base_genre import BaseGenre, Genre

# Set up logger
logger = logging.getLogger(__name__)


class CultivationProgression(Genre):
    """Cultivation progression story generator with manga-style weak-to-strong progression."""
    
    @property
    def genre_name(self) -> str:
        return "Cultivation Progression"
    
    @property 
    def genre_context(self) -> str:
        return "cultivation progression world"
    
    def generate_story(
        self,
        character_name: str,
        character_gender: str,
        language_complexity: str,
        character_origin: str = "normal"
    ) -> Tuple[str, List[Choice]]:
        """
        Generate a manga-style cultivation progression story.
        
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
            
            # Import the origin profile method
            from app.ai_service import AIService
            
            # Create character origin profile with cultivation-specific context
            origin_prompt = AIService._create_character_origin_profile(character_origin, "cultivation")
            
            # Dynamic Storytelling Approach - Goals-Based Generation
            system_prompt = f"""You are creating an engaging cultivation manga/manhwa opening scene. Focus on creative storytelling with dynamic visual flow rather than rigid structure.

🎌 MANGA/MANHWA STORYTELLING APPROACH:
- Create 4-7 visually sequential panels (your creative choice)
- Each panel flows naturally to tell a compelling story
- Use manga/manhwa pacing: dynamic, visual, emotionally engaging
- Concise dialogue under 15 words per speech bubble
- Clear visual context and logical panel progression

CHARACTER ORIGIN INTEGRATION:
{origin_prompt}

🎯 MANDATORY STORYTELLING GOALS FOR THIS SCENE:
1. Visually introduce {character_name}, establishing personality through dynamic action
2. Clearly show {character_name}'s immediate cultivation goal or aspiration  
3. Present compelling initial conflict, challenge, or intriguing event demanding action
4. Introduce at least one supporting character (rival, master, fellow disciple) naturally
5. Showcase at least one visually distinctive, clearly named cultivation technique
6. End with intriguing cliffhanger or visually clear suspense that prompts curiosity

🔥 CULTIVATION WORLD REQUIREMENTS:
- CREATIVE SECT NAMES: "Thousand Stars Sect", "Iron Will Academy", "Shifting Sands Order"
- SPECIFIC TECHNIQUES: "Shattered Earth Palm", "Whisper Step", "Molten Forge Breathing"  
- CLEAR STAGES: Qi Gathering 1-9 → Foundation Building → Core Formation
- VISUAL QI: Specific colors (crimson spirals, violet mist, silver threads) with unique effects
- SECT HIERARCHY: Outer → Inner → Core Disciple → Elder shown naturally
- CHARACTER MOTIVATIONS: Fresh, specific goals beyond generic "get stronger"

✅ CREATIVE STORYTELLING RULES:
- YOU decide optimal number of panels (4-7) for best story flow
- Each panel adds meaningful story progression, avoiding redundancy
- Dialogue reveals distinct character personalities and motivations
- Visual descriptions help readers imagine manga panels clearly
- Logical continuity between panels with creative surprises

❌ STRICTLY AVOID:
- Predictable storytelling clichés (generic rival encounters, basic training scenes)
- Abstract descriptions ("mysterious power" without specifics)
- Generic sect names (Azure/Jade/Golden/Cloud/Sky/Heaven)
- Forced panel structures that limit creativity
- Dead parents motivation (overused trope)

{gender_prompt}
{language_prompt}

🚀 CREATIVE FREEDOM:
Let your storytelling instincts guide the scene structure. Create panels that flow naturally and build engaging narrative tension. Surprise both yourself and the reader with creative developments that feel authentic to cultivation manga/manhwa."""

            # User prompt for dynamic cultivation scene generation
            user_prompt = f"""Create an engaging cultivation manga/manhwa opening scene featuring {character_name} with {character_origin} origin.

🎯 YOUR CREATIVE MISSION:
Create a compelling opening scene that accomplishes these storytelling goals through 4-7 dynamic panels (you choose the optimal number for best narrative flow):

📚 MANDATORY STORYTELLING GOALS:
1. **Character Introduction**: Visually introduce {character_name}, establishing their personality through a dynamic cultivation action or moment
2. **Cultivation Aspiration**: Clearly show {character_name}'s immediate cultivation goal, challenge, or what they're striving for
3. **Compelling Conflict**: Present an intriguing conflict, challenge, or event that demands immediate attention or curiosity
4. **Supporting Character**: Introduce at least one other character naturally (rival, master, fellow disciple, sect member)
5. **Technique Showcase**: Demonstrate at least one clearly named, visually distinctive cultivation technique with specific qi effects
6. **Suspenseful Ending**: End with a cliffhanger, mystery, or visually clear tension that makes readers eager for more

🌟 CULTIVATION WORLD ELEMENTS TO WEAVE IN:
- **Creative Sect**: Use imaginative sect name (avoid Azure/Jade/Golden - try "Thousand Stars Sect", "Shifting Sands Order")
- **Specific Techniques**: Named techniques like "Ember Palm", "Whisper Step", "Iron Will Breathing"
- **Clear Progression**: Show {character_name}'s current stage (Qi Gathering 3, Foundation Building 1, etc.)
- **Visual Qi**: Specific colors and effects (crimson spirals, violet mist, silver threads)
- **Sect Hierarchy**: Natural inclusion of ranks (Outer/Inner/Core Disciple, Elder)
- **Fresh Motivation**: Give {character_name} a specific, compelling reason for cultivation beyond generic "get stronger"

🎨 CREATIVE STORYTELLING APPROACH:
- **Panel Flow**: Create 4-7 panels that flow naturally like a real manga chapter
- **Visual Clarity**: Each panel should be imaginable as a clear manga panel with specific character positioning
- **Dialogue Style**: Concise speech bubbles under 15 words that reveal character personality
- **Pacing**: Build narrative tension naturally, avoiding predictable formulaic progression
- **Surprises**: Include creative elements that feel fresh and unexpected while staying true to cultivation genre

❌ AVOID THESE CLICHÉS:
- Generic rival encounters that feel forced
- Predictable "mysterious master appears" scenarios  
- Basic training montages without personality
- Abstract cultivation descriptions without specifics
- Overly familiar sect politics without fresh angles

🚨 FLEXIBLE RESPONSE FORMAT:
[STORY]
Panel 1:
(Your creative scene opening)

Panel 2:
(Continue the story flow naturally)

[Continue with as many panels as needed for optimal storytelling - 4 to 7 total]

Final Panel:
(End with compelling setup for choices)
[/STORY]

[CHOICES]
1. (Aggressive choice naturally arising from your scene - minimum 12 words with specific details)
2. (Strategic choice based on the situation you created - minimum 12 words with specific details)
3. (Risky/mysterious choice offering uncertain outcomes - minimum 12 words with specific details)
[/CHOICES]

🚀 CREATIVE FREEDOM: 
Let your storytelling instincts guide you! Create a scene that feels authentic, engaging, and makes readers excited to see what happens next. Surprise us with creative cultivation scenarios while maintaining manga/manhwa storytelling quality."""

            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error generating cultivation progression story: {e}")
            # Fallback for cultivation progression
        except Exception as e:
            logger.error(f"Unexpected error generating cultivation progression story: {e}")
            # Fallback for cultivation progression
            return BaseGenre.create_fallback_story(
                character_name,
                f"{character_name} stood at the bottom of the Outer Disciple rankings, mocked by all for having weak spiritual roots. "
                f"Determined to prove their worth and honor their family's memory, {character_name} faced a crucial decision about their cultivation path. "
                f"The upcoming sect trials offered a chance to advance, but other paths beckoned as well...",
                [
                    Choice(id="1", text="Train harder to improve cultivation base"),
                    Choice(id="2", text="Seek help from a senior disciple"),
                    Choice(id="3", text="Challenge a rival to prove worthiness")
                ]
            )

    def continue_story(
        self,
        character_name: str,
        character_gender: str,
        previous_content: str,
        selected_choice: str,
        language_complexity: str,
        character_origin: str = None
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
            
            system_prompt = f"""You are continuing a cultivation manga/manhwa story with dynamic storytelling that builds meaningfully from the previous scene. Focus on creative narrative flow while maintaining character consistency.

🎌 DYNAMIC CONTINUATION APPROACH:
- Create 4-7 panels (your choice) that naturally continue the story
- Build logically from the previous choice while adding creative story development
- Maintain character personalities and established world elements
- Use manga/manhwa pacing: visual, engaging, emotionally compelling

📋 NARRATIVE COHESION REQUIREMENTS:
- First panel MUST show logical consequence of the previous choice
- Reference previous events naturally within the story flow
- Character actions and dialogue must match established personalities
- Each panel should add meaningful story progression

🗣️ CHARACTER-DRIVEN STORYTELLING:
- Dialogue under 15 words that reveals distinct character personalities
- {character_name} speaks/thinks in a way that reflects their {character_origin} background
- Supporting characters have consistent, memorable speech patterns
- Avoid generic dialogue - make each character voice unique

🎯 CREATIVE CONTINUATION GOALS:
1. **Choice Consequence**: Show immediate, logical result of the previous choice
2. **Character Development**: Advance {character_name}'s cultivation journey meaningfully  
3. **Story Progression**: Add one significant plot development or revelation
4. **Relationship Dynamics**: Develop relationships with supporting characters naturally
5. **Technique Advancement**: Showcase cultivation progress through named techniques
6. **Engaging Cliffhanger**: End with compelling setup for next meaningful decision

🔥 CULTIVATION STORY ELEMENTS:
- Clear cultivation advancement (technique mastery, stage progression, qi improvement)
- Visual qi effects with specific colors and patterns (crimson spirals, violet mist, silver threads)
- Sect hierarchy and politics shown naturally in story flow
- Character motivations that feel authentic and specific to their background

🚀 CREATIVE STORYTELLING APPROACH:
- Choose optimal number of panels (4-7) for best narrative flow
- Each panel adds meaningful story value, avoiding predictable filler
- Surprise elements that feel natural and enhance the cultivation journey
- Visual descriptions that help readers imagine clear manga panels

✅ STORYTELLING QUALITY STANDARDS:
- Logical progression from previous choice to new story developments
- Character dialogue that reveals personality and advances relationships
- Named cultivation techniques with specific visual qi effects
- Sect world-building woven naturally into the narrative flow

🚫 AVOID CREATIVE LIMITATIONS:
- Predictable story formulas that feel mechanical or paint-by-numbers
- Random character appearances without logical narrative setup
- Generic cultivation scenarios without fresh angles or creativity
- Forced conflicts that don't arise naturally from established story flow

{gender_prompt}
{language_prompt}"""

            user_prompt = f"""Continue this cultivation manga/manhwa story with creative storytelling that builds meaningfully from the player's choice.

📖 PREVIOUS SCENE:
{previous_content}

⚡ PLAYER'S CHOSEN ACTION:
{selected_choice}

🎯 YOUR CREATIVE CONTINUATION MISSION:
Create a compelling continuation scene (4-7 panels of your choice) that accomplishes these storytelling goals:

📚 MANDATORY STORYTELLING GOALS:
1. **Choice Consequence**: Show the immediate, logical result of the chosen action: "{selected_choice}"
2. **Character Growth**: Demonstrate {character_name}'s cultivation advancement or personal development
3. **Story Advancement**: Add meaningful plot progression that builds from established elements
4. **Character Interaction**: Develop relationships with supporting characters authentically
5. **Technique Showcase**: Feature at least one named cultivation technique with visual qi effects
6. **Compelling Setup**: End with an engaging situation that leads to meaningful player choices

🌟 NARRATIVE COHERENCE REQUIREMENTS:
- First panel must logically show the consequence of the specific choice made
- All character actions must match established personalities and motivations
- New developments must feel like natural story progression, not random events
- Reference previous scene elements appropriately within the story flow

🎨 CREATIVE STORYTELLING APPROACH:
- Choose the optimal number of panels (4-7) for best narrative flow
- Each panel should add meaningful value to the story progression
- Include creative elements that surprise while staying true to cultivation genre
- Visual descriptions should help readers imagine clear manga panels

🔥 CULTIVATION ELEMENTS TO INCLUDE:
- Named cultivation techniques with specific visual qi effects
- Clear indication of {character_name}'s current cultivation stage/progress
- Sect hierarchy, politics, or relationships shown naturally
- Creative sect elements that avoid generic Azure/Jade/Golden names

🗣️ DIALOGUE REQUIREMENTS:
- Each character has distinct speech patterns
- {character_name}: Reflects {character_origin} background in word choice
- Rivals: Confident, challenging, competitive language
- Masters: Wise but concise, technique-focused speech
- Fellow disciples: Casual, worried, or encouraging based on relationship

🚫 STRICTLY FORBIDDEN (Do NOT do these):
- Introducing random, unexplained enemies or sudden antagonists
- Actions or attacks that don't logically match previous panel outcomes  
- Characters suddenly changing personality or allegiance without clear explanation
- Generic or vague choices ("specific to your panels")
- New characters appearing without logical introduction
- Events that contradict established story elements
- Hana or other rivals suddenly becoming hostile without narrative justification

🧩 NARRATIVE COHESION (MANDATORY):
- Every panel must clearly follow the logical progression of the previous panel and chapter
- Explicit continuity required—no sudden unexplained narrative jumps
- All character motivations must be clear and consistent with previous chapters
- If characters change behavior, explicitly show why in the narrative

❌ AVOID PREDICTABLE PATTERNS:
- Forced panel structures that limit creative storytelling
- Generic cultivation scenarios without fresh angles
- Random character personality changes without explanation
- Mechanical story progression that feels paint-by-numbers

🚨 FLEXIBLE RESPONSE FORMAT:
[STORY]
Panel 1:
(Show consequence of "{selected_choice}")

Panel 2:
(Continue story flow naturally)

[Continue with optimal number of panels for your story - 4 to 7 total]

Final Panel:
(End with compelling setup for meaningful choices)
[/STORY]

[CHOICES]
1. (AGGRESSIVE choice arising naturally from your scene - minimum 12 words with specific details)
2. (STRATEGIC choice based on the situation you created - minimum 12 words with specific details)
3. (RISKY choice offering uncertain outcomes specific to your story - minimum 12 words with specific details)
[/CHOICES]

🚀 CREATIVE FREEDOM:
Let your storytelling instincts guide the continuation! Build meaningfully from the previous choice while adding creative cultivation elements that make readers excited for the next development."""

            # Generate content with retry logic
            return BaseGenre.generate_story_with_retry(system_prompt, user_prompt, character_name)
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error continuing cultivation progression story: {e}")
            # Contextual fallback based on the selected choice
        except Exception as e:
            logger.error(f"Unexpected error continuing cultivation progression story: {e}")
            # Contextual fallback based on the selected choice
            return BaseGenre.create_contextual_fallback(
                character_name, selected_choice, self.genre_context
            ) 