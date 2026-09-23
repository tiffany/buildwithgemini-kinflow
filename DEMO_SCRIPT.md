# Kinflow: Step-by-Step Interactive Demo Script

Use this demo script to test Kinflow and experience all **7 integrated Google Cloud and AI capabilities** in action. You can run these prompts either in the **Cloud Run Web Chat UI** or the local **ADK Developer Playground** (`uv run adk web . --port 8080 --reload_agents`).

---

## 📋 Quick Copy-Paste Prompts

| Step | Topic | Exact Prompt to Copy-Paste | Connected Google Technologies |
| :---: | :--- | :--- | :--- |
| **1** | **Care Action Board** | `Hello Kinflow! What care tasks and appointments are currently open for Maya?` | Google Cloud Firestore + Adaptive Agent UI (A2UI v0.8) |
| **2** | **Emergency Clinical Protocol** | `What is the emergency rescue protocol if Maya's seizure lasts longer than 5 minutes?` | Vertex AI Serverless RAG Engine (`consult_care_knowledge_base`) |
| **3A** | **Save Allergy to Long-term Memory** | `Please remember that Maya has a severe anaphylactic allergy to Penicillin and Amoxicillin.` | Vertex AI Memory Bank (Long-Term Patient Memory) |
| **3B** | **Memory Constraint Verification** | `Maya has an ear infection. Can the urgent care doctor prescribe Augmentin?` | Vertex AI Memory Bank (`PreloadMemoryTool` Recall) |
| **4** | **FDA Drug Warnings & Pill Scale** | `Can you look up Keppra in the FDA registry and show me what a 500mg pill looks like compared to a coin?` | openFDA API + Gemini Imagen (`gemini-3.1-flash-lite-image`) on GCS |
| **5** | **Provider & Pharmacy Discovery** | `Look up Dr. Aris in neurology, find his practice address, and locate the nearest 24-hour pharmacy.` | CMS NPPES Registry + Google Maps Geocoding & Places APIs |
| **6** | **Insurance Denial Appeal Letter** | `Draft an insurance appeal letter for Maya's denied $1,450 MRI claim.` | Firestore (`get_care_item`) + RAG Insurance Playbook |

---

## 🔍 Detailed Walkthrough & What to Expect

### Step 1: The Care Action Board (Firestore + A2UI)
* **Prompt**:
  ```text
  Hello Kinflow! What care tasks and appointments are currently open for Maya?
  ```
* **Behind the Scenes**:
  - Kinflow executes the `list_care_items` tool, querying the Cloud Firestore collection.
  - The agent's `a2ui_callback` converts the data into an A2UI v0.8 JSON surface (`Card`, `Column`, `Text` components).
* **Expected Result**:
  An interactive visual card displaying Maya's open neurology appointment, pending cardiology referral, and an unresolved MRI claim denial with owners and due dates.

---

### Step 2: Emergency Protocol Retrieval (Vertex AI Serverless RAG)
* **Prompt**:
  ```text
  What is the emergency rescue protocol if Maya's seizure lasts longer than 5 minutes?
  ```
* **Behind the Scenes**:
  - Kinflow executes the `consult_care_knowledge_base` function tool.
  - It performs a semantic search against the serverless Vertex AI RAG corpus loaded with pediatric emergency care plans.
* **Expected Result**:
  A clinical rescue plan: positioning Maya safely on her side, administering prescribed rescue medications (such as intranasal Nayzilam or rectal Diastat), and calling 911 immediately if the seizure exceeds 5 minutes.

---

### Step 3: Clinical Memory & Allergy Safety (Vertex AI Memory Bank)
* **Part A (Set Memory)**:
  ```text
  Please remember that Maya has a severe anaphylactic allergy to Penicillin and Amoxicillin.
  ```
  *Kinflow confirms the allergy has been recorded in Maya's permanent health profile.*

* **Part B (Test Memory Across Turns / Sessions)**:
  ```text
  Maya has an ear infection. Can the urgent care doctor prescribe Augmentin?
  ```
* **Behind the Scenes**:
  - Kinflow preloads long-term memory via the `PreloadMemoryTool`.
  - It identifies that **Augmentin is a combination of amoxicillin and clavulanate**.
* **Expected Result**:
  Kinflow warns against Augmentin, clearly explaining the cross-allergy risk with amoxicillin, and suggests non-penicillin alternatives (like cephalosporins or azithromycin) for the doctor to review.

---

### Step 4: FDA Drug Intelligence & Pill Scale (openFDA + Gemini Imagen)
* **Prompt**:
  ```text
  Can you look up Keppra in the FDA registry and show me what a 500mg pill looks like compared to a coin?
  ```
* **Behind the Scenes**:
  - Calls `lookup_medication_info` against the official openFDA Drug API to retrieve FDA-approved indications, black-box warnings, and pediatric guidelines.
  - Calls `visualize_pill_size` using **Gemini Imagen** (`gemini-3.1-flash-lite-image`) in the global region.
  - Uploads the image to Cloud Storage and returns the public HTTPS URL.
* **Expected Result**:
  FDA clinical guidance and an inline image comparing the oval yellow Keppra tablet side-by-side with a US penny coin.

---

### Step 5: Healthcare Provider & Pharmacy Discovery (CMS NPPES + Google Maps)
* **Prompt**:
  ```text
  Look up Dr. Aris in neurology, find his practice address, and locate the nearest 24-hour pharmacy.
  ```
* **Behind the Scenes**:
  - Queries `lookup_healthcare_provider` against the CMS NPPES NPI Registry to fetch verified credentials and clinic address.
  - Calls `geocode_address` and `search_nearby_places` using the Google Maps API to find nearby pharmacies.
* **Expected Result**:
  Doctor's verified NPI number, practice address, and nearby pharmacy names, addresses, and coordinates.

---

### Step 6: Insurance Claim Appeal Drafting (Firestore + RAG Playbook)
* **Prompt**:
  ```text
  Draft an insurance appeal letter for Maya's denied $1,450 MRI claim.
  ```
* **Behind the Scenes**:
  - Fetches the denial reason from Firestore (`care-103`).
  - Queries the insurance appeal playbook in RAG for medical necessity guidelines and ERISA/ACA appeal rights.
  - Formulates a formal appeal letter via `draft_followup_communication`.
* **Expected Result**:
  A formal, professional appeal letter addressed to the insurance claims department, citing physician diagnosis, prior authorization context, and medical necessity justification.
