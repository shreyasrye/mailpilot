import json
import os.path
import backend.app.classify_emails as classify_emails
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
import time
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

logging.basicConfig(level=logging.INFO)

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_label_id(service, user_id, label_name):
    """Retrieve the label ID for a given label name."""
    try:
        response = service.users().labels().list(userId=user_id).execute()
        labels = response.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']
    except HttpError as error:
        logging.error(f'An error occurred while retrieving labels: {error}')
    return None

def create_label(service, user_id, label_name):
    """Create a new label if it does not already exist."""
    label_id = get_label_id(service, user_id, label_name)
    if label_id:
        logging.info(f'Label "{label_name}" already exists with ID: {label_id}')
        return label_id

    label = {
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
        'name': label_name
    }
    try:
        created_label = service.users().labels().create(userId=user_id, body=label).execute()
        logging.info(f'Created label "{label_name}" with ID: {created_label["id"]}')
        return created_label['id']
    except HttpError as error:
        logging.error(f'An error occurred while creating the label: {error}')
        return None

def add_label_to_message(service, user_id, message_id, label_id):
    if not label_id:
        logging.error(f'No valid label ID provided for message ID {message_id}')
        return None, 'Invalid label ID'
    
    msg_labels = {'addLabelIds': [label_id]}
    try:
        message = service.users().messages().modify(userId=user_id, id=message_id, body=msg_labels).execute()
        return message, None
    except HttpError as error:
        return None, error

def main():
    service = get_gmail_service()
    user_id = 'me'

    classify_emails.main()
    label_map = classify_emails.LABELS_MAP

    for label_name, msg_list in label_map.items():
        label_id = create_label(service, user_id, label_name)
        for message_id in msg_list:
            retries = 3
            while retries > 0:
                message, error = add_label_to_message(service, user_id, message_id, label_id)
                if error:
                    if error.resp.status in [500, 502, 503, 504]:
                        retries -= 1
                        time.sleep(2 ** (3 - retries))  # Exponential backoff
                        logging.warning(f'Retrying... {retries} attempts left.')
                    else:
                        logging.error(f'Error adding label to message ID {message_id}: {error}')
                        break
                else:
                    logging.info(f'Successfully added label to message ID {message_id}')
                    break

if __name__ == "__main__":
    main()

