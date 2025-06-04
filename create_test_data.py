#!/usr/bin/env python3
"""
Create test data for the StoryTeller application.
This script generates a few test stories for development and testing.
"""

import sys
import os
import time
from app.models import Story, StoryNode, Choice, StoryCreationParams
from app.storage import create_story, add_story_node, save_story

def create_test_data():
    print("Creating test data...")
    
    # Ensure we have a clean slate
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create test stories
    create_cultivation_story()
    create_academy_story()
    create_apocalypse_story()
    
    print("Test data created successfully.")

def create_cultivation_story():
    """Create a test cultivation story."""
    # Create initial parameters
    params = StoryCreationParams(
        character_name="Li Wei",
        setting="cultivation",
        tone="adventure",
        character_origin="hidden",
        power_system="qi"
    )
    
    # Create initial node with content and choices
    initial_node = StoryNode(
        id="initial",
        content=(
            "You, Li Wei, have lived a simple life in Verdant Valley Village, unaware of your hidden potential. "
            "For generations, your family has been known for their medicinal herb shop, but no one has ever shown "
            "talent for cultivation.\n\n"
            "Today, as you were gathering herbs in the mountains, you felt a strange resonance within a hidden cave. "
            "Inside, you discovered an ancient jade medallion that seemed to pulse with energy when you touched it. "
            "Suddenly, you feel channels opening within your body, and a surge of Qi flows through you for the first time.\n\n"
            "As you exit the cave, the world looks different - you can see swirls of energy in plants, animals, and even the air itself."
        ),
        choices=[
            Choice(id="1", text="Return to the village to tell your family about your discovery"),
            Choice(id="2", text="Explore the cave further to see if there are more treasures"),
            Choice(id="3", text="Attempt to circulate the new Qi energy according to instincts you never knew you had")
        ],
        timestamp=time.time() - 86400  # 1 day ago
    )
    
    # Create the story
    story = create_story(params, initial_node)
    
    # Add a second node (as if the user chose option 3)
    second_node = StoryNode(
        id="node_12345678",
        content=(
            "Following an instinct that feels ancient yet familiar, you sit cross-legged at the mouth of the cave. "
            "The jade medallion grows warm against your chest as you close your eyes and focus on the energy flowing "
            "through your body.\n\n"
            "You visualize the Qi as a golden stream, directing it through pathways that seem to reveal themselves "
            "to your mind's eye. The sensation is both exhilarating and peaceful. Hours pass like minutes as you "
            "enter a meditative state deeper than you've ever experienced.\n\n"
            "When you finally open your eyes, the sun has begun to set, casting long shadows across the mountain. "
            "You feel stronger, more aware, and somehow connected to the natural world around you. The first step "
            "on your cultivation path has been taken.\n\n"
            "As you prepare to return to the village, you notice a weathered stone tablet partially hidden by vegetation "
            "near the cave entrance. It bears ancient inscriptions that, surprisingly, you can now understand."
        ),
        choices=[
            Choice(id="1", text="Read the stone tablet to learn its secrets"),
            Choice(id="2", text="Return to the village before your family becomes worried"),
            Choice(id="3", text="Take the stone tablet with you to study it properly at home")
        ],
        parent_node_id="initial",
        selected_choice_id="3",
        timestamp=time.time() - 43200  # 12 hours ago
    )
    
    # Add the node to the story
    story = add_story_node(story.id, second_node)
    
    # Update the story title and cultivation stage
    story.title = "Li Wei's Cultivation Journey"
    story.cultivation_stage = "Qi Condensation Stage (Level 1)"
    save_story(story)
    
    print(f"Created cultivation story: {story.id}")

def create_academy_story():
    """Create a test magic academy story."""
    # Create initial parameters
    params = StoryCreationParams(
        character_name="Elena Frost",
        setting="academy",
        tone="comedy",
        character_origin="normal",
        power_system="magic"
    )
    
    # Create initial node with content and choices
    initial_node = StoryNode(
        id="initial",
        content=(
            "You, Elena Frost, stand nervously at the gates of Silverleaf Academy, clutching your acceptance letter. "
            "You still can't believe that you, a perfectly ordinary person from a small town, have been accepted into "
            "the most prestigious magical academy in the kingdom.\n\n"
            "The massive iron gates swing open silently, revealing a sprawling campus with towers that seem to defy "
            "gravity and gardens blooming with plants you've never seen before. Students in blue and silver robes hurry "
            "across courtyards, some with books floating behind them, others with familiars at their heels.\n\n"
            "\"First year, are you?\" asks a cheerful voice. You turn to see a red-haired girl with freckles and a crooked smile. "
            "\"I'm Penelope. Welcome to the madhouse! Don't worry, only about 10% of students get turned into toads permanently.\""
        ),
        choices=[
            Choice(id="1", text="Ask Penelope to show you around the academy"),
            Choice(id="2", text="Head straight to the administration office to get your schedule"),
            Choice(id="3", text="Ask Penelope if she's joking about the toads")
        ],
        timestamp=time.time() - 172800  # 2 days ago
    )
    
    # Create the story
    story = create_story(params, initial_node)
    
    print(f"Created academy story: {story.id}")

def create_apocalypse_story():
    """Create a test apocalypse story."""
    # Create initial parameters
    params = StoryCreationParams(
        character_name="Marcus Chen",
        setting="apocalypse",
        tone="serious",
        character_origin="normal",
        power_system="levels"
    )
    
    # Create initial node with content and choices
    initial_node = StoryNode(
        id="initial",
        content=(
            "You, Marcus Chen, wake up to the sound of emergency alerts blaring from your phone. Half-asleep, you "
            "check the notification: \"EMERGENCY ALERT: UNKNOWN PHENOMENON. STAY INDOORS. THIS IS NOT A DRILL.\"\n\n"
            "As you stumble to the window of your apartment, your drowsiness instantly vanishes. The sky has turned "
            "a sickly green, with swirling patterns like an aurora. Down on the streets, people are running in panic "
            "or staring upward in disbelief.\n\n"
            "Suddenly, translucent blue rectangles appear in your vision. You blink and rub your eyes, but they remain:"
            "\n\n[System Notification: The Apocalypse Protocol has initiated. You have been selected as a Survivor. "
            "Current Level: 1. Skills: None. Objectives: Survive the first wave.]\n\n"
            "Before you can process this bizarre hallucination, a deep rumbling shakes the building. Something is coming."
        ),
        choices=[
            Choice(id="1", text="Grab essential supplies and try to escape the city"),
            Choice(id="2", text="Barricade yourself in your apartment"),
            Choice(id="3", text="Try to reach your family across town")
        ],
        timestamp=time.time() - 259200  # 3 days ago
    )
    
    # Create the story
    story = create_story(params, initial_node)
    
    print(f"Created apocalypse story: {story.id}")

if __name__ == "__main__":
    create_test_data() 