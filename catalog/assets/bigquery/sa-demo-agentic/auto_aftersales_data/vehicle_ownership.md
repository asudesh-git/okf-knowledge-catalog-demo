---
okf_version: "0.2"
title: "vehicle_ownership"
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
  - target: "../auto_sales_data/vehicle_sales.md"
    type: "schema-join"
    source_column: "vin"
    target_column: "vin"
  - target: "../auto_sales_data/vehicle_models.md"
    type: "schema-join"
    source_column: "model_id"
    target_column: "model_id"
  - target: "../../../../documents/concepts/active-warranty-entitlement-fleet.md"
    type: "related"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.vehicle_ownership`

## Purpose
Master VIN-level ownership, odometer, and warranty entitlement registry (`5,000` rows, 1 row per `vin`). Governs the **Active Warranty Entitlement Fleet** (`4,650` entitled vehicles).

## Columns & Metrics
- `vin` (`STRING`, PK): Unique 17-character Vehicle Identification Number (`1:1` with `auto_sales_data.vehicle_sales.vin`).
- `customer_id` (`STRING`): Current owner identifier.
- `model_id` (`INTEGER`, FK -> `auto_sales_data.vehicle_models.model_id`): Vehicle platform ID (`1..8`).
- `sale_date` (`DATE`): Original retail delivery date.
- `warranty_start_date` (`DATE`): Factory warranty commencement date.
- `warranty_end_date` (`DATE`): Expiration date (`3 years` standard or `5 years` when `extended_warranty_purchased = TRUE`).
- `extended_warranty_purchased` (`BOOLEAN`): Indicates transferable 5-year extended protection plan (`1,069` vehicles = `TRUE`).
- `current_mileage` (`INTEGER`): Latest connected-vehicle/service odometer reading.
- `ownership_status` (`STRING`): Lifecycle ownership state:
  - `'Active'` (`4,582` rows): Original owner; full warranty entitlement.
  - `'Transferred'` (`304` rows): Secondary-market resale; **ONLY entitled to warranty if `extended_warranty_purchased = TRUE` (`68` vehicles)**; the remaining `236` transferred vehicles with standard warranty have no OEM coverage.
  - `'Buyback'` (`114` rows): Manufacturer buyback/lemon-law fleet; excluded from active customer warranty entitlement.
