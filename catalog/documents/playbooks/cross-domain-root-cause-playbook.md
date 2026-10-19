---
okf_version: "0.2"
title: "Cross-Domain Warranty & Manufacturing Root-Cause Playbook"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/playbooks/cross-domain-root-cause-playbook"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/playbooks"
  documentType: "knowledge-base"
---

# Cross-Domain Warranty & Manufacturing Root-Cause Playbook

## Purpose
Guides Data Agents through a 4-stage investigation joining `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.

## Investigation Protocol
1. **Isolate Approved Spend & Split Fault Axis**: Query `warranty_claims` with `claim_status = 'Approved'` and segment into **OEM Assembly Fault (`supplier_fault = FALSE`, `$790,594.66`)** vs **Supplier Component Fault (`supplier_fault = TRUE`, `$464,191.35`)**.
2. **Attribute Assembly Faults to `build_plant_name`**: Join `warranty_claims.build_plant_name = plants.plant_name` and correlate with `assembly_line_status.operational_efficiency` and `quality_inspections`.
3. **Attribute Component Faults to `part_source_plant_name` & Audit Dealership Core Return**: Pre-aggregate `service_parts_usage` by `service_order_id` (`LOGICAL_AND(defective_part_returned)`) and identify which dealerships (`service_orders.dealership_id`) are failing to return defective supplier cores (`$282,518.23` in forfeited supplier recovery).
