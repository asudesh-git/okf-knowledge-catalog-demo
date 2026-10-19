---
okf_version: "0.2"
title: "Automotive Enterprise Knowledge Base (OKF v0.2)"
type: "knowledge-base"
status: "draft"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "2026-10-19T15:40:00Z"
sources:
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_sales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_manufacturing_data"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/agents"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  documentType: "knowledge-base"
---

# Automotive Enterprise Knowledge Base (OKF v0.2)

## Purpose
Progressive-disclosure root routing document for the `sa-demo-agentic` Automotive Enterprise Lakehouse covering After-Sales Warranty (`auto_aftersales_data`), Vehicle Sales (`auto_sales_data`), and Plant Manufacturing (`auto_manufacturing_data`).

## Navigation Spine
1. **BigQuery Asset Context Overlays (`assets/bigquery/sa-demo-agentic/*`)**:
   - `auto_aftersales_data`: `warranty_claims`, `service_orders`, `service_parts_usage`, `vehicle_ownership`, `technicians`, `recall_campaigns`.
   - `auto_sales_data`: `vehicle_sales`, `vehicle_models`, `dealerships`, `customer_identity_crosswalk`.
   - `auto_manufacturing_data`: `plants`, `assembly_line_status`, `parts_inventory`, `quality_inspections`.
2. **Domain Ontology & Tribal Knowledge (`documents/*`)**:
   - `documents/ontology/automotive-lifecycle-ontology`: End-to-end VIN lifecycle, warranty entitlement state machine, and supplier chargeback recovery rules.
   - `documents/concepts/net-oem-warranty-burden`: Canonical formula for Realized Warranty Cost, 70% Supplier Chargeback Recovery, and Unrecovered Supplier Leakage.
   - `documents/concepts/active-warranty-entitlement-fleet`: Secondary-market transfer rules (`4,650` entitled vehicles out of `5,000`).
   - `documents/concepts/dimension-catalog-padding-guardrail`: Mandatory filter for the 259-row padded dimension tables (`plants`, `vehicle_models`, `dealerships`).
   - `documents/playbooks/cross-domain-root-cause-playbook`: Diagnostic SQL playbook linking manufacturing plant telemetry to dealership warranty claims.
   - `documents/learnings/warranty-fanout-and-absorption-learnings`: Validated analyst corrections preventing `service_parts_usage` join fan-out and `service_type` undercounting.
