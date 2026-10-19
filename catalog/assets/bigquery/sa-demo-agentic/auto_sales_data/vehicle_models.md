---
okf_version: "0.2"
title: "vehicle_models"
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
links:
  - target: "../auto_manufacturing_data/plants.md"
    type: "schema-join"
    source_column: "plant_id"
    target_column: "plant_id"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_sales_data.vehicle_models`

## Purpose
Master vehicle platform catalog (`259` total rows; **ONLY 8 active production models** `model_id BETWEEN 1 AND 8`). Maps each vehicle model to its primary assembly `plant_id` in `auto_manufacturing_data.plants`.

## Columns & Metrics
- `model_id` (`INTEGER`, PK): Unique model identifier. **CATALOG PADDING TRAP**: Rows `9..259` are unallocated catalog placeholders with zero sales or service orders. Always filter `model_id BETWEEN 1 AND 8` or `INNER JOIN` to `vehicle_sales` / `vehicle_ownership`.
- `model_name` (`STRING`): Commercial model name (`Model S1`, `Model T1`, `Model X1`, `Model E1`, `Model SUV2`, `Model C1`, `Model V1`, `Model R1`).
- `category` (`STRING`): Body style (`Sedan`, `Truck`, `SUV`, `EV`).
- `msrp` (`FLOAT`): Manufacturer Suggested Retail Price (`USD`).
- `plant_id` (`INTEGER`, FK -> `auto_manufacturing_data.plants.plant_id`): Primary final assembly plant ID (`1..7`).
