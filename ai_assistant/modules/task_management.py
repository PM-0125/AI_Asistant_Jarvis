# modules/task_management.py

import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class TaskManager:
    def __init__(self):
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    def list_messages(self, user_id='me', label_ids=[]):
        try:
            response = self.service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            return messages
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def get_message(self, user_id, msg_id):
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()
            return message
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        return {'raw': raw}

    def send_message(self, user_id, message):
        try:
            message = self.service.users().messages().send(userId=user_id, body=message).execute()
            print(f'Message Id: {message["id"]}')
            return message
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
