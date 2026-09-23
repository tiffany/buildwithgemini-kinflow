# Kinflow: Care Coordination Agent for Families Managing Complex Care

**Kinflow** is an intelligent, compassionate care coordination agent designed for families managing complex pediatric medical care. Built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Engine**, Kinflow helps caregivers track appointments, follow up on pending referrals, appeal denied insurance claims, and access critical clinical protocols.

---

## 💡 Why We Built Kinflow (The Problem & Caregiver Story)

Caring for a child with complex medical needs (such as pediatric epilepsy, rare diseases, or developmental conditions) is often described by parents as a **demanding, unpaid full-time job**.

### The Caregiver Burden:
- **Fragmented Care Teams**: A single child often sees 5 to 10 specialists (neurologists, cardiologists, physical therapists) across different health systems that do not share medical records.
- **Lost Referrals & Bureaucratic Stalls**: Referrals sit in fax queues for weeks. If parents don't proactively call clinics and insurers, consultations get delayed by months.
- **Insurance Claim Denials**: Insurers routinely deny specialized tests (like MRIs or EEGs) as "not pre-authorized." Families face steep out-of-pocket bills unless they file a formal, cite-backed appeal within strict 30-day deadlines.
- **High-Stakes Emergency Protocols**: In emergencies (e.g., a seizure lasting over 5 minutes), caregivers must act instantly. Panicked parents shouldn't have to scramble through paper binders or search generic websites for their child's rescue medication dosage.
- **Cognitive Overload**: Parents must remember every medication change, past allergic reaction, and doctor's recommendation across years of care.

### Our Mission:
**Kinflow was built to lift this logistical burden off caregivers' shoulders.** By acting as an empathetic, context-aware co-pilot, Kinflow ensures no referral gets lost, no appeal deadline passes, allergies are always remembered, and clinical emergency protocols are instantly accessible.

---

## 🛠️ How It Was Built (Architecture & Technical Decisions)

Kinflow is built on top of the **Google Agent Development Kit (ADK)** and integrates **7 core Google Cloud & AI services**:

```
                               ┌────────────────────────────────────────────────────────┐
                               │           Caregiver Browser Interface                  │
                               └───────────────────────────┬────────────────────────────┘
                                                           │ HTTP / A2UI JSON
                                                           ▼
                               ┌────────────────────────────────────────────────────────┐
                               │       Cloud Run Web Frontend (FastAPI A2A Proxy)       │
                               └───────────────────────────┬────────────────────────────┘
                                                           │ A2A Protocol (JSON-RPC)
                                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Vertex AI Agent Runtime (kinflow)                                               │
├─────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│    Vertex AI Memory     │   Vertex AI RAG Engine   │   Google Cloud Firestore │         Gemini Imagen & GCS           │
│   • PreloadMemoryTool   │   • Serverless Corpus    │   • Care items & tasks   │   • gemini-3.1-flash-lite-image       │
│   • Cross-session memory│   • Clinical protocols   │   • Real-time updates    │   • Cloud Storage public hosting      │
│   • Allergy persistence │   • Insurance playbooks  │   • Prioritized backlog  │   • Visual pill-to-coin scaling       │
├─────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────────────────┤
│                                     External Healthcare & Geospatial APIs                                             │
│   • openFDA API (Drug labels & warnings)                                                                              │
│   • CMS NPPES NPI Registry (Verified doctor credentials & clinic taxonomy)                                           │
│   • Google Maps Geocoding & Places APIs (Address coordinates & nearby pharmacy discovery)                            │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                        Adaptive Agent UI (A2UI v0.8)                                                  │
│   • Structured card, column, and row schemas transforming raw agent responses into interactive UI surfaces          │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Choices:
1. **Agent-to-Agent (A2A) Protocol**: Kinflow deploys as a modern A2A agent on Vertex AI Agent Runtime, communicating with our FastAPI proxy via structured JSON-RPC tasks and artifact updates.
2. **Serverless RAG as a Function Tool**: Built-in retrieval declarations often conflict with custom tools in Gemini. We engineered the Vertex AI Serverless RAG Engine as a **plain Python function tool** (`consult_care_knowledge_base`), allowing seamless coexistence with Firestore, Maps, and FDA tools.
3. **Persistent Memory Bank**: Using Vertex AI Memory Bank, Kinflow tracks long-term constraints (such as Maya's severe penicillin allergy) and recalls them across conversations to prevent dangerous medication suggestions.
4. **Resilient A2UI Rendering**: The Cloud Run frontend includes a lightweight A2UI renderer that parses `beginRendering` and `surfaceUpdate` data parts, falling back to clean text if unexpected components are received.

---

## 🌟 What We Built & Connected

Kinflow connects:
1. **Vertex AI Agent Engine (Runtime)**: Deployed ADK agent serving requests over the **A2A Protocol**.
2. **Vertex AI Memory Bank**: Cross-session long-term memory remembering patient history and allergies.
3. **Vertex AI Serverless RAG Engine**: Semantic retrieval over clinical seizure protocols and insurance playbooks.
4. **Google Cloud Firestore**: Real-time database for care tasks, appointments, and referrals.
5. **Gemini Imagen (`gemini-3.1-flash-lite-image`)**: Generates pill scale images relative to a US penny, hosted on **Google Cloud Storage**.
6. **Healthcare & Geospatial Public APIs**:
   - **openFDA API**: Live FDA drug labels and warnings.
   - **CMS NPPES Registry**: Verification of doctor NPI numbers and practice addresses.
   - **Google Maps API**: Geocoding and Nearby Places search for clinics and pharmacies.
7. **Adaptive Agent UI (A2UI v0.8)**: Interactive cards rendered natively in our Cloud Run web frontend.

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
