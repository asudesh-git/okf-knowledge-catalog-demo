---
okf_version: "0.2"
title: "Project sa-demo-agentic Dataset Index"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery"
  documentType: "knowledge-base-index"
---

# Project `sa-demo-agentic` Dataset Index

## Purpose
Contains the three core `us-central1` domains of the Automotive Enterprise Lakehouse.

## Datasets
- `assets/bigquery/sa-demo-agentic/auto_aftersales_data`: Dealership service orders, warranty claims, parts replacements, recalls, and VIN ownership entitlement.
- `assets/bigquery/sa-demo-agentic/auto_sales_data`: Vehicle sales, model catalog, dealership network, and cross-cloud identity crosswalk.
- `assets/bigquery/sa-demo-agentic/auto_manufacturing_data`: Assembly & component plants, line OEE telemetry, parts inventory, and quality inspections.
