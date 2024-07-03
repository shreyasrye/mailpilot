from openai import OpenAI
import json
import db
import fetch_emails
import time

with open("config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])

with open ("prompts.json") as prompts:
    instructions = json.load(prompts)

def classify_emails(chunk):
    """
    Classify a chunk of email data using the OpenAI API.
    
    Parameters:
        chunk (Dict): A dictionary representing a chunk of email data.
        
    Returns:
        List[Dict]: A list of dictionaries where each dictionary represents a classified email.
    """
    classified_emails = []
    email_format = f"id: Email id\nFrom: Who the email is from\nSubject: Subject/Title of Email\nBody: Email Body\n"
    directions = instructions["classification_prompt"]
    max_labels = instructions["max_num_labels"]
    desired_labels = instructions["desired_labels"]
    prompt = f"Emails:\n{chunk}\n Email Format: \n {email_format}\n Max Labels: {max_labels}\n Desired Labels: {desired_labels}\n Directions: {directions}\n"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.0
    )
    return response.choices[0].message.content


emails = fetch_emails.init()
chunks = db.split_text(emails, 3000)
labeled_chunks = []
for chunk in chunks:
    # Create a CSV file to write the classified emails
    with open('classified_emails.csv', 'a', newline='') as file:
        # Iterate over each email and write it to the CSV file
        chunk_dict = json.loads(classify_emails(chunk))
        labeled_chunks.append(chunk_dict)
print(labeled_chunks)