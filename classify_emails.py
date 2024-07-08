from openai import OpenAI
import json
from db import split_text as split
import fetch_emails

with open("config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])

LABELS_MAP = {}

def classify_emails(chunk):
    """
    Classify a chunk of email data using the OpenAI API; 
    Returns a .json where each dictionary represents a classified chunk of emails.
    """
    desired_labels = ["Action Required", "Work", "Spam", "Deadline Approaching", "Orders", "Social/Advertisement"]
    for label in desired_labels:
        if label not in LABELS_MAP:
            LABELS_MAP[label] = []
    labels_str = '\n'.join(desired_labels)
    with open ("prompts/classification_prompt.txt") as labels_prompt:
        instructions = labels_prompt.read()
    
    prompt = f"Emails: {chunk} \nLabels: {labels_str}\n{instructions}\n"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
        ],
        response_format={ "type": "json_object" },
        temperature=0.0
    )
    return response.choices[0].message.content

def sift_labels(label_dict):
    """
    Sift through the labels and merge the similar ones.
    """
    labels_str = '\n'.join(label_dict.keys())
    with open ("prompts/merge_labels_prompt.txt") as sift_prompt:
        instructions = sift_prompt.read()
    prompt = f"Labels: {labels_str}\n{instructions}\n"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.0
    )
    similar_labels = eval(response.choices[0].message.content)
    for pair in similar_labels:
        print("PAIR")
        print(pair)
        print()
        label_dict[pair[0]].extend(label_dict[pair[1]])
        del label_dict[pair[1]]
    return


def parse_labels(chunk_ls):
    """
    Parse the labeled chunk JSON and convert it into a dictionary of each label as the key and all its associated emails.
    """
    output = {}
    for labeled_chunk_dict in chunk_ls:
        for id, label in labeled_chunk_dict.items():
            if output.get(label):
                output[label].append(id)
            else:
                output[label] = [id]
    return output


def main():
    emails = fetch_emails.init()
    chunks = split(emails, 3000)
    for chunk in chunks:
        api_response = classify_emails(chunk)
        chunk_json = eval(api_response)
        for key, value in chunk_json.items():
            if key in LABELS_MAP:
                LABELS_MAP[key].extend(value)
            else:
                LABELS_MAP[key] = value
    sift_labels(LABELS_MAP)

main()# delete later
