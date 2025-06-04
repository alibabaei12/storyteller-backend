from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from uuid import uuid4

from .models import Story, StoryNode, Choice, StoryCreationParams, StoryMetadata
from .storage import (
    save_story, 
    get_story, 
    delete_story, 
    get_all_stories, 
    add_story_node, 
    save_choice, 
    create_story
)
from .ai_service import AIService

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route('/api/status', methods=['GET'])
def get_status():
    """API endpoint to check if the server is running."""
    return jsonify({
        'status': 'ok',
        'message': 'StoryTeller API is running'
    })

@app.route('/api/stories', methods=['GET'])
def get_stories():
    """API endpoint to get all stories."""
    stories = get_all_stories()
    return jsonify([story.model_dump() for story in stories])

@app.route('/api/stories/<story_id>', methods=['GET'])
def get_story_by_id(story_id):
    """API endpoint to get a specific story."""
    story = get_story(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404
    
    return jsonify(story.model_dump())

@app.route('/api/stories/<story_id>', methods=['DELETE'])
def delete_story_by_id(story_id):
    """API endpoint to delete a story."""
    success = delete_story(story_id)
    if not success:
        return jsonify({'error': 'Failed to delete story'}), 500
    
    return jsonify({'success': True})

@app.route('/api/stories', methods=['POST'])
def create_new_story():
    """API endpoint to create a new story."""
    try:
        data = request.json
        
        params = StoryCreationParams(
            character_name=data.get('character_name', ''),
            setting=data.get('setting', 'cultivation'),
            tone=data.get('tone', 'adventure'),
            character_origin=data.get('character_origin', 'normal'),
            power_system=data.get('power_system', 'qi')
        )
        
        # Generate initial story content
        story_content, choices = AIService.generate_initial_story(
            character_name=params.character_name,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
            power_system=params.power_system
        )
        
        # Create initial node
        initial_node = StoryNode(
            id="initial",
            content=story_content,
            choices=choices,
            parent_node_id=None
        )
        
        # Create the story
        story = create_story(params, initial_node)
        
        return jsonify(story.model_dump())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stories/<story_id>/choices/<choice_id>', methods=['POST'])
def make_choice(story_id, choice_id):
    """API endpoint to make a choice in a story."""
    try:
        story = get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Get the current node
        current_node = story.nodes.get(story.current_node_id)
        if not current_node:
            return jsonify({'error': 'Current node not found'}), 500
        
        # Find the choice
        selected_choice = None
        for choice in current_node.choices:
            if choice.id == choice_id:
                selected_choice = choice
                break
        
        if not selected_choice:
            return jsonify({'error': 'Choice not found'}), 404
        
        # Save the choice
        save_choice(story_id, current_node.id, choice_id)
        
        # Generate continuation
        story_content, choices = AIService.continue_story(
            character_name=story.character_name,
            setting=story.setting,
            tone=story.tone,
            previous_content=current_node.content,
            selected_choice=selected_choice.text
        )
        
        # Create new node
        new_node_id = f"node_{int(uuid4().hex[:8], 16)}"
        new_node = StoryNode(
            id=new_node_id,
            content=story_content,
            choices=choices,
            parent_node_id=current_node.id,
            selected_choice_id=choice_id
        )
        
        # Add the node to the story
        updated_story = add_story_node(story_id, new_node)
        
        if not updated_story:
            return jsonify({'error': 'Failed to update story'}), 500
        
        return jsonify(updated_story.model_dump())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_api(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api(debug=True) 