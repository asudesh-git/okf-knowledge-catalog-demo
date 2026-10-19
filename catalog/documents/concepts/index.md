---
okf_version: "0.2"
title: "Business Concepts & Metric Rules Index"
type: "knowledge-base-index"
status: "draft"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "2026-10-19T15:40:00Z"
sources:
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_sales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_manufacturing_data"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents"
  documentType: "knowledge-base-index"
---

# Business Concepts & Metric Rules Index

## Purpose
Defines canonical financial formulas, fleet eligibility rules, and schema guardrails.

## Concepts
- `documents/concepts/net-oem-warranty-burden`: Realized Warranty Cost, 70% Supplier Chargeback Recovery, and Unrecovered Supplier Leakage.
- `documents/concepts/active-warranty-entitlement-fleet`: Secondary-market resale transfer rule (`4,650` entitled vehicles).
- `documents/concepts/dimension-catalog-padding-guardrail`: Mandatory filter for 259-row padded dimension tables (`7` active plants, `8` active models, `8` active dealerships).
