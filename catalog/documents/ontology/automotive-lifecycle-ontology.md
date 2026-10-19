---
okf_version: "0.2"
title: "Automotive Enterprise Lifecycle Ontology"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/ontology/automotive-lifecycle-ontology"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/ontology"
  documentType: "knowledge-base"
---

# Automotive Enterprise Lifecycle Ontology

## Purpose
Defines the authoritative domain ontology connecting **Manufacturing Plants**, **Vehicle Models**, **Sold VINs**, **Dealership Service Orders**, **Replaced Parts**, and **Warranty Claims** in `sa-demo-agentic`.

## Dual Plant Attribution Ontology
Every warranty claim (`warranty_claims`) links to `auto_manufacturing_data.plants` along **two distinct causal axes**:
1. **Final Vehicle Assembly Axis (`build_plant_name = plants.plant_name`)**: Identifies the facility that assembled the complete vehicle (`vin`). Governs internal OEM assembly quality (`WHERE supplier_fault = FALSE`).
2. **Component Manufacturing Axis (`part_source_plant_name = plants.plant_name`)**: Identifies the stamping/powertrain facility or external tier-1 vendor hub that produced the failed component (`part_number`). Governs component containment and supplier recovery (`WHERE supplier_fault = TRUE`).

## Warranty Adjudication & Supplier Recovery Ontology
- **Gross Claim Volume (`$1,798,306.90`)** is divided into:
  - **Realized Warranty Cost (`claim_status = 'Approved'`, `$1,254,786.01`)**
  - **Open Warranty Reserve Exposure (`claim_status IN ('Pending', 'Under Review')`, `$404,016.42`)**
  - **Denied Claims (`claim_status = 'Denied'`, `$139,504.47`, zero OEM liability)**
- **Supplier Chargeback Contract Rule**: For `'Approved'` claims with `supplier_fault = TRUE` (`$464,191.35`), the OEM recovers **70% of `claim_amount`** (`$42,415.72`) when `LOGICAL_AND(defective_part_returned) = TRUE` on `service_parts_usage` for that `service_order_id`. When any replaced part on the order has `defective_part_returned = FALSE`, the 70% recovery (`$282,518.23`) is forfeited as **Unrecovered Supplier Leakage**, resulting in a **Net OEM Warranty Burden of `$1,212,370.29`**.
