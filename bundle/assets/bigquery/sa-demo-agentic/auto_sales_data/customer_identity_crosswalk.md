---
okf_version: "0.2"
title: "customer_identity_crosswalk"
type: "context-overlay"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/assets/bigquery/sa-demo-agentic/auto_sales_data"
  documentType: "context-overlay"
---

# Context Overlay: `sa-demo-agentic.auto_sales_data.customer_identity_crosswalk`

## Purpose
Identity resolution bridge (`5,000` rows) mapping `auto_customer_id` (which stores the vehicle `vin` / `CUST-*` key) to `global_loyalty_id` for cross-cloud CRM attribution.

## Columns & Metrics
- `auto_customer_id` (`STRING`, PK): Local automotive customer/vehicle key.
- `global_loyalty_id` (`STRING`): Enterprise cross-cloud loyalty identifier (`LOYALTY-*`).
- `email_sha256` (`STRING`): Hashed customer email for clean-room matching.
- `identity_provider` (`STRING`): Resolution source (`LiveRamp`, `UID2`, `Internal_Deterministic`).
- `match_confidence` (`FLOAT`): Probabilistic match score (`0.0..1.0`). **MANDATORY GUARDRAIL**: Filter `WHERE match_confidence >= 0.85` for executive LTV and campaign attribution.
- `last_verified_timestamp` (`TIMESTAMP`): Last identity graph verification timestamp.
