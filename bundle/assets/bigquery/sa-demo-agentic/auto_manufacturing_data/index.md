---
okf_version: "0.2"
title: "Dataset auto_manufacturing_data"
type: "knowledge-base-index"
status: "draft"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "2026-10-19T15:40:00Z"
sources:
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_sales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_manufacturing_data"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic"
  documentType: "knowledge-base-index"
---

# Dataset `sa-demo-agentic.auto_manufacturing_data`

## Purpose
Manufacturing facility master data, assembly line OEE telemetry, component parts inventory, and end-of-line quality inspections in `us-central1`.

## Curated Table Overlays
- `plants` (259 rows; **7 active plants** `plant_id` 1..7): Manufacturing plant directory (`plant_name`, `location`, `annual_capacity`).
- `assembly_line_status` (35 rows): Line-level `operational_efficiency` (OEE), `status`, and `daily_output` for the 7 active plants.
- `parts_inventory` (50 rows): Component inventory and `source_plant_id` mapping.
- `quality_inspections` (500 rows): End-of-line plant inspection `defect_severity` and `corrective_action` logs.
