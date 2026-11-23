---
okf_version: "0.2"
title: "Concept: Cross-Project Telematics & Avoidable OTA Hardware Replacement Leakage"
type: "knowledge-base"
status: "stable"
generated:
  by: "agent:okf-cross-project-federation"
  at: "2026-11-19T00:19:30Z"
verified:
  - by: "human:asudesh@google.com"
    at: "2026-11-19T00:19:30Z"
sources:
  - "bigquery://projects/sa-demo-kc/datasets/auto_connected_telematics_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_aftersales_data"
  - "bigquery://projects/sa-demo-agentic/datasets/auto_manufacturing_data"
x-kcmd:
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts/cross-project-telematics-warranty-correlation"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts"
  documentType: "knowledge-base"
---

# Concept: Cross-Project Telematics & Avoidable OTA Hardware Replacement Leakage (`sa-demo-kc` <-> `sa-demo-agentic`)

Defines how Knowledge Catalog and Knowledge Studio unify Connected Vehicle Telematics in spoke project **`sa-demo-kc`** (`auto_connected_telematics_data`) with Dealership Warranty & Manufacturing Lineage in hub project **`sa-demo-agentic`** (`auto_aftersales_data`, `auto_manufacturing_data`).

## Canonical Metric: Avoidable OTA Hardware Replacement Leakage
- **Business Definition**: Approved dealership warranty spend (`sa-demo-agentic.auto_aftersales_data.warranty_claims.claim_status = 'Approved'`) on physical part replacements where the vehicle (`vin`) had emitted a verified OTA-remediable diagnostic alert (`telemetry_stream_status = 'VERIFIED_VEHICLE_ALERT' AND ota_remediable = TRUE` in `sa-demo-kc.auto_connected_telematics_data.connected_vehicle_dtc_events`) for that `part_name`, while an active OTA firmware campaign (`deployment_status = 'Active Rollout'`) had **not yet been installed** (`COALESCE(install_status, 'Unenrolled') != 'Installed'` in `vin_ota_deployments`).
- **Mandatory Anti-Fan-Out Guardrails**:
  1. Exclude `'BENCH_CALIBRATION_NOISE'` rows in `connected_vehicle_dtc_events` (`telemetry_stream_status = 'VERIFIED_VEHICLE_ALERT'`).
  2. Pre-aggregate `connected_vehicle_dtc_events` and `vin_ota_deployments` to `(vin, part_name)` before joining to `warranty_claims` (or query `sa-demo-agentic.auto_aftersales_data.v_cross_project_ota_warranty_leakage` where `is_avoidable_ota_hardware_claim = TRUE`).
  3. When joining `GRAPH_TABLE(\`sa-demo-kc.auto_connected_telematics_data.connected_telematics_ota_graph\`)` with `GRAPH_TABLE(\`sa-demo-agentic.auto_aftersales_data.warranty_supplier_chargeback_graph\`)`, pre-aggregate the `warranty_supplier_chargeback_graph` path at `(vin, claim_id, claim_amount, part_name)` with `COUNT(DISTINCT subcomponent_lot_id)` and `COUNT(DISTINCT supplier_plant)` before `SUM(claim_amount)` so multi-batch BOM lineage never multiplies `claim_amount`.
