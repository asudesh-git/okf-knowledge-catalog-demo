---
okf_version: "0.2"
title: "Net OEM Warranty Burden & Supplier Chargeback Recovery"
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
  name: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts/net-oem-warranty-burden"
  entryType: "projects/655216118709/locations/global/entryTypes/document"
  parentEntry: "projects/sa-demo-agentic/locations/us-central1/entryGroups/auto-enterprise-okf-context-set/entries/documents/concepts"
  documentType: "knowledge-base"
---

# Net OEM Warranty Burden & Supplier Chargeback Recovery

## Purpose
Establishes the CFO-approved accounting formula for **Realized Warranty Cost**, **Recoverable Supplier Chargeback**, **Unrecovered Supplier Leakage**, and **Net OEM Warranty Burden**.

## Mathematical Specification
1. **Realized Warranty Cost**:
   $$\text{Realized Warranty Cost} = \sum_{c \in \text{Approved}} \text{claim\_amount}_c = \$1,254,786.01$$
2. **Order-Level Core Return Compliance (`all_defective_parts_returned`)**:
   Pre-aggregate `service_parts_usage` by `service_order_id` using `LOGICAL_AND(defective_part_returned)`.
3. **Recoverable Supplier Chargeback**:
   $$\text{Recoverable Chargeback} = \sum_{\substack{c \in \text{Approved} \\ \text{supplier\_fault}=\text{TRUE} \\ \text{all\_returned}=\text{TRUE}}} 0.70 \times \text{claim\_amount}_c = \$42,415.72$$
4. **Unrecovered Supplier Leakage**:
   $$\text{Unrecovered Leakage} = \sum_{\substack{c \in \text{Approved} \\ \text{supplier\_fault}=\text{TRUE} \\ \text{all\_returned}=\text{FALSE}}} 0.70 \times \text{claim\_amount}_c = \$282,518.23$$
5. **Net OEM Warranty Burden**:
   $$\text{Net OEM Warranty Burden} = \$1,254,786.01 - \$42,415.72 = \$1,212,370.29$$
