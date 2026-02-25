import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_PATH = "token.pickle"
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token) # type: ignore
    service = build("gmail", "v1", credentials=creds)
    return service

def send_email(service, to_email: str, subject: str, body: str):
    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"Email sent: {sent_message["id"]}")
