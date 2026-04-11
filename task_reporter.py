import os
import csv
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

def get_calendar_events(service, days=7):
    """Retrieve upcoming events from Google Calendar."""
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=time_min, timeMax=time_max,
        singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events

def read_csv_tasks(file_path):
    """Read tasks from a CSV file."""
    tasks = []
    with open(file_path, 'r') as file:
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

    prompt = f"Analyze the following {source} data and generate a structured report on tasks that need to be completed:\n\n{tasks_data}\n\nProvide a summary of upcoming tasks, priorities, and any recommendations."
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    report = response.choices[0].message.content
    return report

def send_email(service, to, subject, body):
    """Send an email using Gmail API."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = 'me'
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message sent: {sent_message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Task Reporting System")
    print("Choose data source:")
    print("1. Google Calendar")
    print("2. CSV File")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        gmail_service, calendar_service = authenticate_google()
        events = get_calendar_events(calendar_service)
        tasks_data = "\n".join([f"{event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events])
        source = "calendar events"
    elif choice == '2':
        csv_path = input("Enter CSV file path: ").strip()
        if not os.path.exists(csv_path):
            print("CSV file not found.")
            return
        tasks = read_csv_tasks(csv_path)
        tasks_data = "\n".join([str(task) for task in tasks])
        source = "CSV tasks"
        gmail_service, _ = authenticate_google()  # Still need Gmail for sending
    else:
        print("Invalid choice.")
        return

    report = analyze_tasks_with_ai(tasks_data, source)
    print("Generated Report:")
    print(report)

    recipient = input("Enter recipient email: ")
    subject = "Automated Task Report"
    send_email(gmail_service, recipient, subject, report)

if __name__ == '__main__':
    main()