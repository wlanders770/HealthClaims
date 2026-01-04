import chromadb
import ollama
import uuid
import random

# 1. SETUP CHROMADB (Standard Persistence)
client = chromadb.PersistentClient(path="./fhir_claims_db")
collection = client.get_or_create_collection(name="healthcare_claims")

# 2. CONFIGURATION DATA
DIAGNOSES = [
    {"code": "I10", "display": "Essential hypertension", "cat": "Cardiology"},
    {"code": "E11.9", "display": "Type 2 diabetes mellitus", "cat": "Endocrinology"},
    {"code": "M54.5", "display": "Low back pain", "cat": "Orthopedics"},
    {"code": "J45.909", "display": "Unspecified asthma", "cat": "Pulmonology"},
    {"code": "F41.1", "display": "Generalized anxiety disorder", "cat": "Psychiatry"}
]

PROVIDERS = [
    "Dr. Alice Smith (NPI: 12345)",
    "Dr. Bob Johnson (NPI: 67890)",
    "General Health Clinic (NPI: 55443)",
    "City Memorial Hospital (NPI: 99887)"
]

# 3. TEXTUALIZER (Turns JSON into a searchable story)
def textualize(claim):
    """Converts a FHIR-like dict into a narrative for the vector DB."""
    patient = claim['patient']['display']
    provider = claim['provider']['display']
    dx = claim['diagnosis'][0]['display']
    total = claim['total']['value']
    
    return (f"Medical claim for {patient}. "
            f"Primary Diagnosis: {dx}. "
            f"Service provided by {provider}. "
            f"Total bill amount: ${total}.")

# 4. GENERATOR & LOADER
print(f"🚀 Environment: Python 3.12 detected. Starting Load...")

for i in range(1000):
    # Randomly select data
    dx_choice = random.choice(DIAGNOSES)
    provider_choice = random.choice(PROVIDERS)
    claim_id = str(uuid.uuid4())[:8]
    amount = random.randint(150, 2500)
    
    # Construct FHIR-like Dictionary
    claim_data = {
        "resourceType": "Claim",
        "id": f"claim-{claim_id}",
        "status": "active",
        "patient": {"display": f"Patient-{random.randint(1000, 9999)}"},
        "provider": {"display": provider_choice},
        "diagnosis": [{"code": dx_choice['code'], "display": dx_choice['display']}],
        "total": {"value": amount, "currency": "USD"}
    }

    # Generate Narrative and Embedding
    narrative = textualize(claim_data)
    
    # Using Ollama to create the vector
    # Ensure 'ollama run nomic-embed-text' was performed once before running this
    response = ollama.embeddings(model="nomic-embed-text", prompt=narrative)
    
    # Add to Chroma
    collection.add(
        ids=[claim_data["id"]],
        embeddings=[response["embedding"]],
        documents=[narrative],
        metadatas={
            "dx_code": dx_choice['code'],
            "provider": provider_choice,
            "category": dx_choice['cat'],
            "cost": amount
        }
    )

    if (i + 1) % 100 == 0:
        print(f"✅ Indexed {i + 1}/1000 claims...")

print("\n✨ Database ready! All 1,000 claims are now searchable.")