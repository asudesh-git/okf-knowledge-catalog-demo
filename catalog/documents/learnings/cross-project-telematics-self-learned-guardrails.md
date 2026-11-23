---
okf_version: "0.2"
title: "Self-Learned: Cross-Project Telematics & Dual-Graph Guardrails"
type: "learning"
status: "stable"
generated:
  by: "agent:conversation_learner"
  at: "2026-11-19T02:20:00Z"
sources:
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data/tables/automotive_agent_events_v2"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/learnings/cross-project-telematics-self-learned-guardrails"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/learnings"
  documentType: "learning"
---

# Self-Learned Guardrails: Cross-Project Telematics & Dual-Graph Queries

Captured recurring analyst corrections from BigQuery Agent Analytics (`sa-demo-agentic.auto_aftersales_data.automotive_agent_events_v2`):
1. Always filter `sa-demo-kc.auto_connected_telematics_data.connected_vehicle_dtc_events` by `telemetry_stream_status = 'VERIFIED_VEHICLE_ALERT'` so lab `'BENCH_CALIBRATION_NOISE'` pings are excluded.
2. Pre-aggregate DTC alerts and OTA deployments to `(vin, part_name)` before joining `warranty_claims` so multiple telemetry pings never fan out claim spend.
3. Deduplicate `warranty_supplier_chargeback_graph` rows at `(vin, claim_id, claim_amount, part_name)` before joining `connected_telematics_ota_graph` so multi-batch supplier lineage never multiplies `claim_amount`.
