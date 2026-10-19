---
okf_version: "0.2"
title: "Dataset auto_sales_data"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic"
  documentType: "knowledge-base-index"
---

# Dataset `sa-demo-agentic.auto_sales_data`

## Purpose
Retail vehicle sales, active vehicle model catalog, dealership directory, and customer identity crosswalk in `us-central1`.

## Curated Table Overlays
- `vehicle_sales` (5,000 rows): VIN-level retail sales transactions linking `model_id`, `dealership_id`, and `sale_price`.
- `vehicle_models` (259 rows; **8 active models** `model_id` 1..8): Model catalog linking each vehicle platform to its primary `plant_id`.
- `dealerships` (259 rows; **8 active dealerships** `dealership_id` 1..8): Authorized retail and service dealership network.
- `customer_identity_crosswalk` (5,000 rows): Bridges `auto_customer_id` (`vin`) to `global_loyalty_id` (`match_confidence >= 0.85`).
