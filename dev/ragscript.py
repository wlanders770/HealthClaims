import chromadb
import requests
import json

# 1. Setup Connections
client = chromadb.HttpClient(host='127.0.0.1', port=8000)
collection_id = "0fd760c1-a678-4c77-96cc-f97bb38d674c"
collection = client.get_collection(name=collection_id)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest" # or whatever model you have in Ollama

def ask_about_claims(user_query):
    # STEP 1: Retrieve the raw data from Chroma
    # We fetch the top 2 most relevant claims
    results = collection.query(
        query_texts=[user_query],
        n_results=500
    )
    
    # Combine the retrieved claims into one block of text
    context = "\n---\n".join(results['documents'][0])

    # STEP 2: Create a prompt for Ollama
    prompt = f"""
    You are a medical billing assistant. Use the following FHIR claim data to answer the user's question.
    When a claim is found that matches the query, provide all details from that claim.
    If the answer isn't in the data, say you don't know. 
    Be specific and extract exact numbers or codes.

    ### CLAIM DATA:
    {context}

    ### USER QUESTION:
    {user_query}

    ### ANSWER:
    """

    # STEP 3: Send to Ollama
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    print(f"🤔 Querying Ollama for: '{user_query}'...")
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get('response')
    else:
        return f"Error: {response.text}"

# --- EXECUTION ---
question = "Can you show me all claims with a diagnosis of low back pain?"
answer = ask_about_claims(question)

print("\n" + "="*50)
print(f"FINAL ANSWER:\n{answer}")
print("="*50)