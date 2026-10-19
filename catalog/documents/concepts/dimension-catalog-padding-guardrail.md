---
okf_version: "0.2"
title: "Dimension Catalog Padding Guardrail (259 Rows Trap)"
type: "knowledge-base"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts/dimension-catalog-padding-guardrail"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts"
  documentType: "knowledge-base"
---

# Dimension Catalog Padding Guardrail (259 Rows Trap)

## Purpose
Prevents 32x aggregation distortion caused by unallocated ERP placeholder rows in `plants`, `vehicle_models`, and `dealerships`.

## Active vs Padded Entity Counts
- `auto_manufacturing_data.plants`: `259` total rows -> **7 active plants** (`plant_id BETWEEN 1 AND 7`, total capacity `1,250,000` units/yr vs `45,860,000` padded).
- `auto_sales_data.vehicle_models`: `259` total rows -> **8 active models** (`model_id BETWEEN 1 AND 8`).
- `auto_sales_data.dealerships`: `259` total rows -> **8 active dealerships** (`dealership_id BETWEEN 1 AND 8`).
