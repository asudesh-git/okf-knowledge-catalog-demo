---
okf_version: "0.2"
title: "assembly_line_status"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.assembly_line_status`

## Purpose
Operational telemetry for active manufacturing lines (`35` rows, 5 lines per active plant `plant_id` 1..7).

## Columns & Metrics
- `line_id` (`INTEGER`, PK): Unique assembly line identifier (`1..35`).
- `plant_id` (`INTEGER`, FK -> `plants.plant_id`): Parent manufacturing plant (`1..7`).
- `line_name` (`STRING`): Line designation (`Body Shop`, `Paint Shop`, `Final Assembly`, `Powertrain`, `Trim & Chassis`).
- `status` (`STRING`): Operational status (`Running`, `Maintenance`, `Downtime`).
- `operational_efficiency` (`FLOAT`): Overall Equipment Effectiveness (OEE) ratio (`0.0..1.0`).
- `daily_output` (`INTEGER`): Units produced per day.
- `last_maintenance_date` (`DATE`): Date of last scheduled preventative maintenance.
