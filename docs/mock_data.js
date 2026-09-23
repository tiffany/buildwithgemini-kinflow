const DEMO_RESPONSES = {
  "agenda": {
    "text": "I've pulled up Maya's current open care tasks and appointments from Firestore:",
    "parts": [
      {
        "kind": "a2ui",
        "data": {
          "beginRendering": { "root": "card-root", "surfaceId": "maya-care-tasks" },
          "surfaceUpdate": {
            "surfaceId": "maya-care-tasks",
            "components": [
              { "id": "card-root", "component": { "Card": { "child": "main-col" } } },
              { "id": "main-col", "component": { "Column": { "children": { "explicitList": ["h1", "t1", "d1", "t2", "d2", "t3"] } } } },
              { "id": "h1", "component": { "Text": { "text": "📋 Maya's Active Care Action Board", "usageHint": "h2" } } },
              { "id": "t1", "component": { "Text": { "text": "• [HIGH] Chase stuck Cardiology Referral at Valley Children's (Sent 2w ago)", "usageHint": "body" } } },
              { "id": "d1", "component": { "Divider": {} } },
              { "id": "t2", "component": { "Text": { "text": "• [SCHEDULED] Dr. Aris Neurology EEG Follow-up — Oct 12, 10:00 AM", "usageHint": "body" } } },
              { "id": "d2", "component": { "Divider": {} } },
              { "id": "t3", "component": { "Text": { "text": "• [OPEN] Draft insurance appeal for denied $1,450 brain MRI claim", "usageHint": "body" } } }
            ]
          }
        }
      }
    ]
  },
  "seizure": {
    "text": "🚨 **EMERGENCY SEIZURE PROTOCOL (Retrieved from Clinical Knowledge Base)**\n\n• **> 5 Minutes**: Status Epilepticus medical emergency. Call 911 immediately.\n• **Rescue Medication**: Administer prescribed rectal diazepam (Diastat) 5mg or nasal midazolam.\n• **Safety Positioning**: Place Maya on her left side in the recovery position to maintain airway; do NOT place anything in her mouth.\n• **Post-Ictal**: Record duration, physical tremors, and report to Dr. Aris's neurology triage nurse.",
    "parts": []
  },
  "appeal": {
    "text": "📝 **EXPEDITED FORMAL INSURANCE APPEAL**\n\n**To:** Health Plan Appeals & Grievance Department\n**Patient:** Maya Lin (DOB: 04/12/2018) | **Claim #:** CLM-992014-A\n**Denied Service:** CPT 70553 (Brain MRI with & without contrast) — $1,450.00\n\n**Reason for Denial:** \"Not medically necessary\"\n\n**Appeal Statement:**\nThis letter formally appeals the denial of coverage for Maya Lin's brain MRI performed on Sept 14. Maya has refractory focal epilepsy with recent breakthrough clusters. Under American Academy of Neurology (AAN) guidelines, high-resolution contrast-enhanced neuroimaging is required to identify structural epileptogenic foci.\n\nEnclosed please find clinical chart notes from treating neurologist Dr. Aris (NPI: 1487692011) confirming clinical medical necessity. We request immediate reversal of this adverse benefit determination.",
    "parts": []
  },
  "keppra": {
    "text": "Here is the FDA drug profile and visual pill scale for Keppra (levetiracetam):",
    "parts": [
      {
        "kind": "a2ui",
        "data": {
          "beginRendering": { "root": "k-root", "surfaceId": "keppra-scale" },
          "surfaceUpdate": {
            "surfaceId": "keppra-scale",
            "components": [
              { "id": "k-root", "component": { "Card": { "child": "k-col" } } },
              { "id": "k-col", "component": { "Column": { "children": { "explicitList": ["kh", "kw", "kimg", "kcap"] } } } },
              { "id": "kh", "component": { "Text": { "text": "Keppra (levetiracetam 500mg) Scale & Warnings", "usageHint": "h2" } } },
              { "id": "kw", "component": { "Text": { "text": "FDA Warning: Monitor for somnolence, behavioral changes, suicidal ideation, and acute coordination difficulties.", "usageHint": "body" } } },
              { "id": "kimg", "component": { "Image": { "url": "https://storage.googleapis.com/kinflow-media-qwiklabs-gcp-04-b99c507c7b84/medications/pill_scale_keppra_500mg_9f1437.jpg" } } },
              { "id": "kcap", "component": { "Text": { "text": "Generated visual scale: Keppra 500mg yellow oblong tablet next to a US penny coin.", "usageHint": "caption" } } }
            ]
          }
        }
      }
    ]
  },
  "doctor": {
    "text": "🏥 **Provider & Pharmacy Lookup**:\n\n• **Dr. Aris (NPI: 1487692011)**\n  Specialty: Pediatric Neurology\n  Practice: Valley Children's Neuroscience Center, 9300 Valley Children's Pl, Madera, CA\n  Phone: (559) 353-3000\n\n• **Nearest 24-Hour Pharmacy**:\n  Walgreens 24/7 Pharmacy (0.8 mi)\n  4175 E Shields Ave, Fresno, CA\n  Phone: (559) 224-6963",
    "parts": []
  },
  "allergy": {
    "text": "⚠️ **CRITICAL ALLERGY ALERT (Vertex AI Long-Term Memory Bank)**\n\n**DO NOT PRESCRIBE AUGMENTIN.**\n\nAccording to Maya's persistent care profile, Maya has a documented severe anaphylactic allergy to **penicillin and amoxicillin**.\n\nAugmentin is **amoxicillin + clavulanate** (a penicillin-class antibiotic) and is strictly contraindicated. Please inform the urgent care physician to prescribe a non-beta-lactam alternative such as **azithromycin** or **cefdinir** (if cephalosporins are cleared).",
    "parts": []
  }
};
