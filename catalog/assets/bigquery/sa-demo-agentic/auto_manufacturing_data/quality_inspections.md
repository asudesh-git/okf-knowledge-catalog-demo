---
okf_version: "0.2"
title: "quality_inspections"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_manufacturing_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.quality_inspections`

## Purpose
End-of-line plant quality audit log (`500` rows) recording in-plant defect detections prior to vehicle shipment.

## Columns & Metrics
- `inspection_id` (`INTEGER`, PK): Unique inspection record ID (`1..500`).
- `plant_id` (`INTEGER`, FK -> `plants.plant_id`): Inspected manufacturing plant (`1..7`).
- `line_id` (`INTEGER`, FK -> `assembly_line_status.line_id`): Inspected assembly line (`1..35`).
- `inspection_date` (`DATE`): Date of audit.
- `inspector_name` (`STRING`): Quality engineer identifier.
- `passed` (`BOOLEAN`): `TRUE` if unit passed without rework; `FALSE` if defect was logged.
- `defect_type` (`STRING`): Logged failure mode (`Weld Porosity`, `Paint Blemish`, `Torque Spec Deviation`, `Electrical Short`, `Panel Gap`, `Fluid Leak`).
- `defect_severity` (`STRING`): Severity tier (`Critical`, `Major`, `Minor`, `Cosmetic`).
- `corrective_action` (`STRING`): Plant disposition (`Line Stop & Recalibrate`, `Rework Bay`, `Scrap Part`, `Supplier Containment`).
