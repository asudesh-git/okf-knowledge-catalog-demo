---
okf_version: "0.2"
title: "parts_inventory"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.parts_inventory`

## Purpose
Manufacturing component catalog and plant inventory (`50` rows) linking `part_number` to its manufacturing `source_plant_id`.

## Columns & Metrics
- `part_id` (`INTEGER`, PK): Numeric part ID (`1..50`).
- `part_number` (`STRING`, UK): Canonical part code (`PART-100..PART-149`, joins to `auto_aftersales_data.service_parts_usage.part_number`).
- `part_name` (`STRING`): Component description.
- `category` (`STRING`): Subsystem category.
- `source_plant_id` (`INTEGER`, FK -> `plants.plant_id`): Plant that manufactures this component (`1..7`).
- `quantity_on_hand` (`INTEGER`): Current warehouse stock level.
- `reorder_threshold` (`INTEGER`): Minimum safety stock threshold.
- `unit_cost` (`FLOAT`): Manufacturing unit cost (`USD`).
