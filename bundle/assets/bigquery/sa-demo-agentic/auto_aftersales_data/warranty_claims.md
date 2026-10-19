---
okf_version: "0.2"
title: "warranty_claims"
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
  - target: "vehicle_ownership.md"
    type: "schema-join"
    source_column: "vin"
    target_column: "vin"
  - target: "../auto_manufacturing_data/plants.md"
    type: "schema-join"
    source_column: "build_plant_name"
    target_column: "plant_name"
  - target: "../../../../documents/concepts/net-oem-warranty-burden.md"
    type: "related"
  - target: "../../../../documents/ontology/automotive-lifecycle-ontology.md"
    type: "related"
queries:
  - title: "Net OEM Warranty Burden & Supplier Recovery by Component"
    description: "Calculates Gross Submitted, Realized Approved Cost, 70% Recoverable Supplier Chargeback (requiring core return), Unrecovered Leakage, and Net OEM Burden."
    sql: |
      WITH parts_by_order AS (
        SELECT
          service_order_id,
          LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned
        FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage`
        GROUP BY service_order_id
      )
      SELECT
        w.failure_component,
        COUNTIF(w.claim_status = 'Approved') AS approved_claims,
        ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost,
        ROUND(SUM(CASE
          WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
          THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback,
        ROUND(SUM(CASE
          WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE
          THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage,
        ROUND(
          SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) -
          SUM(CASE
            WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
            THEN w.claim_amount * 0.70 ELSE 0 END),
          2
        ) AS net_oem_warranty_burden
      FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
      LEFT JOIN parts_by_order p USING (service_order_id)
      GROUP BY w.failure_component
      ORDER BY net_oem_warranty_burden DESC;
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_aftersales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_aftersales_data.warranty_claims`

## Purpose
Records financial warranty claims (`1,894` rows, 1 row per `claim_id` / `service_order_id`) submitted by dealerships for warranty-covered repairs. Central fact table for calculating **Realized Warranty Cost** (`$1,254,786.01`), **Open Warranty Reserve Exposure** (`$404,016.42`), and **Net OEM Warranty Burden** after Supplier Chargeback Recovery.

## Columns & Metrics
- `claim_id` (`INTEGER`, PK): Unique warranty claim identifier (`1..1894`).
- `service_order_id` (`INTEGER`, FK -> `service_orders.service_order_id`): 1:1 link to the originating warranty-covered dealership service visit.
- `vin` (`STRING`, FK -> `vehicle_ownership.vin`, `vehicle_sales.vin`): 17-character Vehicle Identification Number.
- `claim_date` (`DATE`): Date the warranty claim was filed (`30` days after `service_orders.service_date`).
- `failure_component` (`STRING`): Failed vehicle subsystem (`Engine`, `Battery`, `Electrical`, `Brakes`, `Transmission`, `Suspension`, `HVAC`, `Infotainment`, `Steering`, `Exhaust`, `Fuel System`).
- `claim_amount` (`FLOAT`): Total dollar value requested on the claim. **CRITICAL CAVEAT**: Raw `SUM(claim_amount)` (`$1,798,306.90`) includes unadjudicated and rejected claims. Always filter `claim_status = 'Approved'` (`$1,254,786.01`) for realized cost.
- `claim_status` (`STRING`): Adjudication state:
  - `'Approved'` (`1,331` rows, `$1,254,786.01`): Realized financial warranty expense.
  - `'Pending'` (`233` rows, `$217,261.21`) & `'Under Review'` (`186` rows, `$186,755.21`): Open warranty reserve exposure (`$404,016.42` combined).
  - `'Denied'` (`144` rows, `$139,504.47`): Rejected claims; `$0` OEM financial liability.
- `build_plant_name` (`STRING`, FK -> `plants.plant_name`): Final assembly plant where the vehicle (`vin`) was assembled. Use for **Assembly Plant Quality** metrics (`WHERE supplier_fault = FALSE`).
- `part_source_plant_name` (`STRING`, FK -> `plants.plant_name`): Component manufacturing plant that produced the defective replacement part. Use for **Component Plant Defect** tracing.
- `supplier_fault` (`BOOLEAN`): `TRUE` (`501` approved claims, `$464,191.35`) when the failure was caused by an external tier-1 supplier defect; `FALSE` (`830` approved claims, `$790,594.66`) when caused by internal OEM assembly/design.
- **Metric — Recoverable Supplier Chargeback (`recoverable_supplier_chargeback`)**: When `claim_status = 'Approved' AND supplier_fault = TRUE`, the OEM recovers `0.70 * claim_amount` **ONLY IF** all replaced parts on `service_order_id` have `defective_part_returned = TRUE` in `service_parts_usage` (pre-aggregated by `service_order_id`).
