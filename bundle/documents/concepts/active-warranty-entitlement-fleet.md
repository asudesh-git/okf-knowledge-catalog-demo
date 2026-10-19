---
okf_version: "0.2"
title: "Active Warranty Entitlement Fleet Rule"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts/active-warranty-entitlement-fleet"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts"
  documentType: "knowledge-base"
---

# Active Warranty Entitlement Fleet Rule

## Purpose
Defines which vehicles in `sa-demo-agentic.auto_aftersales_data.vehicle_ownership` (`5,000` total VINs) are actively entitled to OEM warranty coverage (`4,650` vehicles).

## Entitlement Rules by `ownership_status`
- `'Active'` (`4,582` VINs): **Entitled** when `warranty_end_date >= CURRENT_DATE()`.
- `'Transferred'` (`304` VINs): Standard 3-year factory warranty does NOT transfer to second-hand buyers. **Entitled ONLY IF `extended_warranty_purchased = TRUE` (`68` VINs)**; the remaining `236` transferred vehicles are out of coverage.
- `'Buyback'` (`114` VINs): Lemon-law/manufacturer buybacks; **Never entitled** to active customer warranty coverage.
- **Total Active Entitled Fleet**: `4,582 + 68 = 4,650` vehicles.
