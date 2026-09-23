# Kinflow: Care Coordination Agent for Families Managing Complex Care

**Kinflow** is an intelligent, compassionate care coordination agent designed for families managing complex pediatric medical care. Built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Engine**, Kinflow helps caregivers keep track of appointments, follow up on pending referrals, appeal denied insurance claims, and quickly access critical care protocols and clinical information.

---

## 🌟 Key Features & Capabilities

- 📋 **Care Action Tracking**: Real-time CRUD operations over active care items, appointments, pending specialist referrals, and unresolved medical bills backed by **Cloud Firestore**.
- 🧠 **Cross-Session Memory Bank**: Powered by **Vertex AI Memory Bank**, Kinflow remembers patient history, family preferences, care team contacts, and critical medical alerts (such as drug allergies) across multiple sessions.
- 📚 **Vertex AI Serverless RAG Engine**: Grounded retrieval over clinical emergency seizure protocols and insurance appeal playbooks via a serverless Vertex AI RAG corpus.
- 💊 **Medication & Clinical Intelligence**:
  - Live FDA drug label lookups via the **openFDA API** (indications, dosages, black-box warnings).
  - Healthcare provider and specialist verification via the **CMS NPPES NPI Registry**.
  - Visual pill sizing & scale comparison with a US penny generated via **Gemini Imagen** (`gemini-3.1-flash-lite-image`) and hosted on Cloud Storage.
- 🗺️ **Geographic Healthcare Navigation**: Provider address geocoding and nearby healthcare facility discovery via **Google Maps Geocoding & Places APIs**.
- 🎨 **Adaptive Agent UI (A2UI)**: Natively renders rich, interactive care cards and summary boards in the chat interface.
- 💬 **Web Chat Frontend**: Modern chat interface served by a **FastAPI proxy** talking the **A2A Protocol** directly to Vertex AI Agent Runtime, deployed on **Cloud Run**.

---

## 🏗️ Architecture

```
User (Browser)
      │
      ▼
Cloud Run Web Frontend (FastAPI Proxy)
      │
      │  A2A Protocol (JSON-RPC)
      ▼
Vertex AI Agent Runtime (kinflow reasoningEngine)
      │
      ├── Memory Service: Vertex AI Memory Bank (Long-term Patient & Allergy Memory)
      ├── Knowledge Base: Vertex AI RAG Engine (Serverless Clinical Protocols)
      ├── Database: Google Cloud Firestore (Care Items & Tasks)
      ├── Image Generation: Gemini Imagen / Cloud Storage
      ├── APIs: Google Maps (Geocoding & Places), openFDA API, CMS NPPES Registry
      └── Presentation: A2UI v0.8 Specification (Interactive Cards & Agendas)
```

---

## 🛠️ Project Structure

```
kinflow/
├── app/
│   ├── agent.py               # Root agent, tools (Firestore, Maps, FDA, NPPES, RAG, Imagen), and callbacks
│   ├── fast_api_app.py        # FastAPI A2A backend server
│   └── app_utils/
│       └── a2ui_utils.py      # A2UI response transformer callback
├── frontend/                  # Web chat interface & A2A proxy
│   ├── main.py                # FastAPI proxy forwarding A2A messages
│   ├── requirements.txt       # Frontend dependencies (FastAPI, a2a-sdk)
│   ├── Dockerfile             # Container configuration for Cloud Run
│   └── static/
│       └── index.html         # Modern web chat UI with native A2UI card renderer
├── rag_docs/                  # Clinical care plans and insurance appeal guides
├── create_rag_corpus.py       # Serverless Vertex AI RAG corpus provisioning script
├── tests/
│   ├── eval/                  # Agent evaluation datasets and quality metrics
│   └── unit/                  # Unit tests for tools and agent callbacks
└── pyproject.toml             # Python dependencies (managed via uv)
```

---

## 🚀 Local Development

### 1. Requirements
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager
- `google-agents-cli` (`uv tool install google-agents-cli`)
- Google Cloud SDK (`gcloud`)

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/tiffany/buildwithgemini-kinflow.git
cd buildwithgemini-kinflow

# Install project dependencies
uv sync
```

### 3. Launch Local Playground
Run the local ADK developer playground with Memory Bank integration:
```bash
uv run adk web . --port 8080 --reload_agents
```
Open `http://localhost:8080` to interact with Kinflow.

---

## 🧪 Evaluation

Evaluate agent performance and trajectory quality using the built-in evaluation framework:
```bash
# Run evaluations
agents-cli eval run

# Grade evaluation traces against test datasets
agents-cli eval grade --config tests/eval/eval_config.yaml --traces artifacts/traces/<trace_file>.json
```

---

## ☁️ Deployment

### Agent Runtime (Vertex AI)
```bash
agents-cli deploy --project <PROJECT_ID> --region us-east1
```

### Frontend (Cloud Run)
```bash
gcloud run deploy kinflow-frontend \
  --source frontend \
  --region us-east1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUM>/locations/us-east1/reasoningEngines/<ENGINE_ID>",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```
