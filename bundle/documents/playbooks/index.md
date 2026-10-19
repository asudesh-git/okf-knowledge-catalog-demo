---
okf_version: "0.2"
title: "Analytical Playbooks Index"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/playbooks"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents"
  documentType: "knowledge-base-index"
---

# Analytical Playbooks Index

## Purpose
Step-by-step SQL investigation playbooks for multi-dataset root-cause analysis.

## Playbooks
- `documents/playbooks/cross-domain-root-cause-playbook`: Tracing field warranty spikes back to assembly plant OEE and component source plants.
