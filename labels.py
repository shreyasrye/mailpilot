import json
import os.path
import classify
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_label(service, user_id, label_name):
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    try:
        label = service.users().labels().create(userId=user_id, body=label_body).execute()
        return label['id']
    except Exception as error:
        print(f'An error occurred while creating the label: {error}')
        return None

def add_label_to_message(service, user_id, message_id, label_id):
    msg_labels = {'addLabelIds': [label_id]}
    try:
        message = service.users().messages().modify(userId=user_id, id=message_id, body=msg_labels).execute()
        return message
    except Exception as error:
        print(f'An error occurred while adding the label to the message: {error}')
        return None

def main():
    service = get_gmail_service()
    user_id = 'me'

    label_dict = classify.main()

    for label_name, msg_list in label_dict.items():
        label_id = create_label(service, user_id, label_name)
        for message_id in msg_list:
            add_label_to_message(service, user_id, message_id, label_id)

    # for message_id, label_name in email_labels.items():
    #     # Create label if it doesn't exist
    #     label_id = create_label(service, user_id, label_name)
    #     if label_id:
    #         # Add label to the message
    #         add_label_to_message(service, user_id, message_id, label_id)

if __name__ == '__main__':
    main()
