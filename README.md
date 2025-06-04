# StoryTeller

An AI-powered interactive fiction experience running in your terminal.

## Features

- Generate unique, AI-driven interactive stories
- Multiple settings, character origins, and power systems
- Terminal-based UI with rich text formatting
- Local storage for saving and continuing stories
- Robust error handling and logging

## Requirements

- Python 3.7+
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/storyteller.git
   cd storyteller-python
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the application:
```
python main.py
```

Follow the prompts to:
1. Create a new story with your character
2. Choose settings, origin, power system, and tone
3. Make choices to advance the story
4. Save and load stories

## Directory Structure

```
storyteller-python/
├── app/                  # Main application package
│   ├── __init__.py       # Package initialization
│   ├── ai_service.py     # OpenAI integration
│   ├── game.py           # Terminal UI and game logic
│   ├── models.py         # Data models
│   └── storage.py        # Local storage utilities
├── data/                 # Directory for saved stories (created on first run)
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── .env                  # Environment variables (you need to create this)
```

## Future Enhancements

- Cloud-based storage option
- User authentication
- More settings and story genres
- Web-based frontend

## License

MIT 