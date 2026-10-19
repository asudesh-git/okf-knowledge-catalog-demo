---
okf_version: "0.2"
title: "Automotive Enterprise OKF v0.2 Context Set Index"
type: "knowledge-base-index"
status: "stable"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "2026-10-19T15:40:00Z"
verified:
  - by: "human:asudesh@google.com"
    at: "2026-10-19T15:40:00Z"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/index"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  documentType: "knowledge-base-index"
---

# Automotive Enterprise OKF v0.2 Context Set Index (`sa-demo-agentic`)

## Purpose
Root Open Knowledge Format (`OKF v0.2`) backbone index cataloging all **26 progressive-disclosure entries** and **13 semantic/join entry links** across `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.

## Bundle Manifest (32 Entries)

| Entry ID | OKF Document Type | Status | Title |
| :--- | :--- | :--- | :--- |
| [`agents`](agents.md) | `knowledge-base` | `draft` | Automotive Enterprise Knowledge Base (OKF v0.2) |
| [`assets`](assets/index.md) | `knowledge-base-index` | `draft` | Data Assets Index |
| [`assets/bigquery`](assets/bigquery/index.md) | `knowledge-base-index` | `draft` | BigQuery System Index |
| [`assets/bigquery/sa-demo-agentic`](assets/bigquery/sa-demo-agentic/index.md) | `knowledge-base-index` | `draft` | Project sa-demo-agentic Dataset Index |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/index.md) | `knowledge-base-index` | `draft` | Dataset auto_aftersales_data |
| [`assets/bigquery/sa-demo-agentic/auto_sales_data`](assets/bigquery/sa-demo-agentic/auto_sales_data/index.md) | `knowledge-base-index` | `draft` | Dataset auto_sales_data |
| [`assets/bigquery/sa-demo-agentic/auto_manufacturing_data`](assets/bigquery/sa-demo-agentic/auto_manufacturing_data/index.md) | `knowledge-base-index` | `draft` | Dataset auto_manufacturing_data |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims.md) | `context-overlay` | `stable` | warranty_claims |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders.md) | `context-overlay` | `stable` | service_orders |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage.md) | `context-overlay` | `stable` | service_parts_usage |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership.md) | `context-overlay` | `stable` | vehicle_ownership |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians.md) | `context-overlay` | `stable` | technicians |
| [`assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns`](assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns.md) | `context-overlay` | `stable` | recall_campaigns |
| [`assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales`](assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales.md) | `context-overlay` | `stable` | vehicle_sales |
| [`assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models`](assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models.md) | `context-overlay` | `stable` | vehicle_models |
| [`assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships`](assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships.md) | `context-overlay` | `stable` | dealerships |
| [`assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk`](assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk.md) | `context-overlay` | `stable` | customer_identity_crosswalk |
| [`assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants`](assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants.md) | `context-overlay` | `stable` | plants |
| [`assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status`](assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status.md) | `context-overlay` | `stable` | assembly_line_status |
| [`assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory`](assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory.md) | `context-overlay` | `stable` | parts_inventory |
| [`assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections`](assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections.md) | `context-overlay` | `stable` | quality_inspections |
| [`documents`](documents/index.md) | `knowledge-base-index` | `draft` | Domain Knowledge & Tribal Documents Index |
| [`documents/ontology`](documents/ontology/index.md) | `knowledge-base-index` | `draft` | Domain Ontologies Index |
| [`documents/ontology/automotive-lifecycle-ontology`](documents/ontology/automotive-lifecycle-ontology.md) | `knowledge-base` | `stable` | Automotive Enterprise Lifecycle Ontology |
| [`documents/concepts`](documents/concepts/index.md) | `knowledge-base-index` | `draft` | Business Concepts & Metric Rules Index |
| [`documents/concepts/net-oem-warranty-burden`](documents/concepts/net-oem-warranty-burden.md) | `knowledge-base` | `stable` | Net OEM Warranty Burden & Supplier Chargeback Recovery |
| [`documents/concepts/active-warranty-entitlement-fleet`](documents/concepts/active-warranty-entitlement-fleet.md) | `knowledge-base` | `stable` | Active Warranty Entitlement Fleet Rule |
| [`documents/concepts/dimension-catalog-padding-guardrail`](documents/concepts/dimension-catalog-padding-guardrail.md) | `knowledge-base` | `stable` | Dimension Catalog Padding Guardrail (259 Rows Trap) |
| [`documents/playbooks`](documents/playbooks/index.md) | `knowledge-base-index` | `draft` | Analytical Playbooks Index |
| [`documents/playbooks/cross-domain-root-cause-playbook`](documents/playbooks/cross-domain-root-cause-playbook.md) | `knowledge-base` | `stable` | Cross-Domain Warranty & Manufacturing Root-Cause Playbook |
| [`documents/learnings`](documents/learnings/index.md) | `knowledge-base-index` | `draft` | Curation Loop Learnings Index |
| [`documents/learnings/warranty-fanout-and-absorption-learnings`](documents/learnings/warranty-fanout-and-absorption-learnings.md) | `knowledge-base` | `stable` | Warranty Join Fan-Out & Service Absorption Learnings |
