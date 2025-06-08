from flask import Flask, request, jsonify, redirect, g
from flask_cors import CORS
import os
import json
from uuid import uuid4

from .models import Story, StoryNode, Choice, StoryCreationParams, StoryMetadata, FeedbackRequest
from .storage import (
    save_story, 
    get_story, 
    delete_story, 
    get_all_stories, 
    add_story_node, 
    save_choice, 
    create_story,
    get_user_stories,
    submit_feedback
)
from .ai_service import AIService
from .usage_service import usage_service
from .auth import auth_required, auth_optional

# Initialize Flask app
app = Flask(__name__)

# Simplified CORS configuration to avoid duplicate headers
CORS(app, 
    origins=["http://localhost:3000", "https://storyteller-frontend-1.onrender.com"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-ID"],
    expose_headers=["Authorization"],
    supports_credentials=True
)

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

@app.route('/stories/<story_id>/share', methods=['POST', 'OPTIONS'])
@auth_required
def root_generate_share_token(story_id):
    """Generate a share token for public viewing of a story (without /api prefix)."""
    return generate_share_token(story_id)

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
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:        
        # Get the story first to check ownership and save creation date
        story = get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Check if the user owns this story
        if story.user_id and story.user_id != g.user_id:
            return jsonify({'error': 'Access denied: You do not own this story'}), 403
        
        # Save creation date before deleting (using last_updated as creation timestamp)
        story_last_updated = story.last_updated
        user_id = g.user_id
        
        success = delete_story(story_id)
        if not success:
            return jsonify({'error': 'Failed to delete story'}), 500
        
        # Update usage tracking - decrement stories created count if it was created this month
        if story_last_updated:
            try:
                # Check if the story was created this month
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                story_created = datetime.fromtimestamp(story_last_updated, tz=timezone.utc)
                
                # If story was created in the current month, decrement the counter
                if (story_created.year == now.year and 
                    story_created.month == now.month):
                    usage_service.decrement_stories_created(user_id)
                    print("[API] Decremented usage count for user")
            except Exception as e:
                print(f"[API] Error updating usage after delete: {e}")
                # Don't fail the delete if usage update fails
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"[API] Error in delete_story_by_id: {e}")
        return jsonify({'error': 'Failed to delete story'}), 500

@app.route('/api/stories', methods=['POST', 'OPTIONS'])
@auth_required
def create_new_story():
    """API endpoint to create a new story."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        # Check if user can create new stories
        user_id = g.user_id
        if not usage_service.can_create_story(user_id):
            remaining = usage_service.get_remaining_stories(user_id)
            return jsonify({
                'error': 'Story creation limit reached',
                'message': f'You have reached your limit of {usage_service.get_user_usage(user_id).stories_created_limit} stories per month. Remaining: {remaining}',
                'remaining_stories': remaining
            }), 429
        
        data = request.json
        
        params = StoryCreationParams(
            character_name=data.get('character_name', ''),
            character_gender=data.get('character_gender', 'unspecified'),
            setting=data.get('setting', 'cultivation'),
            tone=data.get('tone', 'shonen'),
            character_origin=data.get('character_origin', 'weak'),
            manga_genre=data.get('manga_genre', None),
            user_id=g.user_id  # Add the authenticated user's ID
        )
        
        # Generate initial story content
        story_content, choices = AIService.generate_initial_story(
            character_name=params.character_name,
            character_gender=params.character_gender,
            setting=params.setting,
            tone=params.tone,
            character_origin=params.character_origin,
            manga_genre=params.manga_genre
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
        
        # Increment stories created count
        usage_service.increment_stories_created(user_id)
        
        # Add usage info to response
        usage = usage_service.get_user_usage(user_id)
        response_data = story.model_dump()
        response_data['usage'] = {
            'remaining_stories': usage_service.get_remaining_stories(user_id),
            'remaining_continuations': usage_service.get_remaining_continuations(user_id),
            'stories_limit': usage.stories_created_limit,
            'continuations_limit': usage.story_continuations_limit
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stories/<story_id>/choices/<choice_id>', methods=['POST', 'OPTIONS'])
@auth_required
def make_choice(story_id, choice_id):
    """API endpoint to make a choice in a story."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
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
            
        # Check usage limits for story continuations
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
        manga_genre_value = getattr(story, 'manga_genre', None)
        print(f"🔍 DEBUG API: character_name={story.character_name}, manga_genre={manga_genre_value}, setting={story.setting}")
        print(f"🔍 DEBUG API: selected_choice='{selected_choice.text}'")
        print(f"🔍 DEBUG API: previous_content length={len(current_node.content)} chars")
        
        story_content, choices = AIService.continue_story(
            character_name=story.character_name,
            character_gender=story.character_gender,
            setting=story.setting,
            tone=story.tone,
            previous_content=current_node.content,
            selected_choice=selected_choice.text,

            manga_genre=manga_genre_value,
            character_origin=getattr(story, 'character_origin', 'normal')
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
        
        # Get remaining continuations
        remaining = usage_service.get_remaining_continuations(user_id)
        # Add usage info to response
        response_data = updated_story.model_dump()
        response_data['usage'] = {
            'remaining_continuations': remaining,
            'limit': usage_service.get_user_usage(user_id).story_continuations_limit
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usage', methods=['GET', 'OPTIONS'])
@auth_required
def get_usage():
    """API endpoint to get user's usage statistics."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    user_id = g.user_id if hasattr(g, 'user_id') else request.headers.get('X-User-ID', request.remote_addr)
    usage = usage_service.get_user_usage(user_id)
    
    return jsonify({
        'user_id': usage.user_id,
        'story_continuations_used': usage.story_continuations_used,
        'story_continuations_limit': usage.story_continuations_limit,
        'stories_created_this_month': getattr(usage, 'stories_created_this_month', 0),
        'stories_created_limit': getattr(usage, 'stories_created_limit', 5),
        'remaining_continuations': usage_service.get_remaining_continuations(user_id),
        'remaining_stories': usage_service.get_remaining_stories(user_id)
    })

@app.route('/api/usage/reset', methods=['POST', 'OPTIONS'])
@auth_required
def reset_usage():
    """Admin endpoint to reset a user's usage."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    # This should be protected with admin authentication in production
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    usage_service.reset_daily_limits(user_id)
    return jsonify({'success': True})



@app.route('/api/stories/<story_id>/share', methods=['POST', 'OPTIONS'])
@auth_required
def generate_share_token(story_id):
    """Generate a share token for public viewing of a story."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        # Get the story first to check ownership
        story = get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Check if the user owns this story
        if story.user_id and story.user_id != g.user_id:
            return jsonify({'error': 'Access denied: You do not own this story'}), 403
        
        # Generate a unique share token if it doesn't exist
        if not story.share_token:
            story.share_token = f"share_{uuid4().hex[:16]}"
            story.is_shareable = True
            
            # Update the story in storage
            from .storage import update_story_share_token
            success = update_story_share_token(story_id, story.share_token)
            if not success:
                return jsonify({'error': 'Failed to generate share token'}), 500
        
        # Create URL that points to the React frontend, not the API
        if request.host_url.startswith('http://localhost'):
            # Local development - point to React dev server
            share_url = f"http://localhost:3000/share/{story.share_token}"
        else:
            # Production - point to the same host but React frontend route
            share_url = f"{request.host_url}share/{story.share_token}"
        
        return jsonify({
            'share_token': story.share_token,
            'share_url': share_url,
            'success': True
        })
        
    except Exception as e:
        print(f"[API] Error generating share token: {e}")
        return jsonify({'error': 'Failed to generate share token'}), 500

@app.route('/api/shared/<share_token>', methods=['GET'])
def view_shared_story(share_token):
    """API endpoint to get shared story data for frontend."""
    try:
        # Find story by share token
        from .storage import get_story_by_share_token
        story = get_story_by_share_token(share_token)
        
        if not story or not story.is_shareable:
            return jsonify({'error': 'Shared story not found or not available'}), 404
        
        # Return the story data for public viewing
        story_data = story.model_dump()
        
        # Remove sensitive fields for public viewing
        story_data.pop('user_id', None)
        story_data.pop('share_token', None)
        
        return jsonify(story_data)
        
    except Exception as e:
        print(f"[API] Error viewing shared story: {e}")
        return jsonify({'error': 'Failed to load shared story'}), 500

@app.route('/api/feedback', methods=['POST'])
@auth_required
def submit_feedback_endpoint():
    """Submit user feedback with rate limiting and validation."""
    try:
        user_id = g.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'feedback_type' not in data or 'message' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create feedback request
        feedback_request = FeedbackRequest(
            feedback_type=data.get('feedback_type'),
            message=data.get('message', ''),
            contact_email=data.get('contact_email', '')
        )
        
        # Submit with rate limiting
        success = submit_feedback(user_id, feedback_request)
        
        if not success:
            return jsonify({
                'error': 'Feedback submission failed. You may have exceeded the rate limit (3 per day, 1 per 10 minutes) or provided invalid input.'
            }), 429
        
        return jsonify({
            'message': 'Feedback submitted successfully. Thank you!',
            'success': True
        })
        
    except Exception as e:
        print(f"[API] Error in submit_feedback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def run_api(host='0.0.0.0', port=5001, debug=False):
    """Run the Flask API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    debug = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
    run_api(host=host, port=port, debug=debug) 