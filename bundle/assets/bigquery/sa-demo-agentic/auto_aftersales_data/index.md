---
okf_version: "0.2"
title: "Dataset auto_aftersales_data"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic"
  documentType: "knowledge-base-index"
---

# Dataset `sa-demo-agentic.auto_aftersales_data`

## Purpose
Core After-Sales, Dealership Service, and Warranty Adjudication dataset in `us-central1`. Previously lacked native BigQuery column descriptions; enriched via OKF v0.2 with verified financial formulas, supplier recovery rules, and join fan-out guardrails.

## Curated Table Overlays
- `warranty_claims` (1,894 rows): Warranty claim adjudication, plant attribution (`build_plant_name` vs `part_source_plant_name`), and supplier fault flags.
- `service_orders` (6,104 rows): Dealership service visits; use `is_warranty_covered = TRUE` (`$1,591,386.85`) rather than `service_type = 'Warranty Repair'` (`$826,977.80`).
- `service_parts_usage` (10,861 rows): Replaced parts per service order and `defective_part_returned` core-return tracking.
- `vehicle_ownership` (5,000 rows): VIN-level warranty dates, mileage, `ownership_status`, and `extended_warranty_purchased`.
- `technicians` (120 rows): Certified dealership technicians (`Master`, `Senior`, `Apprentice`, `Specialist`).
- `recall_campaigns` (40 rows): Safety recall campaigns by `affected_model_id` and `target_component`.
