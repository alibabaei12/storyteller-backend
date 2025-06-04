#!/usr/bin/env python3
"""
Simple deployment test script.
"""

import os
import sys
import importlib

# Set PORT env var to simulate Render environment
os.environ["PORT"] = "8000"

print("=== StoryTeller Deployment Test ===")

# Check core packages
packages_to_check = [
    "flask", "flask_cors", "openai", "pydantic", "dotenv", 
    "gunicorn", "rich", "jsonpickle", "uuid", "typing_extensions"
]

missing_packages = []
for package in packages_to_check:
    try:
        importlib.import_module(package)
        print(f"✅ {package} is installed")
    except ImportError:
        missing_packages.append(package)
        print(f"❌ {package} is missing")

if missing_packages:
    print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
    print("Please add them to requirements.txt and run: pip install -r requirements.txt")
    sys.exit(1)

# Check Flask app creation
try:
    from main import create_app
    app = create_app()
    print("✅ Flask app created successfully")
except Exception as e:
    print(f"❌ Flask app creation failed: {str(e)}")
    sys.exit(1)

# Check Procfile
try:
    with open('Procfile', 'r') as f:
        procfile_content = f.read().strip()
        if "gunicorn 'main:create_app()' --bind=0.0.0.0:$PORT" in procfile_content:
            print("✅ Procfile is correctly configured")
        else:
            print(f"❌ Procfile has incorrect configuration: {procfile_content}")
            print("It should be: web: gunicorn 'main:create_app()' --bind=0.0.0.0:$PORT")
            sys.exit(1)
except Exception as e:
    print(f"❌ Error reading Procfile: {str(e)}")
    sys.exit(1)

# Check data directory
if not os.path.exists('data'):
    try:
        os.makedirs('data')
        print("✅ Created data directory")
    except Exception as e:
        print(f"❌ Failed to create data directory: {str(e)}")
        sys.exit(1)
else:
    print("✅ Data directory exists")

# Check .env file
if os.path.exists('.env'):
    print("✅ .env file exists")
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY not found in .env file")
        print("    Make sure to set it in Render.com environment variables")
else:
    print("⚠️ Warning: .env file not found")
    print("    Make sure to set OPENAI_API_KEY in Render.com environment variables")

print("\n✅ All deployment tests passed! Your app should deploy successfully.")
print("\nIMPORTANT: Make sure your Render.com settings are:")
print("- Build Command: pip install -r requirements.txt")
print("- Start Command: gunicorn 'main:create_app()' --bind=0.0.0.0:$PORT")
print("- Environment Variables: Add OPENAI_API_KEY=your_api_key_here")
