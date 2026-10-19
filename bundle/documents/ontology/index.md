---
okf_version: "0.2"
title: "Domain Ontologies Index"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/ontology"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents"
  documentType: "knowledge-base-index"
---

# Domain Ontologies Index

## Purpose
Houses formal entity-relationship and state-machine ontologies across Manufacturing, Retail Sales, and After-Sales Warranty.

## Documents
- `documents/ontology/automotive-lifecycle-ontology`: End-to-end VIN lifecycle, dual-plant role (`build_plant_name` vs `part_source_plant_name`), and warranty entitlement state transitions.
