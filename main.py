import os
import base64
from email.mime.text import MIMEText
import openai
import openai import client
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(service, to, subject, body):
    """Send an email using Gmail API."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = 'me'  # Use the authenticated user's email
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message sent: {sent_message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Set up OpenAI API
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable.")
        return
    openai.api_key = api_key

    # Authenticate Gmail
    service = authenticate_gmail()

    # Generate content with OpenAI
    prompt = "Write a short, friendly email to a friend saying hello and asking how they are."
    client = client.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    email_body = response.choices[0].message.content

    # Send the email
    recipient = input("Enter the recipient's email: ")
    subject = "Hello from OpenAI and Gmail!"
    send_email(service, recipient, subject, email_body)

if __name__ == '__main__':
    main()