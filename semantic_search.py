from openai import OpenAI
import json
from pinecone import Pinecone

with open("config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])
PINECONE_KEY = config["pinecone"]["api_key"]
PINECONE_ENV = config["pinecone"]["environment"]
pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index("email-embeddings")

prompt = f"Given these emails, semantically label each email with a category. You decide the categories. Here are the emails:\n\n"
response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.0
    )
print(response.choices[0].message.content)
