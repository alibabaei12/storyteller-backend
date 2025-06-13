# StoryTeller API

The backend API for the StoryTeller interactive fiction application.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your OpenAI API key and Firebase configuration:
   ```
   OPENAI_API_KEY=your_key_here
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_CLIENT_EMAIL=your_service_account_email
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour_Private_Key_Here\n-----END PRIVATE KEY-----\n"
   ```

6. Firebase Setup:
   - Create a Firebase service account JSON file:
     - Go to Firebase Console > Project Settings > Service Accounts
     - Click "Generate New Private Key"
     - Save the file as `firebase-service-account.json` in the project root
     - This file is gitignored for security reasons
   - Alternatively, you can set the environment variables as shown above

## Running Locally

Run the API server:

```bash
python api_server.py
```

The API will be available at http://localhost:5001

## Deploying to Render.com

1. Push your code to GitHub
2. Create a new Web Service on Render.com
3. Connect to your GitHub repository
4. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn 'app.api:app' --bind=0.0.0.0:$PORT`
5. Add the environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FIREBASE_PROJECT_ID`: Your Firebase project ID
   - `FIREBASE_CLIENT_EMAIL`: Your Firebase service account email
   - `FIREBASE_PRIVATE_KEY`: Your Firebase private key (make sure to include the entire key with newlines)

## API Documentation

### Endpoints

- `GET /api/status` - Check API status
- `GET /api/stories` - Get all stories
- `GET /api/stories/<story_id>` - Get a specific story
- `POST /api/stories` - Create a new story
- `DELETE /api/stories/<story_id>` - Delete a story
- `POST /api/stories/<story_id>/choices/<choice_id>` - Make a choice in a story
- `GET /api/usage` - Get current usage statistics
- `POST /api/usage/reset` - Reset usage for a user (admin function) 