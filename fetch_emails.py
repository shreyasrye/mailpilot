import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sklearn.feature_extraction.text import TfidfVectorizer
import base64
import pandas as pd
import tokens
import json
from PyPDF2 import PdfReader
from io import BytesIO

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("logs/fetch_emails.log"),
                    ])

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
with open("config.json") as config_file:
    config = json.load(config_file)
DATE_RANGE = config["gmail_api"]["date_range"]

def extract_text_from_pdf(pdf_data):
    """
    Extract text from PDF binary data.
    """
    text = ""
    try:
        reader = PdfReader(BytesIO(pdf_data))
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
    return text

def process_attachment(service, user_id, message_id, attachment_id, mime_type):
    """
    Fetch and process an attachment from Gmail.
    """
    try:
        attachment = service.users().messages().attachments().get(userId=user_id, messageId=message_id, id=attachment_id).execute()
        file_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
        
        # Process based on mime_type (Might need to add more)
        if (mime_type == 'application/pdf' or 
            mime_type == 'application/x-pdf' or 
            mime_type == 'application/acrobat' or 
            mime_type == 'applications/vnd.pdf' or 
            mime_type == 'text/pdf' or 
            mime_type == 'text/x-pdf' or 
            mime_type == 'application/octet-stream'):
            return extract_text_from_pdf(file_data)
        
        return None
    except Exception as e:
        logger.error(f"Failed to process attachment: {e}")
        return None

def main():
    logger.info("Starting main function")
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error("Failed to refresh token, re-authenticating: %s", e)
                os.remove("token.json")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        query = DATE_RANGE
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=50, q=query).execute()
        messages = results.get("messages", [])
        if not messages:
            logger.info("You have no new messages.")
            return pd.DataFrame()
        else:
            res = []
            for message in messages:
                data = None
                attachment_texts = []
                msg = service.users().messages().get(userId="me", id=message["id"]).execute()
                email_data = msg["payload"]["headers"]
                from_name = None
                subject = None
                date = None

                for values in email_data:
                    name = values["name"]
                    if name.lower() == "from":
                        from_name = values["value"]
                    elif name.lower() == "subject":
                        subject = values["value"]
                    elif name.lower() == "date":
                        date = values["value"]

                if msg["payload"]["mimeType"] in ["text/plain", "text/html"]:
                    data = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")
                else:
                    for p in msg["payload"]["parts"]:
                        if p["mimeType"] in ["text/plain", "text/html"]:
                            data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")

                        if "attachmentId" in p["body"]:
                            print("Attachment found\n")
                            attachment_id = p["body"]["attachmentId"]
                            mime_type = p["mimeType"]
                            attachment_text = process_attachment(service, "me", message["id"], attachment_id, mime_type)
                            print(attachment_text)
                            if attachment_text:
                                attachment_texts.append(attachment_text)
                
                combined_text = (data or "") + " ".join(attachment_texts)
                
                res.append({"id": message['id'], "From": from_name, "Subject": subject, "body": combined_text, "date": date})
            result = pd.DataFrame(res)
            result["date"] = pd.to_datetime(result["date"], errors="coerce", utc=True)
            return result
    except HttpError as error:
        logger.error("An error occurred: %s", error)
        return pd.DataFrame()

def init():
    logger.info("Initializing data processing")
    result = []
    data = main()
    if data.empty:
        logger.error("No data returned from main function")
        return pd.DataFrame(result)
    body = data["body"]
    for i in range(len(body)):
        processed_body = "" if pd.isna(body[i]) else ' '.join(tokens.textFileProcess(body[i], "nofancy", "yesStop", tokens.stopword_lst))
        result.append({"id": data["id"][i], "From": data["From"][i], "Subject": data["Subject"][i], "body": processed_body})
    result = pd.DataFrame(result)
    result.to_csv("processed_emails.csv", index=False)
    return result

if __name__ == "__main__":
    init()
