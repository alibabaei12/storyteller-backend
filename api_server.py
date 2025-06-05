#!/usr/bin/env python3
"""
Simple API server for StoryTeller
Run with: python3 api_server.py
"""

import os
from dotenv import load_dotenv
from app.api import app

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("Starting StoryTeller API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug) 