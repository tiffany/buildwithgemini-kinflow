# Kinflow: Care Coordination Agent for Families Managing Complex Care

**Kinflow** is an intelligent, compassionate care coordination agent designed for families managing complex pediatric medical care. Built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Engine**, Kinflow helps caregivers keep track of appointments, follow up on pending referrals, appeal denied insurance claims, and access critical clinical protocols and clinical information.

---

## 🌟 What We Built & Connected

Kinflow orchestrates **7 Google Cloud & AI capabilities** into a unified experience:

1. **Vertex AI Agent Engine (Runtime)**: Deployed ADK agent serving requests over the **A2A (Agent-to-Agent) Protocol**.
2. **Vertex AI Memory Bank**: Cross-session long-term memory remembering patient history, clinical alerts, and drug allergies across conversations.
3. **Vertex AI Serverless RAG Engine**: Grounded semantic retrieval over clinical seizure emergency protocols and insurance appeal playbooks.
4. **Google Cloud Firestore**: Real-time database for managing care action items, specialist appointments, and referral statuses.
5. **Gemini Imagen Image Generation (`gemini-3.1-flash-lite-image`)**: Generates pill size and shape comparisons relative to a US penny, hosted on **Google Cloud Storage**.
6. **Healthcare & Geospatial Public APIs**:
   - **openFDA API**: Live FDA drug labels, black-box warnings, and pediatric dosing.
   - **CMS NPPES Registry**: Verification of doctor NPI numbers, medical specialties, and clinic addresses.
   - **Google Maps API**: Geocoding and Nearby Places search for clinics and pharmacies.
7. **Adaptive Agent UI (A2UI v0.8)**: Generates structured UI surfaces rendered natively in a custom **Cloud Run Web Chat Frontend**.

---

## 🎯 Step-by-Step Demo Script (Try These Prompts!)

To experience the full power of Kinflow and see each connected service in action, follow this guided walkthrough:

### 1. The Care Action Board (Firestore + A2UI)
* **Prompt to Try**:
  > *"Hello Kinflow! What care tasks and appointments are currently open for Maya?"*
* **What Happens Under the Hood**:
  Kinflow queries Cloud Firestore via `list_care_items` and formats the active care tasks into an **A2UI Card Component** with title headers, priorities, and owners.
* **What You See**:
  An interactive, styled visual card displaying Maya's open neurology appointment, pending cardiology referral, and an unresolved MRI claim denial.

---

### 2. Emergency Protocol Retrieval (Vertex AI Serverless RAG)
* **Prompt to Try**:
  > *"What is the emergency rescue protocol if Maya's seizure lasts longer than 5 minutes?"*
* **What Happens Under the Hood**:
  Kinflow queries the **Vertex AI Serverless RAG Engine** corpus (`consult_care_knowledge_base`) containing clinical pediatric epilepsy guidelines.
* **What You See**:
  A step-by-step emergency action plan: positioning Maya safely, administering prescribed rescue medication (intranasal midazolam / rectal diazepam), and when to call 911.

---

### 3. Cross-Session Clinical Memory & Allergy Safety (Vertex AI Memory Bank)
* **Prompt to Try**:
  > *"Please remember that Maya has a severe anaphylactic allergy to Penicillin and Amoxicillin."*
* **What Happens Under the Hood**:
  The memory callback saves this critical health constraint into the **Vertex AI Memory Bank**.
* **Follow-up Prompt (Testing Memory Retention)**:
  > *"Maya has an ear infection. Can the urgent care doctor prescribe Augmentin?"*
* **What You See**:
  Kinflow retrieves the allergy from long-term memory and **warns against Augmentin**, explaining that Augmentin contains amoxicillin and clavulanate, recommending cephalosporin or macrolide alternatives for the pediatrician to consider.

---

### 4. Real FDA Drug Intelligence & Pill Scale (openFDA + Gemini Imagen)
* **Prompt to Try**:
  > *"Can you look up Keppra in the FDA registry and show me what a 500mg pill looks like compared to a coin?"*
* **What Happens Under the Hood**:
  1. Queries the **openFDA Drug API** for verified indications, adverse effects, and warnings.
  2. Calls **Gemini Imagen** (`visualize_pill_size`) to generate a realistic scale image of an oval yellow Keppra 500mg tablet next to a US penny coin.
  3. Uploads the image to Cloud Storage and renders the image inline.
* **What You See**:
  Clinical warnings and a side-by-side visual pill comparison so caregivers know what pill to expect.

---

### 5. Healthcare Provider & Pharmacy Discovery (CMS NPPES + Google Maps)
* **Prompt to Try**:
  > *"Look up Dr. Aris in neurology, find his practice address, and locate the nearest 24-hour pharmacy."*
* **What Happens Under the Hood**:
  1. Calls `lookup_healthcare_provider` via the **CMS NPPES Registry** to extract Dr. Aris's verified clinic location and NPI number.
  2. Uses the **Google Maps Geocoding & Places APIs** (`search_nearby_places`) to find pharmacies within 5km.
* **What You See**:
  Verified provider credentials, clinic address, and nearby pharmacy options.

---

### 6. Insurance Claim Appeal Drafting
* **Prompt to Try**:
  > *"Draft an insurance appeal letter for Maya's denied $1,450 MRI claim."*
* **What Happens Under the Hood**:
  Kinflow retrieves the denial details from Firestore (`get_care_item`), references the insurance appeal playbook from RAG, and generates a formal, cite-backed Appeal Letter with prior authorization references and medical necessity language.
* **What You See**:
  A complete, ready-to-send appeal letter addressed to the insurer with claim numbers and medical justification.

---

## 🏗️ Technical Architecture

```
                               ┌────────────────────────────────────────────────┐
                               │           Browser Chat Interface               │
                               └──────────────────────┬─────────────────────────┘
                                                      │ HTTP / A2UI
                                                      ▼
                               ┌────────────────────────────────────────────────┐
                               │         Cloud Run Frontend (FastAPI)           │
                               └──────────────────────┬─────────────────────────┘
                                                      │ A2A Protocol (JSON-RPC)
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Vertex AI Agent Runtime (kinflow)                                     │
├───────────────────┬───────────────────┬────────────────────┬────────────────────┬──────────────────────┤
│    Memory Bank    │    RAG Engine     │   Cloud Storage    │  Firestore DB      │  External APIs       │
│  (Cross-Session)  │   (Serverless)    │   (Pill Imagery)   │   (Care Tasks)     │  (Maps, FDA, NPPES)  │
└───────────────────┴───────────────────┴────────────────────┴────────────────────┴──────────────────────┘
```

---

## 🚀 Running the Project

### Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager
- `google-agents-cli` (`uv tool install google-agents-cli`)
- Authenticated GCP SDK (`gcloud auth login`)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/tiffany/buildwithgemini-kinflow.git
cd buildwithgemini-kinflow

# Install dependencies
uv sync

# Launch local developer playground with Memory Bank
uv run adk web . --port 8080 --reload_agents
```
Open `http://localhost:8080` to interact with Kinflow.

---

## 🧪 Evaluation Suite

Automated evaluations run multi-turn traces against custom scoring metrics:
```bash
# Run evaluations
agents-cli eval run

# Grade traces
agents-cli eval grade --config tests/eval/eval_config.yaml --traces artifacts/traces/<trace_file>.json
```

---

## 📦 Deployment

- **Agent Runtime**:
  ```bash
  agents-cli deploy --project <PROJECT_ID> --region us-east1
  ```
- **Web Frontend (Cloud Run)**:
  ```bash
  gcloud run deploy kinflow-frontend --source frontend --region us-east1 --allow-unauthenticated
  ```
