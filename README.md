# Open Knowledge Format (`OKF v0.2`) + Dataplex Knowledge Catalog & Knowledge Studio Showcase (`sa-demo-agentic`)

This repository demonstrates how the **Open Knowledge Format (`OKF v0.2`)**, **Dataplex Knowledge Catalog Context Sets**, and **Knowledge Studio** transform raw, ambiguous enterprise tables into an agent-ready semantic knowledge graph in GCP project **`sa-demo-agentic`**.

---

## 1. Repository Layout

```text
okf-knowledge-catalog-demo/
├── catalog.yaml                         # kcmd configuration (layout: okf)
├── okf_graph_visualizer.html            # Standalone interactive HTML5 Knowledge Graph visualizer
├── raw-tribal-knowledge/                # 6 categories of raw tribal knowledge for Knowledge Studio upload
│   ├── 01_automotive_domain_ontology.md
│   ├── 02_business_metrics_and_glossary.md
│   ├── 03_schema_caveats_and_traps.md
│   ├── 04_join_rules_and_grain.md
│   ├── 05_verified_golden_sql_templates.md
│   └── 06_analyst_feedback_learnings.md
├── bundle/                              # Strict OKF v0.2 progressive-disclosure bundle
│   ├── index.md                         # OKF v0.2 Backbone Index
│   ├── log.md                           # OKF v0.2 Curation & Verification Log
│   ├── agents.md                        # Progressive-disclosure root routing document
│   ├── assets/bigquery/sa-demo-agentic/ # 14 BigQuery Table Context Overlays + Dataset Indexes
│   └── documents/                       # Curated Ontologies, Concepts, Playbooks, & Learnings
├── catalog/                             # kcmd push/pull mirror of the OKF v0.2 bundle
└── scripts/
    ├── build_okf_bundle.py              # Compiles raw tribal knowledge into OKF v0.2 & kcmd trees
    └── publish_to_knowledge_catalog.py  # Publishes Glossary, Context Set, & BQ Schema to sa-demo-agentic
```

---

## 2. Existing Data Agents in `sa-demo-agentic` to Showcase OKF Value

Your project `sa-demo-agentic` already contains live **Conversational Analytics Data Agents** (`projects/sa-demo-agentic/locations/global/dataAgents/*`) plus **Knowledge Studio's built-in Explore & Enrich agents**:

| Data Agent ID (`locations/global/dataAgents/*`) | Display Name | Bound BigQuery Datasets (`sa-demo-agentic`) | Best OKF + Knowledge Catalog Showcase Angle |
| :--- | :--- | :--- | :--- |
| **`auto-aftersales-quality-agent`** | *Automotive After-Sales, Warranty & Quality Analyst* | `auto_aftersales_data` (6 tables), `auto_sales_data` (4 tables), `auto_manufacturing_data` (4 tables) | **Primary Showcase Agent**: Previously relied on an 85-line brittle prompt because `auto_aftersales_data` had **0 column descriptions**. With OKF v0.2 Context Overlays + Tribal Knowledge, it resolves **Net OEM Warranty Burden (`$1,212,370.29`)**, **Unrecovered Supplier Leakage (`$282,518.23`)**, **Active Warranty Entitlement Fleet (`4,650` VINs)**, and **OEM Warranty-Covered Service Absorption (`$1,591,386.85`)**. |
| **`automotive_cross_cloud_agent`** (and `borderless_lakehouse_agent`) | *Borderless Lakehouse & Cross-Cloud Analytics Agent* | `auto_sales_data.vehicle_sales_transactions`, `auto_sales_lakehouse.customer_identity_crosswalk`, `databricks_federation.crm_data.crm_campaign_history` | **Cross-Cloud Identity & Typo Guardrail**: Demonstrates OKF's `match_confidence >= 0.85` identity threshold and legacy campaign code reconciliation (`'PLATINUM-VIP'` + `'PLATNUM-VIP'`). |
| **`ford-manufacturing-360-agent`** (and `ford-quality-compliance-agent`) | *Ford Manufacturing 360 — Executive Operations Agent* | `m360_ford` (10 tables) | **Manufacturing Plant & Supplier Telemetry**: Contrasts hardcoded system instructions against governed, reusable Knowledge Catalog Context Sets. |
| **Knowledge Studio Built-in Explore Agent** | *Knowledge Studio Chat (`dataplex/studio`)* | Dynamically grounded on `auto-enterprise-okf-context-set` (`us-central1`) | **Direct Progressive-Disclosure Traversal**: Traverses `agents` -> `assets/bigquery/sa-demo-agentic/...` -> `schema-join` & `related` links -> `documents/concepts/*` and `@dataplex` Business Glossary terms. |

---

## 3. Empirical "Before OKF vs. After OKF" Benchmarks in `sa-demo-agentic`

| Business Question / Analytical Trap | Without OKF (Naive Schema-Only SQL) | With OKF v0.2 + Knowledge Catalog Context Set | Root Cause Captured in OKF Tribal Knowledge |
| :--- | :--- | :--- | :--- |
| **1. Realized Warranty Cost & Net OEM Warranty Burden** | **`$1,798,306.90`** (unfiltered sum) or **`$2,226,419.83`** (1.77x fan-out when joined to `service_parts_usage`) | **Realized Cost**: **`$1,254,786.01`** (`1,331` Approved claims)<br>**Recoverable Supplier Chargeback (70%)**: **`$42,415.72`**<br>**Unrecovered Supplier Leakage**: **`$282,518.23`**<br>**Net OEM Burden**: **`$1,212,370.29`** | Filters `claim_status = 'Approved'`, pre-aggregates `service_parts_usage` by `service_order_id` (`LOGICAL_AND(defective_part_returned)`), and applies the 70% supplier chargeback contract rule. |
| **2. Total Dealership Service Cost Absorbed Under Warranty** | **`$826,977.80`** (`922` orders where `service_type = 'Warranty Repair'`) | **`$1,591,386.85`** (`1,894` orders where `is_warranty_covered = TRUE`) | Captures `690` covered `'Repair'` orders (`$558,639.28`) and `282` covered `'Recall Service'` orders (`$205,769.77`) where `customer_paid_amount = 0`. |
| **3. Active Fleet Entitled to OEM Warranty Coverage** | **`5,000`** (by date alone) or **`4,582`** (`ownership_status = 'Active'` only) | **`4,650` vehicles** (`4,582` Active + `68` Transferred with transferable extended warranty) | Secondary-market `'Transferred'` vehicles (`304`) lose standard factory coverage unless `extended_warranty_purchased = TRUE` (`68` VINs); `'Buyback'` (`114` VINs) are excluded. |
| **4. Active Manufacturing Plant Count & Nameplate Capacity** | **`259` plants** / **`45,860,000` units/yr** (32x distortion from ERP catalog padding) | **`7` active plants** / **`1,250,000` units/yr** | `plants` (`259` rows), `vehicle_models` (`259` rows), and `dealerships` (`259` rows) contain 251–252 unallocated catalog padding rows. |

---

## 4. Importing & Using Context Sets in Knowledge Studio (`sa-demo-agentic`)

### Option A: Explore the Already-Published Context Set in Knowledge Studio
1. Open **Knowledge Studio** in Google Cloud Console:
   `https://console.cloud.google.com/dataplex/studio?project=sa-demo-agentic`
2. In the **Explore** tab, select Location **`us-central1`** and choose Context Set:
   - `auto-enterprise-okf-context-set` (*Automotive Enterprise OKF v0.2 Context Set*) or
   - `enrichment-entry-group`
3. Inspect the hierarchical tree (`agents`, `assets/bigquery/sa-demo-agentic/...`, `documents/ontology/...`, `documents/concepts/...`, `documents/playbooks/...`, `documents/learnings/...`) and query the **Explore Chat Agent** with the benchmark prompts below.

### Option B: Run the Knowledge Studio "Enrich" Wizard with GitHub (`asudesh-git`) or Raw Tribal Docs
1. Push this repository to `https://github.com/asudesh-git/okf-knowledge-catalog-demo`:
   ```bash
   cd ~/ace/okf-knowledge-catalog-demo
   git push -u origin main
   ```
2. In **Knowledge Studio** (`https://console.cloud.google.com/dataplex/studio?project=sa-demo-agentic`), switch to the **Enrich** tab and click **New Enrichment Job**:
   - **Step 1 (Scope)**: Choose **Select existing Context Set** (`auto-enterprise-okf-context-set` or `enrichment-entry-group` in `us-central1`) to pre-populate the 14 BigQuery tables across `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.
   - **Step 2 (Sources)**:
     - **Upload Documents**: Upload the 6 markdown files from `raw-tribal-knowledge/` (or point to a GCS bucket containing them).
     - **Connect GitHub Repository**: Enter `https://github.com/asudesh-git/okf-knowledge-catalog-demo` (branch `main`).
   - **Step 3 (Review & Publish)**: Review the generated OKF v0.2 diffs (`status: draft` -> `status: stable`, `verified` stamp) and click **Publish to Knowledge Catalog**.
