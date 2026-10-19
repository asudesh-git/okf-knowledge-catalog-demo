---
okf_version: "0.2"
title: "plants"
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
  - target: "../../../../documents/concepts/dimension-catalog-padding-guardrail.md"
    type: "related"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.plants`

## Purpose
Master manufacturing facility table (`259` total rows; **ONLY 7 active manufacturing plants** `plant_id BETWEEN 1 AND 7`).

## Columns & Metrics
- `plant_id` (`INTEGER`, PK): Unique facility identifier. **CATALOG PADDING TRAP**: Rows `8..259` are unallocated global facility codes with zero assembly lines or production. Always filter `plant_id BETWEEN 1 AND 7` or `INNER JOIN` to `assembly_line_status` before computing capacity or efficiency averages!
- `plant_name` (`STRING`, UK): Facility name (`Detroit Assembly`, `Ohio Stamping`, `Kentucky Truck`, `Chicago Assembly`, `Dearborn Engine`, `Kansas City Assembly`, `Buffalo Stamping`). Joins to `warranty_claims.build_plant_name` (as final assembly plant) and `warranty_claims.part_source_plant_name` (as component supplier plant).
- `location` (`STRING`): City and state (`MI`, `OH`, `KY`, `IL`, `MO`, `NY`).
- `annual_capacity` (`INTEGER`): Nameplate annual production capacity.
- `manager_name` (`STRING`): Plant director name.
