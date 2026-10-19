---
okf_version: "0.2"
title: "service_orders"
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
  - target: "../auto_sales_data/dealerships.md"
    type: "schema-join"
    source_column: "dealership_id"
    target_column: "dealership_id"
queries:
  - title: "OEM Warranty-Covered Service Absorption by Service Type"
    description: "Demonstrates why filtering is_warranty_covered = TRUE ($1,591,386.85) is mandatory vs filtering service_type = 'Warranty Repair' ($826,977.80)."
    sql: |
      SELECT
        service_type,
        is_warranty_covered,
        COUNT(*) AS order_count,
        ROUND(SUM(total_cost), 2) AS gross_service_cost,
        ROUND(SUM(customer_paid_amount), 2) AS customer_paid_total,
        ROUND(SUM(total_cost - customer_paid_amount), 2) AS oem_absorbed_warranty_cost
      FROM `sa-demo-agentic.auto_aftersales_data.service_orders`
      GROUP BY service_type, is_warranty_covered
      ORDER BY oem_absorbed_warranty_cost DESC;
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.service_orders`

## Purpose
Captures every dealership service bay visit (`6,104` rows, 1 row per `service_order_id`) across retail maintenance, repairs, warranty repairs, and safety recalls.

## Columns & Metrics
- `service_order_id` (`INTEGER`, PK): Unique service order identifier (`1..6104`).
- `vin` (`STRING`, FK -> `vehicle_ownership.vin`): Serviced vehicle VIN.
- `dealership_id` (`INTEGER`, FK -> `auto_sales_data.dealerships.dealership_id`): Servicing dealership ID (`1..8` active dealerships).
- `technician_id` (`INTEGER`, FK -> `technicians.technician_id`): Assigned lead service technician (`1..120`).
- `service_date` (`DATE`): Date the repair order was completed.
- `service_type` (`STRING`): Operational bay category (`'Routine Maintenance'`, `'Repair'`, `'Warranty Repair'`, `'Recall Service'`). **CRITICAL CAVEAT**: Do NOT filter `service_type = 'Warranty Repair'` (`$826,977.80`) to compute total warranty-covered service cost! `690` `'Repair'` orders (`$558,639.28`) and `282` `'Recall Service'` orders (`$205,769.77`) are ALSO covered under warranty (`is_warranty_covered = TRUE`, `customer_paid_amount = 0`).
- `labor_hours` (`FLOAT`): Billable technician labor hours.
- `labor_cost` (`FLOAT`): Dealership labor charge.
- `parts_cost` (`FLOAT`): Rollup of replaced parts cost for this order.
- `total_cost` (`FLOAT`): `labor_cost + parts_cost` (`$4,468,695.07` across all 6,104 orders).
- `customer_paid_amount` (`FLOAT`): Out-of-pocket amount paid by the vehicle owner (`$0.00` whenever `is_warranty_covered = TRUE`).
- `is_warranty_covered` (`BOOLEAN`): Canonical flag (`1,894` orders = `TRUE`) indicating OEM warranty absorption (`$1,591,386.85` total absorbed cost).
