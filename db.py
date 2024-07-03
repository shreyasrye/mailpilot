from pinecone import Pinecone
import json
from openai import OpenAI
import fetch_emails
import tqdm


with open("config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])
PINECONE_KEY = config["pinecone"]["api_key"]
PINECONE_ENV = config["pinecone"]["environment"]
pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index("email-embeddings")

def num_tokens(text: str, model: str = "gpt-4o"):
  response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": text}],
        max_tokens=1  # Setting max_tokens to 1 as we are only interested in counting tokens
    )
  return response.usage.total_tokens

def split_text(email_df, max_tokens_per_chunk):
    """
    Split the email text data into chunks that fit within the token limits.
    
    Parameters:
        emails (pd.DataFrame): DataFrame containing email data with columns 'id', 'from', 'subject', and 'body'.
        max_tokens_per_chunk (int): Maximum number of tokens allowed per chunk.
        
    Returns:
        List[Dict]: A list of dictionaries where each dictionary represents a chunk of email data.
    """
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0

    for index, row in email_df.iterrows():
        email_text = f"From: {row['From']}\nSubject: {row['Subject']}\nBody: {row['body']}\n"
        email_tokens = num_tokens(email_text)

        # If adding the current email exceeds the token limit, start a new chunk
        if current_chunk_tokens + email_tokens > max_tokens_per_chunk:
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "emails": current_chunk,
                "tokens": current_chunk_tokens
            })
            current_chunk = []
            current_chunk_tokens = 0

        current_chunk.append({
            "id": row['id'],
            "from": row['From'],
            "subject": row['Subject'],
            "body": row['body']
        })
        current_chunk_tokens += email_tokens

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append({
            "chunk_id": len(chunks) + 1,
            "emails": current_chunk,
            "tokens": current_chunk_tokens
        })
    return chunks

def generate_embeddings(text_chunks):
    """
    Generates embeddings for each email using OpenAI's text-embedding-ada-002 model.
    """
    embeddings = []
    for chunk in tqdm.tqdm(text_chunks, desc="Generating embeddings"):
        for email in chunk['emails']:
            email_text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}\n"
            response = client.embeddings.create(input=email_text, model="text-embedding-ada-002")
            embeddings.append(response.data[0].embedding)
    print(len(embeddings))
    return embeddings


def main():
    emails = fetch_emails.init()
    email_chunks = split_text(emails, 3000)
    embeddings = generate_embeddings(email_chunks)

    metadata = []
    for chunk in email_chunks:
        for email in chunk['emails']:
            metadata.append({
                "id": email['id'],
                "from": email['from'],
                "subject": email['subject']
            })

    ids = [f"email-{i}" for i in range(len(metadata))]

    pinecone_vectors = list(zip(ids, embeddings, metadata))

    index.upsert(vectors=pinecone_vectors)
