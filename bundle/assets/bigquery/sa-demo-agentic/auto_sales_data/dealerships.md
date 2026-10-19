---
okf_version: "0.2"
title: "dealerships"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_sales_data.dealerships`

## Purpose
Master dealership directory (`259` total rows; **ONLY 8 active operational dealerships** `dealership_id BETWEEN 1 AND 8`).

## Columns & Metrics
- `dealership_id` (`INTEGER`, PK): Unique dealership identifier. **CATALOG PADDING TRAP**: Rows `9..259` are inactive franchise placeholders with zero sales, service orders, or technicians. Always `INNER JOIN` to `vehicle_sales` or `service_orders`, or filter `dealership_id BETWEEN 1 AND 8`.
- `dealership_name` (`STRING`): Authorized dealer name (`AutoNation North`, `Metro Motors`, `Pacific Crest Auto`, `Lone Star Ford`, `Midwest Premier`, `Empire State Auto`, `Sunbelt Dealership`, `Mountain View Motors`).
- `region` (`STRING`): Sales territory (`North`, `South`, `East`, `West`, `Midwest`).
- `state` (`STRING`): US state code.
