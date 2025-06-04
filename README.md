# StoryTeller API

The backend API for the StoryTeller interactive fiction application.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Running Locally

Run the API server:

```bash
python main.py
```

The API will be available at http://localhost:5000

## Deploying to Render.com

1. Push your code to GitHub
2. Create a new Web Service on Render.com
3. Connect to your GitHub repository
4. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn 'main:create_app()' --bind=0.0.0.0:$PORT`
5. Add the environment variable:
   - `OPENAI_API_KEY`: Your OpenAI API key

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