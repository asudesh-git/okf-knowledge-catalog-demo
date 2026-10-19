---
okf_version: "0.2"
title: "recall_campaigns"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.recall_campaigns`

## Purpose
Registry of NHTSA / OEM safety and compliance recall campaigns (`40` rows, 1 row per `recall_id`).

## Columns & Metrics
- `recall_id` (`INTEGER`, PK): Unique campaign identifier (`1..40`).
- `campaign_code` (`STRING`): Official recall bulletin code (`RC-2023-001..RC-2023-040`).
- `issue_date` (`DATE`): Campaign release date.
- `affected_model_id` (`INTEGER`, FK -> `auto_sales_data.vehicle_models.model_id`): Target vehicle model (`1..8`).
- `target_component` (`STRING`): Subsystem subject to recall (`Brakes`, `Electrical`, `Battery`, `Engine`, `Steering`, `Fuel System`, `Suspension`, `Transmission`).
- `severity` (`STRING`): Risk classification (`'Critical'`, `'High'`, `'Medium'`, `'Low'`).
- `estimated_cost_per_vehicle` (`FLOAT`): Budgeted per-VIN remediation cost.
