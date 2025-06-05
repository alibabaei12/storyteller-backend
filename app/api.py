from flask import Flask, request, jsonify, redirect, g, make_response
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
    create_story,
    get_user_stories
)
from .ai_service import AIService
from .usage_service import usage_service
from .auth import auth_required, auth_optional

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes with explicit origins
CORS(app, 
    resources={r"/*": {"origins": ["http://localhost:3000", "https://storyteller-frontend-1.onrender.com"]}}, 
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-ID", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
    expose_headers=["Authorization"]
)

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:3000", "https://storyteller-frontend-1.onrender.com"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:3000", "https://storyteller-frontend-1.onrender.com"]:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# Usage service is imported as a singleton

# Root status endpoint (for frontend without /api prefix)
@app.route('/status', methods=['GET', 'OPTIONS'])
def root_status():
    """Root status endpoint for compatibility."""
    return jsonify({
        'status': 'ok',
        'message': 'StoryTeller API is running'
    })

# Routes without /api prefix for compatibility
@app.route('/stories', methods=['GET', 'OPTIONS'])
@auth_optional
def root_get_stories():
    """Get all stories (without /api prefix)."""
    return get_stories()

@app.route('/stories/<story_id>', methods=['GET', 'OPTIONS'])
@auth_optional
def root_get_story(story_id):
    """Get a specific story (without /api prefix)."""
    return get_story_by_id(story_id)

@app.route('/stories', methods=['POST', 'OPTIONS'])
@auth_required
def root_create_story():
    """Create a new story (without /api prefix)."""
    return create_new_story()

@app.route('/stories/<story_id>/choices/<choice_id>', methods=['POST', 'OPTIONS'])
@auth_required
def root_make_choice(story_id, choice_id):
    """Make a choice in a story (without /api prefix)."""
    return make_choice(story_id, choice_id)

@app.route('/stories/<story_id>', methods=['DELETE', 'OPTIONS'])
@auth_required
def root_delete_story(story_id):
    """Delete a story (without /api prefix)."""
    return delete_story_by_id(story_id)

# Original API endpoints with /api prefix
@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_status():
    """API endpoint to check if the server is running."""
    return jsonify({
        'status': 'ok',
        'message': 'StoryTeller API is running'
    })

@app.route('/api/stories', methods=['GET', 'OPTIONS'])
@auth_optional
def get_stories():
    """API endpoint to get all stories."""
    # If authenticated, filter to only show user's stories
    if hasattr(g, 'user_id') and g.user_id:
        # Get stories for the authenticated user
        stories = get_user_stories(g.user_id)
    else:
        # Get all stories for unauthenticated users
        stories = get_all_stories()
        
    return jsonify([story.model_dump() for story in stories])

@app.route('/api/stories/<story_id>', methods=['GET', 'OPTIONS'])
@auth_optional
def get_story_by_id(story_id):
    """API endpoint to get a specific story."""
    story = get_story(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404
    
    # In a real implementation, you might check if the user has access to this story
    # if hasattr(g, 'user_id') and g.user_id and story.user_id != g.user_id:
    #    return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(story.model_dump())

@app.route('/api/stories/<story_id>', methods=['DELETE', 'OPTIONS'])
@auth_required
def delete_story_by_id(story_id):
    """API endpoint to delete a story."""
    # Get the story first to check ownership
    story = get_story(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404
    
    # Check if the user owns this story
    if story.user_id and story.user_id != g.user_id:
        return jsonify({'error': 'Access denied: You do not own this story'}), 403
    
    success = delete_story(story_id)
    if not success:
        return jsonify({'error': 'Failed to delete story'}), 500
    
    return jsonify({'success': True})

@app.route('/api/stories', methods=['POST', 'OPTIONS'])
@auth_required
def create_new_story():
    """API endpoint to create a new story."""
    try:
        data = request.json
        
        params = StoryCreationParams(
            character_name=data.get('character_name', ''),
            character_gender=data.get('character_gender', 'unspecified'),
            setting=data.get('setting', 'cultivation'),
            tone=data.get('tone', 'adventure'),
            character_origin=data.get('character_origin', 'normal'),
            story_length=data.get('story_length', 'medium'),
            user_id=g.user_id  # Add the authenticated user's ID
        )
        
        # Generate initial story content
        story_content, choices = AIService.generate_initial_story(
            character_name=params.character_name,
            character_gender=params.character_gender,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
            story_length=params.story_length
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

@app.route('/api/stories/<story_id>/choices/<choice_id>', methods=['POST', 'OPTIONS'])
@auth_required
def make_choice(story_id, choice_id):
    """API endpoint to make a choice in a story."""
    try:
        # Get user ID from auth context
        user_id = g.user_id
        
        # Check if user has reached their limit (skip for infinite stories)
        story = get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Check if the user owns this story
        if story.user_id and story.user_id != user_id:
            return jsonify({'error': 'Access denied: You do not own this story'}), 403
            
        # For non-infinite stories, check the usage limits
        if story.story_length != "infinite":
            if not usage_service.can_continue_story(user_id):
                remaining = usage_service.get_remaining_continuations(user_id)
                return jsonify({
                    'error': 'Usage limit reached',
                    'message': f'You have reached your limit of story continuations. Remaining: {remaining}',
                    'remaining_continuations': remaining
                }), 429
            
            # Increment usage count
            usage_service.increment_story_continuations(user_id)
        
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
            character_gender=story.character_gender,
            setting=story.setting,
            tone=story.tone,
            story_length=story.story_length,
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
        
        # Get remaining continuations (for non-infinite stories)
        if story.story_length != "infinite":
            remaining = usage_service.get_remaining_continuations(user_id)
            # Add usage info to response
            response_data = updated_story.model_dump()
            response_data['usage'] = {
                'remaining_continuations': remaining,
                'limit': usage_service.get_user_usage(user_id).story_continuations_limit
            }
        else:
            response_data = updated_story.model_dump()
            response_data['usage'] = {
                'remaining_continuations': 'unlimited',
                'limit': 'unlimited'
            }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usage', methods=['GET', 'OPTIONS'])
@auth_required
def get_usage():
    """API endpoint to get user's usage statistics."""
    user_id = g.user_id if hasattr(g, 'user_id') else request.headers.get('X-User-ID', request.remote_addr)
    usage = usage_service.get_user_usage(user_id)
    
    return jsonify({
        'user_id': usage.user_id,
        'story_continuations_used': usage.story_continuations_used,
        'story_continuations_limit': usage.story_continuations_limit,
        'remaining_continuations': usage_service.get_remaining_continuations(user_id)
    })

@app.route('/api/usage/reset', methods=['POST', 'OPTIONS'])
@auth_required
def reset_usage():
    """Admin endpoint to reset a user's usage."""
    # This should be protected with admin authentication in production
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    usage_service.reset_daily_limits(user_id)
    return jsonify({'success': True})

def run_api(host='0.0.0.0', port=5001, debug=False):
    """Run the Flask API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    debug = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
    run_api(host=host, port=port, debug=debug) 