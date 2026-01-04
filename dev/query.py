import chromadb

# 1. Setup Connection
client = chromadb.HttpClient(host='127.0.0.1', port=8000)
collection_id = "0fd760c1-a678-4c77-96cc-f97bb38d674c"

try:
    collection = client.get_collection(name=collection_id)
    print(f"✅ Connected to Collection: {collection_id}")
    print(f"📊 Total items in index: {collection.count()}\n")
except Exception as e:
    print(f"❌ Error: Could not find collection. {e}")
    exit()

# 2. Define Multiple Test Queries
test_queries = [
    "Howard Guzman's claim details",
    "List the procedure codes mentioned in the documents.",
    "Which patient has the highest claim cost?",
    "Find any mention of medication or prescriptions."
]

# 3. Execute and Display Results
for i, query in enumerate(test_queries, 1):
    print(f"🔍 Query {i}: '{query}'")
    
    # We ask for the top 2 results for each query
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    
    # Print the results found
    if results['documents'][0]:
        for idx, doc in enumerate(results['documents'][0]):
            score = results['distances'][0][idx]
            # Lower distance usually means higher similarity
            print(f"   [Result {idx+1}] (Distance: {score:.4f})")
            print(f"   Text: {doc[:150]}...") 
            print(f"   Metadata: {results['metadatas'][0][idx]}")
            print("-" * 30)
    else:
        print("   ⚠️ No results found for this query.")
    print("\n")