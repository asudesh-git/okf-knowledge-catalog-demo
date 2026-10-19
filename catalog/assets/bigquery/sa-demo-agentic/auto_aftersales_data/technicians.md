---
okf_version: "0.2"
title: "technicians"
type: "context-overlay"
status: "stable"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "2026-10-19T15:40:00Z"
verified:
  - by: "human:asudesh@google.com"
    at: "2026-10-19T15:40:00Z"
sources:
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_sales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_manufacturing_data"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.technicians`

## Purpose
Directory of dealership service technicians (`120` rows, 1 row per `technician_id`) used to analyze repair efficiency, labor hours, and core-return compliance by certification tier.

## Columns & Metrics
- `technician_id` (`INTEGER`, PK): Unique technician ID (`1..120`).
- `technician_name` (`STRING`): Full name of the technician (`Tech_1..Tech_120`).
- `dealership_id` (`INTEGER`, FK -> `auto_sales_data.dealerships.dealership_id`): Assigned dealership (`1..8`).
- `certification_level` (`STRING`): Qualification tier (`'Master'`, `'Specialist'`, `'Senior'`, `'Apprentice'`).
- `specialty` (`STRING`): Primary subsystem specialization (`Engine`, `Electrical`, `Transmission`, `EV Battery`, `General`, `Brakes`, `HVAC`).
- `hire_date` (`DATE`): Dealership onboarding date.
