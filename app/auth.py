"""Authentication middleware for development with minimal token validation."""

import base64
import json
import logging
import os
from functools import wraps

from flask import request, jsonify, g

from .config.logging import setup_logging

# Configure logging
setup_logging()

# Get logger
logger = logging.getLogger(__name__)

# For development, we'll use a simplified token verification
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
logger.info(f"Using Firebase Project ID: {FIREBASE_PROJECT_ID}")
logger.warning("DEVELOPMENT MODE: Using simplified token validation")

def get_auth_token():
    """Extract the auth token from the request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.debug("No Authorization header found")
        return None
    
    # Expected format: "Bearer {token}"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid Authorization header format: {auth_header}")
        return None
    
    logger.debug("Auth token extracted successfully")
    return parts[1]

def decode_token_simple(token):
    """Simple JWT decoder that doesn't verify the signature (FOR DEVELOPMENT ONLY)."""
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode the payload (middle part)
        # Add padding if needed
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
        
        decoded = base64.b64decode(payload)
        data = json.loads(decoded)
        
        logger.debug("Token decoded successfully (DEV MODE)")
        return data
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

def auth_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        token = get_auth_token()
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        # In development mode, decode the token without verification
        decoded_token = decode_token_simple(token)
        if not decoded_token:
            return jsonify({"error": "Invalid token format"}), 401
        
        # Store user info in Flask's g object
        g.user_id = decoded_token.get("user_id") or decoded_token.get("sub") or decoded_token.get("uid")
        g.user_email = decoded_token.get("email", "")
        
        logger.info(f"Authentication successful for user: {g.user_id}")
        return f(*args, **kwargs)
    
    return decorated_function

def auth_optional(f):
    """Decorator to use authentication if provided but not require it."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        token = get_auth_token()
        
        if token:
            # In development mode, decode the token without verification
            decoded_token = decode_token_simple(token)
            if decoded_token:
                g.user_id = decoded_token.get("user_id") or decoded_token.get("sub") or decoded_token.get("uid")
                g.user_email = decoded_token.get("email", "")
                logger.debug(f"Optional authentication successful for user: {g.user_id}")
            else:
                g.user_id = None
                g.user_email = None
                logger.warning("Optional authentication token was invalid")
        else:
            g.user_id = None
            g.user_email = None
            logger.debug("No authentication token provided for optional auth")
        
        return f(*args, **kwargs)
    
    return decorated_function 