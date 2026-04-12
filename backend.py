import os
import csv
import json
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import openai
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes for Gmail and Calendar APIs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly'
]
GROUPS_FILE = 'recipient_groups.json'


def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return []
    try:
        with open(GROUPS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []


def save_groups(groups):
    with open(GROUPS_FILE, 'w', encoding='utf-8') as file:
        json.dump(groups, file, indent=2)


def authenticate_google():
    """Authenticate and return services for Gmail and Calendar."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    gmail_service = build('gmail', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    return gmail_service, calendar_service


def get_connected_email(service):
    try:
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress', 'Unknown')
    except Exception:
        return 'Unknown'


def get_calendar_events(service, days=7):
    """Retrieve upcoming events from Google Calendar."""
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=time_min, timeMax=time_max,
        singleEvents=True, orderBy='startTime'
    ).execute()
    return events_result.get('items', [])


def read_csv_tasks(file_path):
    """Read tasks from a CSV file."""
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tasks.append(row)
    return tasks


def analyze_tasks_with_ai(tasks_data, source):
    """Use OpenAI to analyze tasks and generate a report."""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "OpenAI API key not found."
    openai.api_key = api_key

    prompt = (
        f"Analyze the following {source} data and generate a structured report on tasks that need to be completed:\n\n"
        f"{tasks_data}\n\n"
        "Provide a summary of upcoming tasks, priorities, and any recommendations."
    )

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0].message.content


def send_email(service, to, subject, body):
    """Send an email using Gmail API."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = 'me'
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw}
    sent_message = service.users().messages().send(userId='me', body=message_body).execute()
    return sent_message.get('id')


def logout():
    """Clear stored Google credentials."""
    if os.path.exists('token.json'):
        os.remove('token.json')
        return True
    return False