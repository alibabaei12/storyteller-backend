"""Authentication middleware for development with minimal token validation."""

import os
import json
import base64
from functools import wraps
from flask import request, jsonify, g

# For development, we'll use a simplified token verification
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
print(f"Using Firebase Project ID: {FIREBASE_PROJECT_ID}")
print("DEVELOPMENT MODE: Using simplified token validation")

def get_auth_token():
    """Extract the auth token from the request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        print("No Authorization header found")
        return None
    
    # Expected format: "Bearer {token}"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        print(f"Invalid Authorization header format: {auth_header}")
        return None
    
    print(f"Auth token extracted successfully: {parts[1][:10]}...")
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
        
        print(f"Decoded token payload (DEV MODE): {data}")
        return data
    except Exception as e:
        print(f"Error decoding token: {e}")
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
        
        print(f"Authentication successful for user: {g.user_id}")
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
                print(f"Optional authentication successful for user: {g.user_id}")
            else:
                g.user_id = None
                g.user_email = None
                print("Optional authentication token was invalid")
        else:
            g.user_id = None
            g.user_email = None
            print("No authentication token provided for optional auth")
        
        return f(*args, **kwargs)
    
    return decorated_function 