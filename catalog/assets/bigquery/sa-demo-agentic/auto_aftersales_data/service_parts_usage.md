---
okf_version: "0.2"
title: "service_parts_usage"
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
  - target: "service_orders.md"
    type: "schema-join"
    source_column: "service_order_id"
    target_column: "service_order_id"
  - target: "../../../../documents/learnings/warranty-fanout-and-absorption-learnings.md"
    type: "related"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.service_parts_usage`

## Purpose
Line-item component replacement log (`10,861` rows, 1 row per `usage_id`, `N:1` to `service_order_id`). Tracks part numbers, quantities, costs, and whether defective cores were returned by the dealership for supplier chargeback recovery.

## Columns & Metrics
- `usage_id` (`INTEGER`, PK): Unique part replacement line item ID.
- `service_order_id` (`INTEGER`, FK -> `service_orders.service_order_id`): Parent service visit. **JOIN FAN-OUT WARNING**: Multiple rows exist per `service_order_id` (`1.78` average). Always aggregate by `service_order_id` before joining to `service_orders` or `warranty_claims`.
- `part_number` (`STRING`): OEM catalog part number (`PART-100..PART-149`, links to `auto_manufacturing_data.parts_inventory.part_number`).
- `part_name` (`STRING`): Component description.
- `part_category` (`STRING`): Subsystem category (`Engine`, `Brakes`, `Electrical`, `Suspension`, `Transmission`, `HVAC`, `Battery`, `Body`, `Exhaust`).
- `quantity_used` (`INTEGER`): Units installed during the repair.
- `unit_cost` (`FLOAT`): Wholesale cost per unit.
- `total_part_cost` (`FLOAT`): `quantity_used * unit_cost`.
- `defective_part_returned` (`BOOLEAN`): `TRUE` if the dealership returned the failed component core to the OEM teardown center. Required (`LOGICAL_AND(defective_part_returned) = TRUE` across the `service_order_id`) to claim the 70% supplier chargeback on `supplier_fault = TRUE` warranty claims.
