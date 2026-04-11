# OpenAI and Gmail Integration Programs

This repository contains Python programs for task reporting with Gmail and OpenAI integration:

1. **main.py**: Entry point that launches the Task Reporter user interface.
2. **task_reporter.py**: Orchestrates the application, importing GUI and backend components.
3. **gui.py**: Contains the Tkinter-based user interface for managing recipient groups and generating/sending reports.
4. **backend.py**: Handles all backend logic, including Google API authentication, data retrieval, AI analysis, and email sending.

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
   - Launch the Task Reporter UI: `py main.py`
   - If you want to run the task reporter directly in non-UI mode: `py task_reporter.py`
     - Choose data source (Calendar or CSV).
     - For CSV, provide the file path (CSV should have columns like 'Task', 'Due Date', etc.).

## Notes
- The first run will open a browser for Google authentication.
- Ensure your Gmail account allows OAuth access.
- For CSV, use a simple format; the AI will analyze the content accordingly.