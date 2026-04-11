# OpenAI and Gmail Integration Programs

This repository contains two Python programs:

1. **main.py**: A simple program that generates a friendly email using OpenAI and sends it via Gmail.
2. **task_reporter.py**: An automated task reporting system that retrieves data from Google Calendar or a CSV file, analyzes it with OpenAI, generates a report, and sends it via email.

## Setup

1. **Google Cloud Project** (for Gmail and Calendar APIs):
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Enable the following APIs:
     - Gmail API
     - Google Calendar API (for task_reporter.py)
   - Create OAuth 2.0 Client IDs (Desktop application).
   - Download the `credentials.json` file and place it in the project root.

2. **OpenAI API Key**:
   - Go to [OpenAI Platform](https://platform.openai.com/).
   - Sign up or log in.
   - Navigate to API Keys and create a new key.
   - Create a `.env` file in the project root with: `OPENAI_API_KEY=your_api_key_here`

3. **Install Dependencies**:
   - Run `py -m pip install -r requirements.txt`

4. **Run the Programs**:
   - For simple email: `py main.py`
   - For task reporting: `py task_reporter.py`
     - Choose data source (Calendar or CSV).
     - For CSV, provide the file path (CSV should have columns like 'Task', 'Due Date', etc.).

## Notes
- The first run will open a browser for Google authentication.
- Ensure your Gmail account allows OAuth access.
- For CSV, use a simple format; the AI will analyze the content accordingly.