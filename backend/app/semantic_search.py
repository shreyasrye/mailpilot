# with open("/app/app/config.json") as config:
#   config = json.load(config)
# client = OpenAI(api_key=config["openai"]["api_key"])
# PINECONE_KEY = config["pinecone"]["api_key"]
# PINECONE_ENV = config["pinecone"]["environment"]
# pc = Pinecone(api_key=PINECONE_KEY)
# index = pc.Index(config["pinecone"]["index"])

def semantic_search(query, client, pc_index):
    query_embedding = client.embeddings.create(
            input=[query], 
            model="text-embedding-ada-002",
        ).data[0].embedding

    query_result = pc_index.query(vector=query_embedding, top_k=5, include_metadata=True)
    relevant_texts = [match['metadata'] for match in query_result['matches']]
    context = '\n\n'.join(str(relevant_texts))

    prompt = f"Context: {context}\n\nTell me about my recent flight history."

    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0.0
        )
    return response.choices[0].message.content
