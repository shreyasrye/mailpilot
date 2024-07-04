from openai import OpenAI
import json
from db import split_text as split
import fetch_emails

with open("config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])

with open ("prompts.json") as prompts:
    instructions = json.load(prompts)

def classify_emails(chunk):
    """
    Classify a chunk of email data using the OpenAI API; 
    Returns a .json where each dictionary represents a classified chunk of emails.
    """
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
        temperature=0.5
    )
    return response.choices[0].message.content


def parse_labels(chunk_ls):
    """
    Parse the labeled chunk JSON and convert it into a dictionary of each label and all its associated emails.
    """
    output = {}
    for labeled_chunk_dict in chunk_ls:
        for id, label in labeled_chunk_dict.items():
            if output.get(label):
                output[label].append(id)
            else:
                output[label] = [id]
    return output

def clean_api_response(api_response):
    """
    Clean the API response to remove unnecessary characters. In this case, anything outside the curly braces.
    """
    start = api_response.find("{")
    end = api_response.rfind("}")
    return api_response[start:end+1]


def main():
    emails = fetch_emails.init()
    chunks = split(emails, 3000)
    labeled_chunks = []
    for chunk in chunks:
        api_response = clean_api_response(classify_emails(chunk))
        print(api_response)
        chunk_dict = eval(api_response)
        labeled_chunks.append(chunk_dict)
    print(labeled_chunks)
    parsed_labeled_chunks = parse_labels(labeled_chunks)
    print(parsed_labeled_chunks)
    return parsed_labeled_chunks
