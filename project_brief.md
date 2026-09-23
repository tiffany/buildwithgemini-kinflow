# My agent: Kinflow

One-liner: A conversational agent that helps families managing complex care keep track of appointments, referrals, and medical bills with a catalog of active care tasks and visit notes.

Tool coverage:
- Memory: Remembers care recipient background, diagnoses, insurance details, care team contacts, historical decisions from visits, and ongoing family preferences across sessions.
- Tools:
  - `get_care_items(status, category)`: Fetches open action items (appointments, pending referrals, unresolved bills, follow-up calls).
  - `add_care_item(title, category, due_date, owner, notes)`: Logs a new action item or next step.
  - `prepare_appointment_agenda(doctor_name, visit_reason)`: Compiles questions and data updates for upcoming visits before time runs out.
  - `draft_followup_message(item_id, channel)`: Drafts follow-up communication (calls/emails) to providers or insurers with full context.
- Catalog/UI: A "Care Action Board" catalog of open referrals, pending claims/bills, and upcoming visit checklists rendered as A2UI status cards and summary tables.
- Image gen: Visual care timeline cards, medication schedules, and printable appointment prep summary infographics.
- Sandbox: Computes days elapsed on stuck referrals, appeal deadlines, and tracks cumulative out-of-pocket medical expenses against insurance deductibles.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for calculating appeal deadlines and out-of-pocket medical costs; Cloud Trace for monitoring response latencies.
