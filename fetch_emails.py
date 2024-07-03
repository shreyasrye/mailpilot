import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sklearn.feature_extraction.text import TfidfVectorizer
import base64
import pandas as pd
import tokens

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def parse_msg(msg):
    if msg.get("payload").get("body").get("data"):
        return base64.urlsafe_b64decode(msg.get("payload").get("body").get("data").encode("ASCII")).decode("utf-8")
    return msg.get("snippet")

def main():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "client_secret.json", SCOPES
      )
      creds = flow.run_local_server(port=8080)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    
    # Specify the date range (use RFC 3339 format: YYYY-MM-DD)
    query = 'after:2023-06-01 before:2023-06-30'

    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=100, q=query).execute()
    messages = results.get("messages", [])
    if not messages:
      print("You have no New Messages.")
      return 0
    else:
      res = []
      message_count = 0
      for message in messages:
          data = None
          msg = service.users().messages().get(userId="me", id=message["id"]).execute()
          message_count = message_count + 1
          email_data = msg["payload"]["headers"] 
          for values in email_data:
            name = values["name"]
            # print(name)
            if name in ["From", "from"]: 
              from_name = values["value"]
              subject = [j["value"] for j in email_data if j["name"] == "Subject"]
            if msg["payload"]["mimeType"] in ["text/plain", "text/html"]:
              data = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")
            else:
              for p in msg["payload"]["parts"]:
                if p["mimeType"] in ["text/plain", "text/html"]:
                    data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
            # if data == None:
            #   for j in msg["payload"]["parts"]:
            #     print(j["mimeType"])
          res.append({"id": message['id'],"From": from_name, "Subject": subject, "body": data})
      result = pd.DataFrame(res)
      return result

  except HttpError as error:
    print(f"An error occurred: {error}")
    return None


def init():
  result = []
  data = main()
  body = data["body"]
  for i in range(len(body) - 1):
    if body[i] == None:
      result.append({"id": data["id"][i], "From": data["From"][i], "Subject": data["Subject"][i], "body": "Error"})
    else:
      result.append({"id": data["id"][i], "From": data["From"][i], "Subject": data["Subject"][i], "body": (tokens.textFileProcess(body[i], "nofancy", "yesStop", "porterStem", tokens.stopword_lst))})
  result = pd.DataFrame(result)
  result['body'] = result['body'].apply(lambda tokens: ' '.join(tokens))
  return result


if __name__ == "__main__":
  init()