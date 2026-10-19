---
okf_version: "0.2"
title: "Warranty Join Fan-Out & Service Absorption Learnings"
type: "knowledge-base"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/learnings/warranty-fanout-and-absorption-learnings"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/learnings"
  documentType: "knowledge-base"
---

# Warranty Join Fan-Out & Service Absorption Learnings

## Purpose
Prevents the three most common SQL calculation errors when querying `sa-demo-agentic.auto_aftersales_data`:

## Verified Guardrails
1. **Never join `warranty_claims` to `service_parts_usage` without pre-aggregating `service_parts_usage` to `service_order_id` grain**: Direct join multiplies `claim_amount` by 1.77x (`$2,226,419.83` instead of `$1,254,786.01`).
2. **Never filter `service_orders` by `service_type = 'Warranty Repair'` to measure total warranty-covered service cost**: Always filter `WHERE is_warranty_covered = TRUE` (`$1,591,386.85` across 1,894 orders vs `$826,977.80` on 922 `'Warranty Repair'` orders).
3. **Always reconcile `customer_identity_crosswalk` with `match_confidence >= 0.85` and `promo_code_received IN ('PLATINUM-VIP', 'PLATNUM-VIP')`**.
