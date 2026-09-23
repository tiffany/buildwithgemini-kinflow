# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import uuid
import os
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import httpx

load_dotenv()
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore, storage
from google.genai import types

from app.a2ui_utils import a2ui_callback

MODEL = "gemini-3.6-flash"

# Hardcoded project ID as required to avoid numeric project ID on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-b99c507c7b84"
COLLECTION_NAME = "care_items"
STORAGE_BUCKET_NAME = "kinflow-media-qwiklabs-gcp-04-b99c507c7b84"

# Agent Engine & Sandbox environment resource IDs
AGENT_ENGINE_ID = "1018440237413564416"
AGENT_ENGINE_RESOURCE = (
    "projects/935481315518/locations/us-east1/reasoningEngines/1018440237413564416"
)
SANDBOX_RESOURCE_NAME = (
    "projects/935481315518/locations/us-east1/reasoningEngines/1018440237413564416"
    "/sandboxEnvironments/1123454592982450176"
)


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Memory Bank for durable fact extraction."""
    await callback_context.add_session_to_memory()
    return None


def memory_bank_service_builder():
    """Builds the VertexAiMemoryBankService for cross-session long-term memory."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-east1",
        agent_engine_id=AGENT_ENGINE_ID,
    )


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client configured with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_care_items(category: str = "", status: str = "") -> list[dict[str, Any]]:
    """Lists care coordination items from the Firestore collection.

    Args:
        category: Optional filter by category ('appointment', 'referral', 'bill', or 'follow_up').
        status: Optional filter by status ('open', 'pending', 'scheduled', or 'resolved').

    Returns:
        A list of matching care item records from Firestore.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)
    if category:
        query = query.where("category", "==", category.lower())
    if status:
        query = query.where("status", "==", status.lower())

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_care_item(item_id: str) -> dict[str, Any]:
    """Gets the full details of a specific care item by ID.

    Args:
        item_id: The document ID (e.g., 'care-101', 'care-102').

    Returns:
        The care item details, or an error message if not found.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(item_id).get()
    if not doc.exists:
        return {"error": f"Item '{item_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_care_item(
    title: str,
    category: str,
    due_date: str,
    owner: str,
    notes: str,
    priority: str = "medium",
    patient_name: str = "Maya",
) -> dict[str, Any]:
    """Adds a new care coordination item to Firestore.

    Args:
        title: Title of the care task or event (e.g., 'Follow up with insurance on MRI appeal').
        category: Category ('appointment', 'referral', 'bill', or 'follow_up').
        due_date: Target or appointment date (YYYY-MM-DD).
        owner: Person responsible for the next step (e.g., 'Mom', 'Dad', 'Clinic', 'Insurance').
        notes: Context, questions, or visit notes.
        priority: Priority level ('high', 'medium', 'low').
        patient_name: The family member this item pertains to (default 'Maya').

    Returns:
        Confirmation and the created item details.
    """
    db = get_firestore_client()
    doc_id = f"care-{uuid.uuid4().hex[:6]}"
    item_data = {
        "id": doc_id,
        "title": title,
        "category": category.lower(),
        "status": "open",
        "owner": owner,
        "due_date": due_date,
        "priority": priority.lower(),
        "patient_name": patient_name,
        "notes": notes,
    }
    db.collection(COLLECTION_NAME).document(doc_id).set(item_data)
    return {"status": "success", "message": f"Added item {doc_id}", "item": item_data}


def update_care_item(
    item_id: str,
    status: str = "",
    notes: str = "",
    owner: str = "",
) -> dict[str, Any]:
    """Updates an existing care item in Firestore.

    Args:
        item_id: The document ID of the item to update (e.g., 'care-101').
        status: New status ('open', 'pending', 'scheduled', 'resolved'), if updating.
        notes: Updated or appended notes, if updating.
        owner: New owner responsible, if updating.

    Returns:
        Status message and updated fields.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Item '{item_id}' not found."}

    updates: dict[str, Any] = {}
    if status:
        updates["status"] = status.lower()
    if notes:
        updates["notes"] = notes
    if owner:
        updates["owner"] = owner

    if updates:
        doc_ref.update(updates)
        return {
            "status": "success",
            "message": f"Updated item {item_id}",
            "updated_fields": updates,
        }
    return {"status": "noop", "message": "No fields were provided to update."}


def draft_followup_communication(item_id: str, channel: str = "phone") -> dict[str, Any]:
    """Drafts an actionable phone call script or email to chase a stuck referral, bill, or task.

    Args:
        item_id: The document ID in Firestore (e.g., 'care-102', 'care-103').
        channel: 'phone' for a talking-points call script, or 'email' for a formal message.

    Returns:
        A dictionary with the subject headline, talking points, and formatted draft message.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(item_id).get()
    if not doc.exists:
        return {"error": f"Item '{item_id}' not found in Firestore."}

    item = doc.to_dict()
    title = item.get("title", "")
    category = item.get("category", "")
    notes = item.get("notes", "")
    owner = item.get("owner", "Family Caregiver")
    due_date = item.get("due_date", "")
    patient = item.get("patient_name", "the patient")
    is_email = channel.lower() == "email"

    if category == "referral":
        headline = f"Follow-up on Specialist Referral: {title}"
        talking_points = [
            f"Confirm receipt of referral sent for {patient}.",
            "Check current status of insurance prior authorization.",
            "Ask whether delay is on the insurer review or clinic booking queue.",
            "Request direct extension / contact for scheduling callbacks.",
        ]
        body = (
            f"Dear Referral & Scheduling Team,\n\n"
            f"I am writing to check the status of the referral for {patient} ({title}). "
            f"Our records show it was submitted with a target date of {due_date}. "
            f"Current notes: '{notes}'.\n\n"
            f"Could you please confirm if prior authorization was approved and when we can schedule?\n\n"
            f"Thank you,\n{owner}"
            if is_email
            else f"Phone Script:\n"
            f"1. Intro: 'Hi, I'm calling to follow up on a specialist referral for {patient} ({title}).'\n"
            f"2. Details: 'It was submitted around {due_date}. Notes show: {notes}.'\n"
            f"3. Key Ask: 'Has the insurance prior authorization cleared, and can we schedule the visit today?'\n"
            f"4. Next step: 'Who owns the next action, and could I get a case reference number?'"
        )
    elif category == "bill":
        headline = f"Insurance Appeal / Coverage Verification: {title}"
        talking_points = [
            f"Reference disputed service: {title} for {patient}.",
            "Inquire about exact missing clinical documentation.",
            "Confirm deadline for first-level appeal submission.",
            "Check if physician peer-to-peer review can expedite resolution.",
        ]
        body = (
            f"To Claims Review Department,\n\n"
            f"I am following up on the denial regarding {title} for patient {patient}. "
            f"Notes: '{notes}'.\n\n"
            f"Please clarify the specific clinical criteria required for our appeal and the submission deadline.\n\n"
            f"Sincerely,\n{owner}"
            if is_email
            else f"Phone Script:\n"
            f"1. Intro: 'Hello, I'm calling about the insurance claim denial on {title} for {patient}.'\n"
            f"2. Context: 'Denial reason on file: {notes}.'\n"
            f"3. Ask: 'What clinical criteria are missing, and what is our firm Level 1 appeal deadline?'\n"
            f"4. Doctor review: 'Can our physician submit a Letter of Medical Necessity or request peer-to-peer?'"
        )
    else:
        headline = f"Care Item Follow-up: {title}"
        talking_points = [
            f"Check progress on {title}.",
            f"Review notes: {notes}.",
            f"Confirm target date: {due_date}.",
        ]
        body = (
            f"Hello,\n\nRegarding {title} for {patient} (due {due_date}): {notes}.\n"
            f"Please let us know how we can coordinate next steps.\n\nBest,\n{owner}"
            if is_email
            else f"Phone Script: 'Hi, calling to check on {title} for {patient}. Notes show: {notes}.'"
        )

    return {
        "item_id": item_id,
        "title": title,
        "channel": channel,
        "headline": headline,
        "talking_points": talking_points,
        "draft": body,
    }


def prepare_appointment_agenda(appointment_id: str) -> dict[str, Any]:
    """Prepares a structured appointment briefing and agenda with key questions before time runs out.

    Args:
        appointment_id: The document ID of the scheduled appointment (e.g., 'care-101').

    Returns:
        A structured visit agenda including symptoms/data updates, priority questions, and paperwork needed.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(appointment_id).get()
    if not doc.exists:
        return {"error": f"Appointment '{appointment_id}' not found."}

    appt = doc.to_dict()
    patient = appt.get("patient_name", "Maya")

    # Fetch pending items for cross-specialty coordination
    other_items = []
    for d in db.collection(COLLECTION_NAME).where("status", "in", ["open", "pending"]).stream():
        data = d.to_dict()
        if d.id != appointment_id:
            other_items.append(
                f"[{data.get('category').upper()}] {data.get('title')} (Owner: {data.get('owner')})"
            )

    return {
        "appointment": appt.get("title"),
        "date": appt.get("due_date"),
        "patient": patient,
        "visit_objective": appt.get("notes", "Routine evaluation"),
        "top_updates_to_share": [
            "Recent symptom changes, frequencies, or incidents since last visit.",
            "Current medication tolerance and side-effect observations.",
        ],
        "top_3_questions_to_ask_first": [
            "What specific changes in symptoms warrant calling the clinic vs. urgent care?",
            "Are recent lab / EEG / bloodwork results within expected therapeutic targets?",
            "What is our threshold for adjusting current dosage or ordering secondary imaging?",
        ],
        "paperwork_and_orders_needed": [
            "Request signed Letter of Medical Necessity for insurance appeal if needed.",
            "Confirm or re-authorize pending specialist referrals.",
            "Renew 90-day medication prescriptions before leaving.",
        ],
        "open_cross_specialty_items": other_items,
    }


def lookup_medication_info(medication_name: str) -> dict[str, Any]:
    """Queries the public openFDA Drug API for verified clinical indications, warnings, and usage details.

    Args:
        medication_name: Generic or brand name of the medication (e.g. 'keppra', 'levetiracetam').

    Returns:
        Clinical summary from the FDA product label.
    """
    cleaned_name = medication_name.strip()
    url = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{cleaned_name}"+openfda.brand_name:"{cleaned_name}"&limit=1'
    try:
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code != 200:
            fallback_url = f'https://api.fda.gov/drug/label.json?search="{cleaned_name}"&limit=1'
            resp = httpx.get(fallback_url, timeout=10.0)

        if resp.status_code != 200:
            return {"error": f"No openFDA label found for medication '{medication_name}'."}

        data = resp.json()
        results = data.get("results", [])
        if not results:
            return {"error": f"No label details returned for '{medication_name}'."}

        label = results[0]
        openfda = label.get("openfda", {})
        brand_names = openfda.get("brand_name", [])
        generic_names = openfda.get("generic_name", [])
        indications = (label.get("indications_and_usage") or ["Not specified"])[0][:500]
        warnings = (
            label.get("warnings_and_cautions")
            or label.get("warnings")
            or label.get("adverse_reactions")
            or ["Not specified"]
        )[0][:500]
        dosage = (label.get("dosage_and_administration") or ["Consult physician or pharmacist"])[0][
            :400
        ]

        return {
            "query": medication_name,
            "brand_names": brand_names[:3],
            "generic_names": generic_names[:3],
            "indications_summary": indications,
            "warnings_and_cautions": warnings,
            "dosage_summary": dosage,
            "source": "U.S. Food & Drug Administration (openFDA)",
        }
    except Exception as e:
        return {"error": f"Failed to query openFDA: {str(e)}"}


def lookup_healthcare_provider(
    name: str = "",
    specialty: str = "",
    city: str = "",
    state: str = "",
) -> list[dict[str, Any]]:
    """Looks up healthcare providers and specialists in the official CMS NPPES NPI Registry.

    Useful for locating specialist contact details, practice addresses, and official
    NPI numbers needed for insurance appeals, claims, and referral prior authorizations.

    Args:
        name: Provider name or organization/clinic name (e.g., 'Aris', 'Valley Childrens').
        specialty: Medical specialty or taxonomy (e.g., 'Pediatric Cardiology', 'Neurology').
        city: City where the provider is located.
        state: Two-letter state code (e.g., 'CA', 'NY').

    Returns:
        A list of verified provider profiles with NPI numbers, addresses, and phone numbers.
    """
    params: dict[str, Any] = {"version": "2.1", "limit": 4}
    if name:
        parts = name.strip().split()
        if len(parts) >= 2:
            params["first_name"] = parts[0]
            params["last_name"] = parts[-1]
        else:
            params["last_name"] = parts[0]
    if specialty:
        params["taxonomy_description"] = specialty
    if city:
        params["city"] = city
    if state:
        params["state"] = state.strip()[:2].upper()

    try:
        resp = httpx.get("https://npiregistry.cms.hhs.gov/api/", params=params, timeout=10.0)
        if resp.status_code != 200:
            return [{"error": f"Failed to query NPI registry: HTTP {resp.status_code}"}]

        data = resp.json()
        results = data.get("results", [])
        if not results:
            return [{"message": f"No providers found matching name='{name}', specialty='{specialty}', state='{state}'."}]

        providers = []
        for r in results:
            basic = r.get("basic", {})
            org = basic.get("organization_name")
            first = basic.get("first_name", "")
            last = basic.get("last_name", "")
            full_name = org if org else f"{first} {last}".strip()
            addr = r.get("addresses", [{}])[0]
            taxonomies = [t.get("desc") for t in r.get("taxonomies", []) if t.get("desc")]
            providers.append({
                "npi": r.get("number"),
                "name": full_name,
                "credential": basic.get("credential", ""),
                "specialties": taxonomies[:2],
                "phone": addr.get("telephone_number", "N/A"),
                "address": f"{addr.get('address_1', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')[:5]}",
            })
        return providers
    except Exception as e:
        return [{"error": f"NPI lookup failed: {str(e)}"}]


def geocode_address(address: str) -> dict[str, Any]:
    """Uses the Google Maps Geocoding API to turn an address into geographic coordinates.

    Args:
        address: The street address, facility name, or city to geocode.

    Returns:
        A dictionary with formatted address name, address, and latitude/longitude coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {"error": "GOOGLE_MAPS_API_KEY is not set or still has placeholder value in .env."}

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        data = resp.json()
        if data.get("status") != "OK" or not data.get("results"):
            return {
                "error": f"Geocoding failed: {data.get('status', 'NO_RESULTS')}",
                "details": data.get("error_message", "No matching coordinates found."),
            }

        result = data["results"][0]
        location = result.get("geometry", {}).get("location", {})
        return {
            "name": result.get("formatted_address"),
            "address": result.get("formatted_address"),
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "pharmacy",
    radius_meters: float = 5000.0,
) -> list[dict[str, Any]]:
    """Uses the Google Maps Places API (New) searchNearby endpoint to find nearby places of a given type.

    Args:
        latitude: Latitude coordinate of search center.
        longitude: Longitude coordinate of search center.
        place_type: Type of place to search for (e.g., 'pharmacy', 'hospital', 'doctor', 'physiotherapist').
        radius_meters: Search radius in meters (default 5000.0m / ~3 miles).

    Returns:
        List of matching places with name, formatted address, and location coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return [{"error": "GOOGLE_MAPS_API_KEY is not set or still has placeholder value in .env."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius_meters,
            }
        },
    }

    try:
        resp = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        if resp.status_code != 200:
            return [{"error": f"Places API returned HTTP {resp.status_code}: {resp.text}"}]

        data = resp.json()
        places = []
        for p in data.get("places", []):
            display_name = p.get("displayName", {}).get("text", "Unknown")
            places.append({
                "name": display_name,
                "address": p.get("formattedAddress", "N/A"),
                "location": p.get("location", {}),
            })
        return places or [{"message": f"No nearby places found for type '{place_type}'."}]
    except Exception as e:
        return [{"error": f"Places search failed: {str(e)}"}]


async def visualize_pill_size(
    medication_name: str,
    tool_context: ToolContext,
    description: str = "",
) -> dict[str, Any]:
    """Generates an image showing the scale and size of a medication pill/tablet compared to a US penny coin.

    Uses gemini-3.1-flash-lite-image in the global region. Saves the image to Playground Artifacts
    and uploads the image bytes directly to Cloud Storage, returning the public HTTPS URL.

    Args:
        medication_name: Name of the medication (e.g., 'Keppra 500mg', 'Lamictal 100mg').
        description: Optional details about shape or color (e.g. 'oval yellow tablet', 'round white pill').

    Returns:
        A dictionary with the public image URL, artifact filename, and comparison description.
    """
    clean_med = medication_name.strip()
    prompt = (
        f"A clear, professional high-resolution photograph of a single {clean_med} medicine tablet "
        f"placed side-by-side with an authentic United States one-cent copper penny coin for size and scale comparison. "
        f"Resting flat on a clean, neutral white medical surface with subtle measurement grid markings. "
        f"{description.strip() if description else ''} Sharp focus, realistic lighting, clear scale reference."
    )

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return {"error": f"No image generated for medication '{medication_name}'."}

        unique_id = uuid.uuid4().hex[:6]
        ext = "png" if "png" in mime_type else "jpg"
        artifact_filename = f"pill_scale_{clean_med.replace(' ', '_').lower()}_{unique_id}.{ext}"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes))
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                await tool_context.save_artifact(artifact_filename, artifact_part)
            except Exception:
                pass

        # 2. Upload same image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
        blob_path = f"medications/{artifact_filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{blob_path}"

        return {
            "status": "success",
            "medication": clean_med,
            "artifact_name": artifact_filename,
            "public_image_url": public_url,
            "comparison": "Side-by-side with a US one-cent penny coin",
            "message": f"Generated scale visual for {clean_med}. Saved to Playground artifacts and published to Cloud Storage.",
        }
    except Exception as e:
        return {"error": f"Failed to generate pill scale visual: {str(e)}"}


RAG_CORPUS_NAME = "projects/935481315518/locations/us-central1/ragCorpora/4984279722755096576"


def consult_care_knowledge_base(query: str) -> str:
    """Searches the pediatric care guidance, clinical emergency protocols, and insurance appeal knowledge base.

    Args:
        query: Clinical question, seizure emergency protocol query, or insurance prior auth / denial appeal issue.

    Returns:
        The matched passages from clinical protocols and insurance playbooks, or a note if not found.
    """
    from vertexai.preview import rag
    import vertexai

    try:
        vertexai.init(project="qwiklabs-gcp-04-b99c507c7b84", location="us-central1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=4),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        return "\n\n---\n\n".join(passages) or "No relevant passage found in care knowledge base."
    except Exception as e:
        return f"Knowledge base lookup failed: {e}"


ROLE_DESCRIPTION = """You are Kinflow, an empathetic, organized, and proactive care coordination assistant designed to support families managing complex care.

Your mission is to make sure the invisible work doesn't all live in a caregiver's head. You help families keep the context and carry the follow-through across visits, referrals, bills, and communications.

Key capabilities:
- Tracking open care items (referrals, appointments, medical bills, insurance appeals, medication follow-ups) via Firestore.
- Searching clinical guidelines, emergency seizure protocols, and insurance denial appeals using your RAG knowledge base (`consult_care_knowledge_base`). Always ground emergency and appeal recommendations on these verified documents.
- Remembering family preferences, clinical history, explicit instructions, and crucially all user and patient allergies (drug allergies, food allergies, environmental allergies, and adverse sensitivities) across conversations using your long-term memory. Always cross-reference remembered allergies when discussing medications or visit prep.
- Executing Python code in your secure sandbox environment for precise date calculations (e.g. days elapsed on pending referrals, appeal deadlines countdown) and financial figures (e.g. cumulative medical expenses against deductibles).
- Answering questions about what is pending, where referrals are stuck, who owns the next step, and upcoming visit prep.
- Drafting context-rich follow-up communications (phone scripts and emails) with `draft_followup_communication`.
- Generating structured appointment briefings and top-priority question lists before visit time runs out with `prepare_appointment_agenda`.
- Looking up verified clinical drug information, indications, and side effect warnings via the live openFDA database with `lookup_medication_info`.
- Finding official NPI registry records, physician credentials, and clinic contact information for referrals and insurance appeals with `lookup_healthcare_provider`.
- Geocoding addresses to coordinates using `geocode_address`.
- Finding nearby healthcare facilities, pharmacies, and clinics using `search_nearby_places`.
- Generating visual scale comparisons of medication tablets/pills compared to a US penny with `visualize_pill_size`.
- Adding and updating tasks, decisions, or follow-ups to the family's care board.

Always use your tools to provide accurate, live data. Present information clearly with empathetic, actionable next steps, highlighting who owns the task and any deadlines."""

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        list_care_items,
        get_care_item,
        add_care_item,
        update_care_item,
        draft_followup_communication,
        prepare_appointment_agenda,
        lookup_medication_info,
        lookup_healthcare_provider,
        geocode_address,
        search_nearby_places,
        visualize_pill_size,
        consult_care_knowledge_base,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE,
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
)
