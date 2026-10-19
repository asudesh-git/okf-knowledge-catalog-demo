---
okf_version: "0.2"
title: "Domain Knowledge & Tribal Documents Index"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/agents"
  documentType: "knowledge-base-index"
---

# Domain Knowledge & Tribal Documents Index

## Purpose
Organizes enterprise domain ontologies, semantic business concepts, diagnostic SQL playbooks, and analyst curation learnings.

## Sub-Collections
- `documents/ontology`: Domain entity lifecycle & state machine rules.
- `documents/concepts`: Canonical business metrics, supplier chargeback formulas, and dimension padding guardrails.
- `documents/playbooks`: Cross-dataset analytical SQL playbooks.
- `documents/learnings`: Empirical corrections from Conversational Analytics agent benchmarking.
