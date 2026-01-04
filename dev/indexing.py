import json
import os
import sys
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# 1. Setup Nomic Embedding via Ollama
nomic_ef = embedding_functions.OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434/api/embeddings"
)


# 2. Connect to Chroma (HttpClient) - UPDATED TO MATCH YOUR COMPOSE
client = chromadb.HttpClient(
    host='localhost', 
    port=8000,
    tenant='default_tenant',     # <--- MATCHES YOUR COMPOSE
    database='default_database', # <--- MATCHES YOUR COMPOSE
    settings=Settings(chroma_api_impl="chromadb.api.fastapi.FastAPI")
)

collection = client.get_or_create_collection(
    name="health_claims",
    embedding_function=nomic_ef
)

def index_rich_claims(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    print(f"Indexing {len(files)} rich claims...")
    try:
        for filename in files:
            with open(os.path.join(folder_path, filename), 'r') as f:
                claim = json.load(f)
                print(filename)
                # Extract basic text for vector search (the "Document")
                try:
                    extensions = claim.get("patient", {}).get("extension", [{}])
        
                    # 1. Extract Sex (handling both valueCode and potential case issues)
                    sex_map = {"M": "male", "F": "female", "UNK": "unknown"}
                    raw_sex = "unknown"
                    for ext in extensions:
                        print(ext)
                        if "us-core-birthsex" in ext.get("url", "").lower():
                            raw_sex = ext.get("valueCode", "unknown")
                            break
                    patient_sex = sex_map.get(raw_sex, "unknown")
                    print(patient_sex)

                    # 2. Extract Age (Targeting valueInteger)
                    patient_age = "unknown"
                    for ext in extensions:
                        
                        if "patient-age" in ext.get("url", "").lower():
                            print(ext)
                            # Check specifically for valueInteger as you identified
                            if "valueInteger" in ext:
                                patient_age = ext["valueInteger"]
                            # Fallback just in case some records differ
                            elif "valueQuantity" in ext:
                                patient_age = ext["valueQuantity"]["value"]
                            break
                    print(patient_age)
                    patient = claim.get('patient', {}).get('display', 'Unknown')
                    diagnosis = claim.get('diagnosis', [{}])[0].get('diagnosisCodeableConcept', {}).get('coding', [{}])[0].get('display', 'No Diagnosis')
                    diagnosis_code = claim.get('diagnosis', [{}])[0].get('diagnosisCodeableConcept', {}).get('coding', [{}])[0].get('code', 'No Code')
                    provider = claim.get('provider', {}).get('display', 'Unknown')
                    procedure = claim.get('procedure', [{}])[0].get('procedureCodeableConcept', {}).get('coding', [{}])[0].get('display', 'No Procedure')
                    procedure_code = claim.get('procedure', [{}])[0].get('procedureCodeableConcept', {}).get('coding', [{}])[0].get('code', 'No Code')
                    item = claim.get('item', [{}])[0].get('productOrService', {}).get('coding', [{}])[0].get('display', 'No Item')
                    item_code = claim.get('item', [{}])[0].get('productOrService', {}).get('coding', [{}])[0].get('code', 'No Code')
                    itemPrice = claim.get('item', [{}])[0].get('unitPrice', {}).get('value', 0.0)
                    itemCurrency = claim.get('item', [{}])[0].get('unitPrice', {}).get('currency', 'No currency')
                    insurer = claim.get('insurer', {}).get('display', 'Unknown')
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
    
                    # Extract the line number specifically
                    line_number = exc_traceback.tb_lineno
                    print(f"Error extracting fields from claim {claim.get('id')}")
                    print(f"Exception Type: {exc_type}, Value: {exc_value}, Line: {line_number}")

                summary = f"Claim for {patient} {patient_age} {patient_sex}. Diagnosis: {diagnosis}. Provider: {provider}."
                print(summary)
                # 3. EXTENDED METADATA: Indexing multiple specific fields
                # You can add as many keys here as you want!
                meta = {
                    "patient_name": patient,
                    "patient_sex": patient_sex,
                    "patient_age": patient_age,
                    "diagnosis": diagnosis,
                    "diagnosis_code": diagnosis_code,
                    "procedure": procedure,
                    "procedure_code": procedure_code,
                    "item": item,
                    "item_price": float(itemPrice),
                    "provider_name": provider,
                    "insurer_name": insurer,
                    "claim_id": str(claim.get('id')),
                    "date": claim.get('created', '2000-01-01'),
                    "status": claim.get('status', 'active')
                }
        

            collection.add(
                documents=[summary],
                ids=[str(claim['id'])],
                metadatas=[meta]
            )
    except Exception as e:
        print(f"Error indexing claim {claim.get('id')}: {e}")

    print(f"Finished! {collection.count()} claims indexed with rich metadata.")

index_rich_claims("../../generated_claims")