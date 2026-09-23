"""Seed Firestore with initial care items for Kinflow."""

from google.cloud import firestore

# Hardcoded project ID as required to avoid numeric project ID on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-b99c507c7b84"
COLLECTION_NAME = "care_items"

SEED_ITEMS = [
    {
        "id": "care-101",
        "title": "Dr. Aris (Neurology) 6-Month Review",
        "category": "appointment",
        "status": "scheduled",
        "owner": "Mom",
        "due_date": "2026-10-05",
        "priority": "high",
        "patient_name": "Maya",
        "notes": "Agenda: Discuss dizzy spells, review bloodwork, check EEG results before time runs out.",
    },
    {
        "id": "care-102",
        "title": "Pediatric Cardiology Referral - Valley Children's",
        "category": "referral",
        "status": "pending",
        "owner": "Dr. Aris Office",
        "due_date": "2026-09-28",
        "priority": "high",
        "patient_name": "Maya",
        "notes": "Referral sent 10 days ago. Call clinic to verify if insurance authorization is stuck.",
    },
    {
        "id": "care-103",
        "title": "Out-of-Network MRI Claim Denial ($1,450)",
        "category": "bill",
        "status": "open",
        "owner": "Dad",
        "due_date": "2026-10-15",
        "priority": "high",
        "patient_name": "Maya",
        "notes": "Denied as not pre-authorized. Need letter of medical necessity to file first-level appeal.",
    },
    {
        "id": "care-104",
        "title": "Refill Levetiracetam (Keppra) 500mg",
        "category": "follow_up",
        "status": "open",
        "owner": "Mom",
        "due_date": "2026-09-30",
        "priority": "medium",
        "patient_name": "Maya",
        "notes": "5 days of medication left. Call pharmacy for 90-day mail order authorization.",
    },
]


def seed():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connected to Firestore project: {PROJECT_ID}")
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_ITEMS:
        doc_id = item["id"]
        collection_ref.document(doc_id).set(item)
        print(f"Seeded {doc_id}: {item['title']} [{item['category']} / {item['status']}]")

    print(f"\nSuccessfully seeded {len(SEED_ITEMS)} items into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
