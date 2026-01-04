import chromadb
import csv
import sys
import os
import traceback
from chromadb.config import Settings

# --- CONFIGURATION ---
# Points to the directory one level above your current project folder
DB_PATH = "./chroma_data" 
COLLECTION_NAME = "health_claims"

def export_for_projector():
    try:
        # 1. Path Verification
        full_path = os.path.abspath(DB_PATH)
        if not os.path.exists(full_path):
            print(f"Error: Database path not found at {full_path}")
            return

        # 2. Connect to Chroma
        # We include allow_reset=True just in case your config requires it
        client = chromadb.PersistentClient(
            path=full_path,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        
        collection = client.get_collection(name=COLLECTION_NAME)
        
        print(f"Connected to: {full_path}")
        print(f"Fetching data from '{COLLECTION_NAME}'...")
        
        # 3. Fetch data
        results = collection.get(include=['embeddings', 'metadatas', 'documents'])
        
        ids = results.get('ids', [])
        embeddings = results.get('embeddings', [])
        metadatas = results.get('metadatas', [])
        documents = results.get('documents', [])

        if embeddings is None or len(embeddings) == 0:
            print("No embeddings found in this collection.")
            return

        # 4. Export Vectors TSV
        with open('vectors.tsv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            for vector in embeddings:
                writer.writerow(vector)
        
        # 5. Export Metadata TSV
        with open('metadata.tsv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            
            if metadatas:
                # Use keys from first record, add Document_Text for reference
                headers = list(metadatas[0].keys()) + ['Document_Text']
                writer.writerow(headers)
                
                for i in range(len(ids)):
                    meta_values = [metadatas[i].get(h, "") for h in headers[:-1]]
                    row_data = meta_values + [documents[i]]
                    writer.writerow(row_data)

        print(f"Done! Exported {len(ids)} records to vectors.tsv and metadata.tsv")

    except Exception as e:
        _, _, tb = sys.exc_info()
        line = traceback.extract_tb(tb)[-1][1]
        print(f"Export Error on line {line}: {e}")

if __name__ == "__main__":
    export_for_projector()