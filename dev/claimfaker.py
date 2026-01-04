import json
import os
import random
from faker import Faker

fake = Faker()

# Configuration
NUM_CLAIMS = 500
OUTPUT_DIR = "generated_claims"

# Sample Data Pools for Variety
DIAGNOSES = [
    {"code": "I10", "display": "Essential (primary) hypertension"},
    {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"},
    {"code": "M54.50", "display": "Low back pain, unspecified"},
    {"code": "J45.909", "display": "Unspecified asthma, uncomplicated"},
    {"code": "K21.9", "display": "Gastro-esophageal reflux disease without esophagitis"}
]

PROCEDURES = [
    {"code": "99213", "display": "Office visit, established patient, 20-29 min"},
    {"code": "99214", "display": "Office visit, established patient, 30-39 min"},
    {"code": "36415", "display": "Collection of venous blood by venipuncture"},
    {"code": "80053", "display": "Comprehensive metabolic panel"},
    {"code": "93000", "display": "Electrocardiogram, routine ECG with at least 12 leads"}
]

INSURERS = ["BlueCross BlueShield", "Aetna", "UnitedHealthcare", "Cigna", "Kaiser Permanente"]
PROVIDERS = ["Dr. Sarah Jenkins", "Dr. James Miller", "Dr. Elena Rodriguez", "Dr. Michael Chen"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_claim(index):
    diag = random.choice(DIAGNOSES)
    proc = random.choice(PROCEDURES)
    
    claim = {
        "resourceType": "Claim",
        "id": f"claim-2026-{index:03d}",
        "status": "active",
        "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/claim-type", "code": "professional"}]},
        "use": "claim",
        "patient": {
            "display": fake.name(),
            "extension": [
                {"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", "valueCode": random.choice(["M", "F"])},
                {"url": "http://example.org/fhir/StructureDefinition/patient-age", "valueInteger": random.randint(18, 85)}
            ]
        },
        "created": "2026-01-02",
        "insurer": {"display": random.choice(INSURERS)},
        "provider": {"display": random.choice(PROVIDERS)},
        "diagnosis": [{"sequence": 1, "diagnosisCodeableConcept": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", **diag}]}}],
        "procedure": [{"sequence": 1, "procedureCodeableConcept": {"coding": [{"system": "http://www.ama-assn.org/go/cpt", **proc}]}}],
        "item": [{
            "sequence": 1,
            "productOrService": {"coding": [{"system": "http://www.ama-assn.org/go/cpt", **proc}]},
            "unitPrice": {"value": float(random.randint(150, 1200)), "currency": "USD"}
        }]
    }
    return claim

print(f"Generating {NUM_CLAIMS} claims...")
for i in range(1, NUM_CLAIMS + 1):
    file_path = os.path.join(OUTPUT_DIR, f"claim_{i:03d}.json")
    with open(file_path, "w") as f:
        json.dump(generate_claim(i), f, indent=2)
