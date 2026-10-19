---
okf_version: "0.2"
title: "vehicle_sales"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_sales_data.vehicle_sales`

## Purpose
Retail vehicle sales fact table (`5,000` rows, 1 row per `sale_id` / `vin`). Connects sold vehicles (`vin`) to `vehicle_models` (`model_id`) and selling `dealerships` (`dealership_id`).

## Columns & Metrics
- `sale_id` (`INTEGER`, PK): Unique retail transaction ID (`1..5000`).
- `vin` (`STRING`, UK, FK -> `auto_aftersales_data.vehicle_ownership.vin`): 17-character VIN (`1:1` grain with `vehicle_ownership`).
- `model_id` (`INTEGER`, FK -> `vehicle_models.model_id`): Sold model ID (`1..8`).
- `dealership_id` (`INTEGER`, FK -> `dealerships.dealership_id`): Selling dealership ID (`1..8`).
- `sale_date` (`DATE`): Retail delivery date.
- `sale_price` (`FLOAT`): Final transaction price paid (`USD`).
- `customer_id` (`STRING`): Purchasing customer identifier.
