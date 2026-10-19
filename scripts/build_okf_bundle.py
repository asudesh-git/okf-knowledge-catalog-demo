#!/usr/bin/env python3
"""Builds the Open Knowledge Format (OKF v0.2) Bundle, kcmd Catalog, and Raw Tribal Knowledge Corpus.

Target GCP Project: sa-demo-agentic (Project Number: 229419534491)
Target Datasets (us-central1):
  - auto_aftersales_data (6 tables)
  - auto_sales_data (7 tables)
  - auto_manufacturing_data (4 tables)
"""

import json
import os
from pathlib import Path

BASE_DIR = Path("/usr/local/google/home/asudesh/ace/okf-knowledge-catalog-demo")
PROJECT_ID = "sa-demo-agentic"
PROJECT_NUMBER = "229419534491"
DATAPLEX_TYPES_NUM = "655216118709"
LOCATION = "us-central1"
ENTRY_GROUP_ID = "auto-enterprise-okf-context-set"
TIMESTAMP = "2026-10-19T15:40:00Z"


def write_text(rel_path: str, content: str) -> None:
  path = BASE_DIR / rel_path
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content.strip() + "\n", encoding="utf-8")


def build_raw_tribal_knowledge() -> None:
  """Writes the 6 classes of raw tribal knowledge for ingestion into Knowledge Studio."""
  write_text(
      "raw-tribal-knowledge/01_automotive_domain_ontology.md",
      """# Automotive Enterprise Domain Ontology (Manufacturing -> Sales -> After-Sales)

## Core Domain Entities & Lifecycle Hierarchy

1. **Manufacturing Plant (`auto_manufacturing_data.plants`)**:
   - Physical assembly or component-stamping facility identified by `plant_id` and `plant_name`.
   - **Critical Dual-Role Relationship**: A plant can act as the **Vehicle Final Assembly Plant** (`warranty_claims.build_plant_name`, `vehicle_models.plant_id`) OR as the **Component Source Plant** (`warranty_claims.part_source_plant_name`, `parts_inventory.source_plant_id`).
   - Only **7 facilities** are active operational plants in the enterprise fleet; the remaining 252 rows in `plants` are unallocated global facility codes.

2. **Vehicle Model (`auto_sales_data.vehicle_models`)**:
   - Canonical vehicle platform defined by `model_id`, `model_name`, `category` (`SUV`, `Truck`, `Sedan`, `EV`), `msrp`, and primary assembly `plant_id`.
   - Only **8 vehicle models** (`model_id` 1 through 8) represent active production vehicles sold and serviced in the fleet.

3. **Sold & Entitled Vehicle (`auto_sales_data.vehicle_sales` <-> `auto_aftersales_data.vehicle_ownership`)**:
   - Uniquely identified across the enterprise by **VIN (`vin`)** (1:1 grain across `vehicle_sales` and `vehicle_ownership`, 5,000 vehicles).
   - **Warranty Entitlement State Machine**:
     - `ownership_status = 'Active'` (4,582 vehicles): Full factory and extended warranty entitlement.
     - `ownership_status = 'Transferred'` (304 vehicles): Secondary-market resale. Standard factory coverage terminates upon resale UNLESS `extended_warranty_purchased = TRUE` (68 vehicles retain transferable coverage; 236 lose coverage).
     - `ownership_status = 'Buyback'` (114 vehicles): Lemon-law or manufacturer buyback. Excluded from active customer warranty entitlement cohorts.
     - **True Active Warranty Entitlement Fleet** = `4,582 + 68 = 4,650` vehicles.

4. **Dealership Service Event (`auto_aftersales_data.service_orders`)**:
   - Repair, maintenance, or recall visit at an authorized dealership (`dealership_id`, `vin`, `technician_id`).
   - **Warranty Absorption Classification**: Any service order with `is_warranty_covered = TRUE` (1,894 orders across `service_type IN ('Warranty Repair', 'Repair', 'Recall Service')`) is absorbed by the OEM (`customer_paid_amount = 0.0`) and generates a corresponding `warranty_claims` record (`1:1` on `service_order_id`).

5. **Component Replacement (`auto_aftersales_data.service_parts_usage`)**:
   - Line-item parts (`part_number`, `part_name`, `part_category`, `quantity_used`, `unit_cost`, `total_part_cost`) installed during a `service_order_id`.
   - Tracks physical return of defective cores via `defective_part_returned` (`BOOL`), which governs supplier chargeback recovery eligibility.

6. **Warranty Claim & Supplier Recovery (`auto_aftersales_data.warranty_claims`)**:
   - Financial adjudication record (`claim_id`, `service_order_id`, `vin`, `claim_status`, `claim_amount`, `supplier_fault`).
   - Adjudication states: `'Approved'` (realized ledger cost), `'Pending'` and `'Under Review'` (open reserve exposure), `'Denied'` (rejected, zero OEM liability).
""",
  )

  write_text(
      "raw-tribal-knowledge/02_business_metrics_and_glossary.md",
      """# Enterprise Business Metrics & Canonical Formulas

## 1. Realized Warranty Cost (`realized_warranty_cost`)
- **Definition**: Adjudicated, financially recognized OEM warranty claim expenditure.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END)` on `sa-demo-agentic.auto_aftersales_data.warranty_claims`.
- **Empirical Baseline in `sa-demo-agentic`**: **`$1,254,786.01`** across **1,331 approved claims** (vs. `$1,798,306.90` gross unfiltered `SUM(claim_amount)` across all 1,894 claims).
- **Exclusions**: Must exclude `'Pending'` (`$217,261.21`), `'Under Review'` (`$186,755.21`), and `'Denied'` (`$139,504.47`).

## 2. Open Warranty Reserve Exposure (`open_warranty_exposure`)
- **Definition**: Unadjudicated warranty liability currently in review queues.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status IN ('Pending', 'Under Review') THEN claim_amount ELSE 0 END)`
- **Empirical Baseline in `sa-demo-agentic`**: **`$404,016.42`** (`233 Pending + 186 Under Review = 419 claims`).

## 3. Supplier Chargeback Recovery & Unrecovered Supplier Leakage (`net_oem_warranty_burden`)
- **Definition**: Under OEM Supplier Quality Assurance (SQA) contracts, when an `'Approved'` warranty claim is caused by a vendor defect (`supplier_fault = TRUE`), the OEM recovers **70% of `claim_amount`** from the supplier **ONLY IF** all defective parts replaced on that `service_order_id` were physically returned to the central teardown depot (`LOGICAL_AND(defective_part_returned) = TRUE` in `service_parts_usage`).
- **Unrecovered Supplier Leakage**: If any replaced part on an approved supplier-fault claim has `defective_part_returned = FALSE`, the supplier chargeback is forfeited (`0%` recovery), creating **Dealership Core-Return Leakage**.
- **Net OEM Warranty Burden Formula**:
  `Realized Warranty Cost - Recoverable Supplier Chargeback`

## 4. Total OEM Warranty-Covered Service Absorption (`oem_warranty_absorption`)
- **Definition**: Total dealership repair cost absorbed by the OEM across all warranty-covered visits in `service_orders`.
- **Canonical SQL Formula**:
  `SUM(total_cost - customer_paid_amount) WHERE is_warranty_covered = TRUE`
- **Empirical Baseline in `sa-demo-agentic`**: **`$1,591,386.85`** across **1,894 service orders**:
  - `service_type = 'Warranty Repair'` (922 orders): `$826,977.80`
  - `service_type = 'Repair' AND is_warranty_covered = TRUE` (690 goodwill/bumper-to-bumper covered repairs): `$558,639.28`
  - `service_type = 'Recall Service' AND is_warranty_covered = TRUE` (282 campaign repairs): `$205,769.77`

## 5. Active Warranty Entitlement Fleet (`active_warranty_entitlement_fleet`)
- **Definition**: Count of vehicles currently entitled to OEM warranty coverage.
- **Canonical SQL Filter**:
  `warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))`
- **Empirical Baseline in `sa-demo-agentic`**: **`4,650` vehicles** (`4,582 Active + 68 Transferred with transferable extended warranty`). Excludes `114 Buyback` and `236 Transferred without extended warranty`.

## 6. Assembly Plant Claim Rate per 1,000 Vehicles Built (`plant_claim_rate_per_1000_built`)
- **Definition**: Approved assembly-fault warranty claims per 1,000 vehicles produced by a final assembly plant.
- **Canonical SQL Formula**:
  `COUNTIF(w.claim_status = 'Approved' AND w.supplier_fault = FALSE) * 1000.0 / COUNT(DISTINCT v.vin)` joined via `w.build_plant_name = p.plant_name`.
""",
  )

  write_text(
      "raw-tribal-knowledge/03_schema_caveats_and_traps.md",
      """# Tacit Schema Caveats & Data Traps in `sa-demo-agentic`

## Trap 1: Dimension Table Catalog Padding (`259 rows` vs `7–8 active entities`)
- **Affected Tables**:
  - `sa-demo-agentic.auto_manufacturing_data.plants` (259 rows; only **7 active plants** have assembly lines, parts inventory, or vehicles built).
  - `sa-demo-agentic.auto_sales_data.vehicle_models` (259 rows; only **8 active models**, `model_id` 1..8, have vehicle sales or warranty claims).
  - `sa-demo-agentic.auto_sales_data.dealerships` (259 rows; only **8 active dealerships**, `dealership_id` 1..8, have sales or service orders).
- **Impact on AI Agents**: Any agent that runs `SELECT AVG(annual_capacity) FROM plants` or `LEFT JOIN vehicle_sales` from the dimension table without filtering to active operational entities dilutes per-entity averages by **32x** and outputs 251 empty rows.
- **Mandatory Guardrail**: Always `INNER JOIN` to fact tables (`vehicle_sales`, `service_orders`, `warranty_claims`, `assembly_line_status`) or filter `WHERE model_id BETWEEN 1 AND 8` / `dealership_id BETWEEN 1 AND 8`.

## Trap 2: `build_plant_name` vs `part_source_plant_name` in `warranty_claims`
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.warranty_claims`
- **Impact on AI Agents**: `warranty_claims` has two plant columns:
  - `build_plant_name`: Final assembly plant where the vehicle (`vin`) was built.
  - `part_source_plant_name`: Component plant that manufactured the failed part.
- **Mandatory Guardrail**:
  - For **Assembly Plant Quality Audits**, group by `build_plant_name` and filter `supplier_fault = FALSE`.
  - For **Component/Stamping Plant Defect Audits**, group by `part_source_plant_name`.

## Trap 3: `service_type = 'Warranty Repair'` Misses 48% of Covered Service Cost
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.service_orders`
- **Impact on AI Agents**: Filtering `WHERE service_type = 'Warranty Repair'` captures only 922 orders (`$826,977.80`), missing 690 `'Repair'` orders (`$558,639.28`) and 282 `'Recall Service'` orders (`$205,769.77`) that ALSO have `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Mandatory Guardrail**: Always use `WHERE is_warranty_covered = TRUE` when calculating OEM-absorbed dealership repair spend.

## Trap 4: Zero Native BigQuery Column Descriptions in `auto_aftersales_data`
- **Affected Dataset**: `sa-demo-agentic.auto_aftersales_data`
- **Impact on AI Agents**: All 6 tables in `auto_aftersales_data` originally had `0` column descriptions in BigQuery `INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`, forcing agents to guess column semantics from column names alone.

## Trap 5: Cross-Cloud Promo Code Typo & Identity Match Confidence (`auto_sales_data`)
- **Affected Tables**: `customer_identity_crosswalk`, `crm_campaign_history`
- **Mandatory Guardrail**: Filter `match_confidence >= 0.85` for verified customer attribution, and always include both `'PLATINUM-VIP'` and legacy typo `'PLATNUM-VIP'` when filtering Platinum VIP campaign conversions.
""",
  )

  write_text(
      "raw-tribal-knowledge/04_join_rules_and_grain.md",
      """# Cross-Dataset Join Rules, Primary Keys & Cardinality Grain

## Table Grains
1. `auto_aftersales_data.vehicle_ownership`: **1 row per `vin`** (5,000 rows).
2. `auto_sales_data.vehicle_sales`: **1 row per `sale_id` / `vin`** (5,000 rows, 1:1 with `vehicle_ownership.vin`).
3. `auto_aftersales_data.service_orders`: **1 row per `service_order_id`** (6,104 rows; `N:1` to `vin`, `N:1` to `dealership_id`, `N:1` to `technician_id`).
4. `auto_aftersales_data.warranty_claims`: **1 row per `claim_id`** (1,894 rows; **1:1** with `service_orders.service_order_id` where `is_warranty_covered = TRUE`).
5. `auto_aftersales_data.service_parts_usage`: **1 row per `usage_id`** (10,861 rows; **N:1** to `service_order_id`—averaging 1.78 part rows per service order).

## Critical Join Fan-Out Warning (`warranty_claims` <-> `service_parts_usage`)
- Joining `warranty_claims` (`1,894` rows) directly to `service_parts_usage` (`10,861` rows) on `service_order_id` produces **3,372 joined rows**.
- **NEVER** compute `SUM(w.claim_amount)` after joining `warranty_claims` to `service_parts_usage` without first pre-aggregating `service_parts_usage` to the `service_order_id` grain (e.g., `GROUP BY service_order_id` with `LOGICAL_AND(defective_part_returned)` and `SUM(total_part_cost)`), OR using `SUM(DISTINCT ...)`. Unaggregated joins inflate `claim_amount` by ~1.78x!
""",
  )

  write_text(
      "raw-tribal-knowledge/05_verified_golden_sql_templates.md",
      """# Verified Golden SQL Templates (`sa-demo-agentic`)

## Query 1: Net OEM Warranty Burden & Unrecovered Supplier Chargeback Leakage by Failure Component
```sql
WITH parts_by_order AS (
  SELECT
    service_order_id,
    COUNT(*) AS part_line_items,
    SUM(total_part_cost) AS total_replaced_parts_cost,
    LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned
  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage`
  GROUP BY service_order_id
)
SELECT
  w.failure_component,
  COUNT(w.claim_id) AS total_claims_submitted,
  COUNTIF(w.claim_status = 'Approved') AS approved_claims,
  ROUND(SUM(w.claim_amount), 2) AS gross_submitted_claim_amount,
  ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage,
  ROUND(
    SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) -
    SUM(CASE
      WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
      THEN w.claim_amount * 0.70 ELSE 0 END),
    2
  ) AS net_oem_warranty_burden
FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
LEFT JOIN parts_by_order p
  ON w.service_order_id = p.service_order_id
GROUP BY w.failure_component
ORDER BY net_oem_warranty_burden DESC;
```

## Query 2: Active Fleet Warranty Entitlement & Claim Frequency by Vehicle Model
```sql
WITH entitled_fleet AS (
  SELECT
    vo.vin,
    vo.model_id,
    vo.ownership_status,
    vo.extended_warranty_purchased,
    CASE
      WHEN vo.warranty_end_date >= CURRENT_DATE()
       AND (vo.ownership_status = 'Active'
            OR (vo.ownership_status = 'Transferred' AND vo.extended_warranty_purchased = TRUE))
      THEN TRUE
      ELSE FALSE
    END AS is_warranty_entitled
  FROM `sa-demo-agentic.auto_aftersales_data.vehicle_ownership` vo
),
approved_claims_by_vin AS (
  SELECT
    vin,
    COUNT(claim_id) AS approved_claim_count,
    SUM(claim_amount) AS approved_claim_spend
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  WHERE claim_status = 'Approved'
  GROUP BY vin
)
SELECT
  vm.model_id,
  vm.model_name,
  vm.category,
  COUNT(ef.vin) AS total_sold_fleet,
  COUNTIF(ef.is_warranty_entitled) AS active_entitled_fleet,
  SUM(COALESCE(ac.approved_claim_count, 0)) AS total_approved_claims,
  ROUND(SUM(COALESCE(ac.approved_claim_spend, 0)), 2) AS realized_warranty_spend,
  ROUND(SAFE_DIVIDE(SUM(COALESCE(ac.approved_claim_spend, 0)), COUNTIF(ef.is_warranty_entitled)), 2) AS realized_warranty_cost_per_entitled_vehicle
FROM `sa-demo-agentic.auto_sales_data.vehicle_models` vm
INNER JOIN entitled_fleet ef
  ON vm.model_id = ef.model_id
LEFT JOIN approved_claims_by_vin ac
  ON ef.vin = ac.vin
GROUP BY vm.model_id, vm.model_name, vm.category
ORDER BY realized_warranty_spend DESC;
```

## Query 3: Final Assembly Plant vs Component Source Plant Quality Scorecard
```sql
WITH active_plants AS (
  SELECT DISTINCT p.plant_id, p.plant_name, p.location, p.capacity
  FROM `sa-demo-agentic.auto_manufacturing_data.plants` p
  INNER JOIN `sa-demo-agentic.auto_manufacturing_data.assembly_line_status` als
    ON p.plant_name = als.plant_name
),
assembly_claims AS (
  SELECT
    build_plant_name AS plant_name,
    COUNTIF(claim_status = 'Approved' AND supplier_fault = FALSE) AS approved_assembly_fault_claims,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = FALSE THEN claim_amount ELSE 0 END), 2) AS assembly_fault_warranty_cost
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  GROUP BY build_plant_name
),
component_claims AS (
  SELECT
    part_source_plant_name AS plant_name,
    COUNTIF(claim_status = 'Approved' AND supplier_fault = TRUE) AS approved_component_fault_claims,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = TRUE THEN claim_amount ELSE 0 END), 2) AS component_fault_warranty_cost
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  GROUP BY part_source_plant_name
)
SELECT
  ap.plant_id,
  ap.plant_name,
  ap.location,
  ap.capacity,
  COALESCE(ac.approved_assembly_fault_claims, 0) AS approved_assembly_fault_claims,
  COALESCE(ac.assembly_fault_warranty_cost, 0.0) AS assembly_fault_warranty_cost,
  COALESCE(cc.approved_component_fault_claims, 0) AS approved_component_fault_claims,
  COALESCE(cc.component_fault_warranty_cost, 0.0) AS component_fault_warranty_cost
FROM active_plants ap
LEFT JOIN assembly_claims ac USING (plant_name)
LEFT JOIN component_claims cc USING (plant_name)
ORDER BY assembly_fault_warranty_cost DESC;
```
""",
  )

  write_text(
      "raw-tribal-knowledge/06_analyst_feedback_learnings.md",
      """# Analyst Curation Loop Learnings (Conversational Analytics Feedback)

## Learning 1 (`warranty-spend-overstatement-fix`)
- **Observed Agent Failure**: When asked for *"Total warranty spend by failure component"*, the ungrounded agent executed `SELECT failure_component, SUM(claim_amount) FROM warranty_claims GROUP BY 1`, reporting **`$1,798,306.90`**.
- **Root Cause**: The agent summed unadjudicated (`Pending`, `Under Review`) and rejected (`Denied`) claims alongside `Approved` claims.
- **Verified Correction**: Always filter `claim_status = 'Approved'` for realized spend (`$1,254,786.01`), or report `Approved` vs `Open Exposure` (`Pending` + `Under Review` = `$404,016.42`) in separate columns.

## Learning 2 (`dealership-warranty-absorption-trap`)
- **Observed Agent Failure**: When asked *"How much service cost did the OEM absorb under warranty across dealerships?"*, the ungrounded agent filtered `WHERE service_type = 'Warranty Repair'`, returning **`$826,977.80`** instead of **`$1,591,386.85`**.
- **Root Cause**: `service_orders` has 690 `'Repair'` rows and 282 `'Recall Service'` rows where `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Verified Correction**: Filter `service_orders` using `WHERE is_warranty_covered = TRUE` and compute `SUM(total_cost - customer_paid_amount)`.

## Learning 3 (`parts-usage-fanout-on-claims`)
- **Observed Agent Failure**: Joining `warranty_claims` directly to `service_parts_usage` on `service_order_id` and running `SUM(w.claim_amount)` inflated warranty claim dollars from `$1,254,786.01` to **`$2,226,419.83`** (1.77x fan-out).
- **Root Cause**: `service_parts_usage` has multiple part rows per `service_order_id` (`10,861` rows across `6,104` service orders).
- **Verified Correction**: Pre-aggregate `service_parts_usage` by `service_order_id` in a CTE before joining to `warranty_claims`.
""",
  )


def get_catalog_nodes():
  """Returns the structured PROGRESSIVE disclosure nodes and links for both OKF bundle and Dataplex publishing."""
  entry_group_res = f"projects/{PROJECT_ID}/locations/{LOCATION}/entryGroups/{ENTRY_GROUP_ID}"
  glossary_res = f"projects/{PROJECT_NUMBER}/locations/global/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/global/glossaries/auto-enterprise-okf-glossary"

  nodes = [
      {
          "id": "agents",
          "entry_id": "agents",
          "parent_id": None,
          "doc_type": "knowledge-base",
          "title": "Automotive Enterprise Knowledge Base (OKF v0.2)",
          "catalog_path": "catalog/agents.md",
          "bundle_path": "bundle/agents.md",
          "overview": """# Automotive Enterprise Knowledge Base (OKF v0.2)

## Purpose
Progressive-disclosure root routing document for the `sa-demo-agentic` Automotive Enterprise Lakehouse covering After-Sales Warranty (`auto_aftersales_data`), Vehicle Sales (`auto_sales_data`), and Plant Manufacturing (`auto_manufacturing_data`).

## Navigation Spine
1. **BigQuery Asset Context Overlays (`assets/bigquery/sa-demo-agentic/*`)**:
   - `auto_aftersales_data`: `warranty_claims`, `service_orders`, `service_parts_usage`, `vehicle_ownership`, `technicians`, `recall_campaigns`.
   - `auto_sales_data`: `vehicle_sales`, `vehicle_models`, `dealerships`, `customer_identity_crosswalk`.
   - `auto_manufacturing_data`: `plants`, `assembly_line_status`, `parts_inventory`, `quality_inspections`.
2. **Domain Ontology & Tribal Knowledge (`documents/*`)**:
   - `documents/ontology/automotive-lifecycle-ontology`: End-to-end VIN lifecycle, warranty entitlement state machine, and supplier chargeback recovery rules.
   - `documents/concepts/net-oem-warranty-burden`: Canonical formula for Realized Warranty Cost, 70% Supplier Chargeback Recovery, and Unrecovered Supplier Leakage.
   - `documents/concepts/active-warranty-entitlement-fleet`: Secondary-market transfer rules (`4,650` entitled vehicles out of `5,000`).
   - `documents/concepts/dimension-catalog-padding-guardrail`: Mandatory filter for the 259-row padded dimension tables (`plants`, `vehicle_models`, `dealerships`).
   - `documents/playbooks/cross-domain-root-cause-playbook`: Diagnostic SQL playbook linking manufacturing plant telemetry to dealership warranty claims.
   - `documents/learnings/warranty-fanout-and-absorption-learnings`: Validated analyst corrections preventing `service_parts_usage` join fan-out and `service_type` undercounting.
""",
          "queries": [],
      },
      {
          "id": "assets",
          "entry_id": "assets",
          "parent_id": "agents",
          "doc_type": "knowledge-base-index",
          "title": "Data Assets Index",
          "catalog_path": "catalog/assets/index.md",
          "bundle_path": "bundle/assets/index.md",
          "overview": """# Data Assets Index

## Purpose
Index of physical data platform systems enriched by this Context Set.

## Child Systems
- `assets/bigquery`: Google Cloud BigQuery datasets in `sa-demo-agentic` (`us-central1`).
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery",
          "entry_id": "assets/bigquery",
          "parent_id": "assets",
          "doc_type": "knowledge-base-index",
          "title": "BigQuery System Index",
          "catalog_path": "catalog/assets/bigquery/index.md",
          "bundle_path": "bundle/assets/bigquery/index.md",
          "overview": """# BigQuery System Index

## Purpose
Index of GCP projects containing curated BigQuery analytical datasets.

## Projects
- `assets/bigquery/sa-demo-agentic`: Automotive Enterprise Lakehouse (`auto_aftersales_data`, `auto_sales_data`, `auto_manufacturing_data`).
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic",
          "entry_id": "assets/bigquery/sa-demo-agentic",
          "parent_id": "assets/bigquery",
          "doc_type": "knowledge-base-index",
          "title": "Project sa-demo-agentic Dataset Index",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/index.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/index.md",
          "overview": """# Project `sa-demo-agentic` Dataset Index

## Purpose
Contains the three core `us-central1` domains of the Automotive Enterprise Lakehouse.

## Datasets
- `assets/bigquery/sa-demo-agentic/auto_aftersales_data`: Dealership service orders, warranty claims, parts replacements, recalls, and VIN ownership entitlement.
- `assets/bigquery/sa-demo-agentic/auto_sales_data`: Vehicle sales, model catalog, dealership network, and cross-cloud identity crosswalk.
- `assets/bigquery/sa-demo-agentic/auto_manufacturing_data`: Assembly & component plants, line OEE telemetry, parts inventory, and quality inspections.
""",
          "queries": [],
      },
      # Dataset Indexes
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "parent_id": "assets/bigquery/sa-demo-agentic",
          "doc_type": "knowledge-base-index",
          "title": "Dataset auto_aftersales_data",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/index.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/index.md",
          "overview": """# Dataset `sa-demo-agentic.auto_aftersales_data`

## Purpose
Core After-Sales, Dealership Service, and Warranty Adjudication dataset in `us-central1`. Previously lacked native BigQuery column descriptions; enriched via OKF v0.2 with verified financial formulas, supplier recovery rules, and join fan-out guardrails.

## Curated Table Overlays
- `warranty_claims` (1,894 rows): Warranty claim adjudication, plant attribution (`build_plant_name` vs `part_source_plant_name`), and supplier fault flags.
- `service_orders` (6,104 rows): Dealership service visits; use `is_warranty_covered = TRUE` (`$1,591,386.85`) rather than `service_type = 'Warranty Repair'` (`$826,977.80`).
- `service_parts_usage` (10,861 rows): Replaced parts per service order and `defective_part_returned` core-return tracking.
- `vehicle_ownership` (5,000 rows): VIN-level warranty dates, mileage, `ownership_status`, and `extended_warranty_purchased`.
- `technicians` (120 rows): Certified dealership technicians (`Master`, `Senior`, `Apprentice`, `Specialist`).
- `recall_campaigns` (40 rows): Safety recall campaigns by `affected_model_id` and `target_component`.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "parent_id": "assets/bigquery/sa-demo-agentic",
          "doc_type": "knowledge-base-index",
          "title": "Dataset auto_sales_data",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_sales_data/index.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_sales_data/index.md",
          "overview": """# Dataset `sa-demo-agentic.auto_sales_data`

## Purpose
Retail vehicle sales, active vehicle model catalog, dealership directory, and customer identity crosswalk in `us-central1`.

## Curated Table Overlays
- `vehicle_sales` (5,000 rows): VIN-level retail sales transactions linking `model_id`, `dealership_id`, and `sale_price`.
- `vehicle_models` (259 rows; **8 active models** `model_id` 1..8): Model catalog linking each vehicle platform to its primary `plant_id`.
- `dealerships` (259 rows; **8 active dealerships** `dealership_id` 1..8): Authorized retail and service dealership network.
- `customer_identity_crosswalk` (5,000 rows): Bridges `auto_customer_id` (`vin`) to `global_loyalty_id` (`match_confidence >= 0.85`).
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "parent_id": "assets/bigquery/sa-demo-agentic",
          "doc_type": "knowledge-base-index",
          "title": "Dataset auto_manufacturing_data",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/index.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/index.md",
          "overview": """# Dataset `sa-demo-agentic.auto_manufacturing_data`

## Purpose
Manufacturing facility master data, assembly line OEE telemetry, component parts inventory, and end-of-line quality inspections in `us-central1`.

## Curated Table Overlays
- `plants` (259 rows; **7 active plants** `plant_id` 1..7): Manufacturing plant directory (`plant_name`, `location`, `annual_capacity`).
- `assembly_line_status` (35 rows): Line-level `operational_efficiency` (OEE), `status`, and `daily_output` for the 7 active plants.
- `parts_inventory` (50 rows): Component inventory and `source_plant_id` mapping.
- `quality_inspections` (500 rows): End-of-line plant inspection `defect_severity` and `corrective_action` logs.
""",
          "queries": [],
      },
      # Table Overlays - auto_aftersales_data
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "warranty_claims",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.warranty_claims`

## Purpose
Records financial warranty claims (`1,894` rows, 1 row per `claim_id` / `service_order_id`) submitted by dealerships for warranty-covered repairs. Central fact table for calculating **Realized Warranty Cost** (`$1,254,786.01`), **Open Warranty Reserve Exposure** (`$404,016.42`), and **Net OEM Warranty Burden** after Supplier Chargeback Recovery.

## Columns & Metrics
- `claim_id` (`INTEGER`, PK): Unique warranty claim identifier (`1..1894`).
- `service_order_id` (`INTEGER`, FK -> `service_orders.service_order_id`): 1:1 link to the originating warranty-covered dealership service visit.
- `vin` (`STRING`, FK -> `vehicle_ownership.vin`, `vehicle_sales.vin`): 17-character Vehicle Identification Number.
- `claim_date` (`DATE`): Date the warranty claim was filed (`30` days after `service_orders.service_date`).
- `failure_component` (`STRING`): Failed vehicle subsystem (`Engine`, `Battery`, `Electrical`, `Brakes`, `Transmission`, `Suspension`, `HVAC`, `Infotainment`, `Steering`, `Exhaust`, `Fuel System`).
- `claim_amount` (`FLOAT`): Total dollar value requested on the claim. **CRITICAL CAVEAT**: Raw `SUM(claim_amount)` (`$1,798,306.90`) includes unadjudicated and rejected claims. Always filter `claim_status = 'Approved'` (`$1,254,786.01`) for realized cost.
- `claim_status` (`STRING`): Adjudication state:
  - `'Approved'` (`1,331` rows, `$1,254,786.01`): Realized financial warranty expense.
  - `'Pending'` (`233` rows, `$217,261.21`) & `'Under Review'` (`186` rows, `$186,755.21`): Open warranty reserve exposure (`$404,016.42` combined).
  - `'Denied'` (`144` rows, `$139,504.47`): Rejected claims; `$0` OEM financial liability.
- `build_plant_name` (`STRING`, FK -> `plants.plant_name`): Final assembly plant where the vehicle (`vin`) was assembled. Use for **Assembly Plant Quality** metrics (`WHERE supplier_fault = FALSE`).
- `part_source_plant_name` (`STRING`, FK -> `plants.plant_name`): Component manufacturing plant that produced the defective replacement part. Use for **Component Plant Defect** tracing.
- `supplier_fault` (`BOOLEAN`): `TRUE` (`501` approved claims, `$464,191.35`) when the failure was caused by an external tier-1 supplier defect; `FALSE` (`830` approved claims, `$790,594.66`) when caused by internal OEM assembly/design.
- **Metric — Recoverable Supplier Chargeback (`recoverable_supplier_chargeback`)**: When `claim_status = 'Approved' AND supplier_fault = TRUE`, the OEM recovers `0.70 * claim_amount` **ONLY IF** all replaced parts on `service_order_id` have `defective_part_returned = TRUE` in `service_parts_usage` (pre-aggregated by `service_order_id`).
""",
          "queries": [
              {
                  "title": "Net OEM Warranty Burden & Supplier Recovery by Component",
                  "description": "Calculates Gross Submitted, Realized Approved Cost, 70% Recoverable Supplier Chargeback (requiring core return), Unrecovered Leakage, and Net OEM Burden.",
                  "sql": """WITH parts_by_order AS (
  SELECT
    service_order_id,
    LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned
  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage`
  GROUP BY service_order_id
)
SELECT
  w.failure_component,
  COUNTIF(w.claim_status = 'Approved') AS approved_claims,
  ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage,
  ROUND(
    SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) -
    SUM(CASE
      WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
      THEN w.claim_amount * 0.70 ELSE 0 END),
    2
  ) AS net_oem_warranty_burden
FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
LEFT JOIN parts_by_order p USING (service_order_id)
GROUP BY w.failure_component
ORDER BY net_oem_warranty_burden DESC;""",
              }
          ],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "service_orders",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.service_orders`

## Purpose
Captures every dealership service bay visit (`6,104` rows, 1 row per `service_order_id`) across retail maintenance, repairs, warranty repairs, and safety recalls.

## Columns & Metrics
- `service_order_id` (`INTEGER`, PK): Unique service order identifier (`1..6104`).
- `vin` (`STRING`, FK -> `vehicle_ownership.vin`): Serviced vehicle VIN.
- `dealership_id` (`INTEGER`, FK -> `auto_sales_data.dealerships.dealership_id`): Servicing dealership ID (`1..8` active dealerships).
- `technician_id` (`INTEGER`, FK -> `technicians.technician_id`): Assigned lead service technician (`1..120`).
- `service_date` (`DATE`): Date the repair order was completed.
- `service_type` (`STRING`): Operational bay category (`'Routine Maintenance'`, `'Repair'`, `'Warranty Repair'`, `'Recall Service'`). **CRITICAL CAVEAT**: Do NOT filter `service_type = 'Warranty Repair'` (`$826,977.80`) to compute total warranty-covered service cost! `690` `'Repair'` orders (`$558,639.28`) and `282` `'Recall Service'` orders (`$205,769.77`) are ALSO covered under warranty (`is_warranty_covered = TRUE`, `customer_paid_amount = 0`).
- `labor_hours` (`FLOAT`): Billable technician labor hours.
- `labor_cost` (`FLOAT`): Dealership labor charge.
- `parts_cost` (`FLOAT`): Rollup of replaced parts cost for this order.
- `total_cost` (`FLOAT`): `labor_cost + parts_cost` (`$4,468,695.07` across all 6,104 orders).
- `customer_paid_amount` (`FLOAT`): Out-of-pocket amount paid by the vehicle owner (`$0.00` whenever `is_warranty_covered = TRUE`).
- `is_warranty_covered` (`BOOLEAN`): Canonical flag (`1,894` orders = `TRUE`) indicating OEM warranty absorption (`$1,591,386.85` total absorbed cost).
""",
          "queries": [
              {
                  "title": "OEM Warranty-Covered Service Absorption by Service Type",
                  "description": "Demonstrates why filtering is_warranty_covered = TRUE ($1,591,386.85) is mandatory vs filtering service_type = 'Warranty Repair' ($826,977.80).",
                  "sql": """SELECT
  service_type,
  is_warranty_covered,
  COUNT(*) AS order_count,
  ROUND(SUM(total_cost), 2) AS gross_service_cost,
  ROUND(SUM(customer_paid_amount), 2) AS customer_paid_total,
  ROUND(SUM(total_cost - customer_paid_amount), 2) AS oem_absorbed_warranty_cost
FROM `sa-demo-agentic.auto_aftersales_data.service_orders`
GROUP BY service_type, is_warranty_covered
ORDER BY oem_absorbed_warranty_cost DESC;""",
              }
          ],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "service_parts_usage",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.service_parts_usage`

## Purpose
Line-item component replacement log (`10,861` rows, 1 row per `usage_id`, `N:1` to `service_order_id`). Tracks part numbers, quantities, costs, and whether defective cores were returned by the dealership for supplier chargeback recovery.

## Columns & Metrics
- `usage_id` (`INTEGER`, PK): Unique part replacement line item ID.
- `service_order_id` (`INTEGER`, FK -> `service_orders.service_order_id`): Parent service visit. **JOIN FAN-OUT WARNING**: Multiple rows exist per `service_order_id` (`1.78` average). Always aggregate by `service_order_id` before joining to `service_orders` or `warranty_claims`.
- `part_number` (`STRING`): OEM catalog part number (`PART-100..PART-149`, links to `auto_manufacturing_data.parts_inventory.part_number`).
- `part_name` (`STRING`): Component description.
- `part_category` (`STRING`): Subsystem category (`Engine`, `Brakes`, `Electrical`, `Suspension`, `Transmission`, `HVAC`, `Battery`, `Body`, `Exhaust`).
- `quantity_used` (`INTEGER`): Units installed during the repair.
- `unit_cost` (`FLOAT`): Wholesale cost per unit.
- `total_part_cost` (`FLOAT`): `quantity_used * unit_cost`.
- `defective_part_returned` (`BOOLEAN`): `TRUE` if the dealership returned the failed component core to the OEM teardown center. Required (`LOGICAL_AND(defective_part_returned) = TRUE` across the `service_order_id`) to claim the 70% supplier chargeback on `supplier_fault = TRUE` warranty claims.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "vehicle_ownership",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.vehicle_ownership`

## Purpose
Master VIN-level ownership, odometer, and warranty entitlement registry (`5,000` rows, 1 row per `vin`). Governs the **Active Warranty Entitlement Fleet** (`4,650` entitled vehicles).

## Columns & Metrics
- `vin` (`STRING`, PK): Unique 17-character Vehicle Identification Number (`1:1` with `auto_sales_data.vehicle_sales.vin`).
- `customer_id` (`STRING`): Current owner identifier.
- `model_id` (`INTEGER`, FK -> `auto_sales_data.vehicle_models.model_id`): Vehicle platform ID (`1..8`).
- `sale_date` (`DATE`): Original retail delivery date.
- `warranty_start_date` (`DATE`): Factory warranty commencement date.
- `warranty_end_date` (`DATE`): Expiration date (`3 years` standard or `5 years` when `extended_warranty_purchased = TRUE`).
- `extended_warranty_purchased` (`BOOLEAN`): Indicates transferable 5-year extended protection plan (`1,069` vehicles = `TRUE`).
- `current_mileage` (`INTEGER`): Latest connected-vehicle/service odometer reading.
- `ownership_status` (`STRING`): Lifecycle ownership state:
  - `'Active'` (`4,582` rows): Original owner; full warranty entitlement.
  - `'Transferred'` (`304` rows): Secondary-market resale; **ONLY entitled to warranty if `extended_warranty_purchased = TRUE` (`68` vehicles)**; the remaining `236` transferred vehicles with standard warranty have no OEM coverage.
  - `'Buyback'` (`114` rows): Manufacturer buyback/lemon-law fleet; excluded from active customer warranty entitlement.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "technicians",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/technicians.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.technicians`

## Purpose
Directory of dealership service technicians (`120` rows, 1 row per `technician_id`) used to analyze repair efficiency, labor hours, and core-return compliance by certification tier.

## Columns & Metrics
- `technician_id` (`INTEGER`, PK): Unique technician ID (`1..120`).
- `technician_name` (`STRING`): Full name of the technician (`Tech_1..Tech_120`).
- `dealership_id` (`INTEGER`, FK -> `auto_sales_data.dealerships.dealership_id`): Assigned dealership (`1..8`).
- `certification_level` (`STRING`): Qualification tier (`'Master'`, `'Specialist'`, `'Senior'`, `'Apprentice'`).
- `specialty` (`STRING`): Primary subsystem specialization (`Engine`, `Electrical`, `Transmission`, `EV Battery`, `General`, `Brakes`, `HVAC`).
- `hire_date` (`DATE`): Dealership onboarding date.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_aftersales_data",
          "doc_type": "context-overlay",
          "title": "recall_campaigns",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_aftersales_data/recall_campaigns.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_aftersales_data.recall_campaigns`

## Purpose
Registry of NHTSA / OEM safety and compliance recall campaigns (`40` rows, 1 row per `recall_id`).

## Columns & Metrics
- `recall_id` (`INTEGER`, PK): Unique campaign identifier (`1..40`).
- `campaign_code` (`STRING`): Official recall bulletin code (`RC-2023-001..RC-2023-040`).
- `issue_date` (`DATE`): Campaign release date.
- `affected_model_id` (`INTEGER`, FK -> `auto_sales_data.vehicle_models.model_id`): Target vehicle model (`1..8`).
- `target_component` (`STRING`): Subsystem subject to recall (`Brakes`, `Electrical`, `Battery`, `Engine`, `Steering`, `Fuel System`, `Suspension`, `Transmission`).
- `severity` (`STRING`): Risk classification (`'Critical'`, `'High'`, `'Medium'`, `'Low'`).
- `estimated_cost_per_vehicle` (`FLOAT`): Budgeted per-VIN remediation cost.
""",
          "queries": [],
      },
      # Table Overlays - auto_sales_data
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "doc_type": "context-overlay",
          "title": "vehicle_sales",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_sales_data.vehicle_sales`

## Purpose
Retail vehicle sales fact table (`5,000` rows, 1 row per `sale_id` / `vin`). Connects sold vehicles (`vin`) to `vehicle_models` (`model_id`) and selling `dealerships` (`dealership_id`).

## Columns & Metrics
- `sale_id` (`INTEGER`, PK): Unique retail transaction ID (`1..5000`).
- `vin` (`STRING`, UK, FK -> `auto_aftersales_data.vehicle_ownership.vin`): 17-character VIN (`1:1` grain with `vehicle_ownership`).
- `model_id` (`INTEGER`, FK -> `vehicle_models.model_id`): Sold model ID (`1..8`).
- `dealership_id` (`INTEGER`, FK -> `dealerships.dealership_id`): Selling dealership ID (`1..8`).
- `sale_date` (`DATE`): Retail delivery date.
- `sale_price` (`FLOAT`): Final transaction price paid (`USD`).
- `customer_id` (`STRING`): Purchasing customer identifier.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "doc_type": "context-overlay",
          "title": "vehicle_models",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_sales_data.vehicle_models`

## Purpose
Master vehicle platform catalog (`259` total rows; **ONLY 8 active production models** `model_id BETWEEN 1 AND 8`). Maps each vehicle model to its primary assembly `plant_id` in `auto_manufacturing_data.plants`.

## Columns & Metrics
- `model_id` (`INTEGER`, PK): Unique model identifier. **CATALOG PADDING TRAP**: Rows `9..259` are unallocated catalog placeholders with zero sales or service orders. Always filter `model_id BETWEEN 1 AND 8` or `INNER JOIN` to `vehicle_sales` / `vehicle_ownership`.
- `model_name` (`STRING`): Commercial model name (`Model S1`, `Model T1`, `Model X1`, `Model E1`, `Model SUV2`, `Model C1`, `Model V1`, `Model R1`).
- `category` (`STRING`): Body style (`Sedan`, `Truck`, `SUV`, `EV`).
- `msrp` (`FLOAT`): Manufacturer Suggested Retail Price (`USD`).
- `plant_id` (`INTEGER`, FK -> `auto_manufacturing_data.plants.plant_id`): Primary final assembly plant ID (`1..7`).
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "doc_type": "context-overlay",
          "title": "dealerships",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_sales_data.dealerships`

## Purpose
Master dealership directory (`259` total rows; **ONLY 8 active operational dealerships** `dealership_id BETWEEN 1 AND 8`).

## Columns & Metrics
- `dealership_id` (`INTEGER`, PK): Unique dealership identifier. **CATALOG PADDING TRAP**: Rows `9..259` are inactive franchise placeholders with zero sales, service orders, or technicians. Always `INNER JOIN` to `vehicle_sales` or `service_orders`, or filter `dealership_id BETWEEN 1 AND 8`.
- `dealership_name` (`STRING`): Authorized dealer name (`AutoNation North`, `Metro Motors`, `Pacific Crest Auto`, `Lone Star Ford`, `Midwest Premier`, `Empire State Auto`, `Sunbelt Dealership`, `Mountain View Motors`).
- `region` (`STRING`): Sales territory (`North`, `South`, `East`, `West`, `Midwest`).
- `state` (`STRING`): US state code.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_sales_data",
          "doc_type": "context-overlay",
          "title": "customer_identity_crosswalk",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_sales_data/customer_identity_crosswalk.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_sales_data.customer_identity_crosswalk`

## Purpose
Identity resolution bridge (`5,000` rows) mapping `auto_customer_id` (which stores the vehicle `vin` / `CUST-*` key) to `global_loyalty_id` for cross-cloud CRM attribution.

## Columns & Metrics
- `auto_customer_id` (`STRING`, PK): Local automotive customer/vehicle key.
- `global_loyalty_id` (`STRING`): Enterprise cross-cloud loyalty identifier (`LOYALTY-*`).
- `email_sha256` (`STRING`): Hashed customer email for clean-room matching.
- `identity_provider` (`STRING`): Resolution source (`LiveRamp`, `UID2`, `Internal_Deterministic`).
- `match_confidence` (`FLOAT`): Probabilistic match score (`0.0..1.0`). **MANDATORY GUARDRAIL**: Filter `WHERE match_confidence >= 0.85` for executive LTV and campaign attribution.
- `last_verified_timestamp` (`TIMESTAMP`): Last identity graph verification timestamp.
""",
          "queries": [],
      },
      # Table Overlays - auto_manufacturing_data
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "doc_type": "context-overlay",
          "title": "plants",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.plants`

## Purpose
Master manufacturing facility table (`259` total rows; **ONLY 7 active manufacturing plants** `plant_id BETWEEN 1 AND 7`).

## Columns & Metrics
- `plant_id` (`INTEGER`, PK): Unique facility identifier. **CATALOG PADDING TRAP**: Rows `8..259` are unallocated global facility codes with zero assembly lines or production. Always filter `plant_id BETWEEN 1 AND 7` or `INNER JOIN` to `assembly_line_status` before computing capacity or efficiency averages!
- `plant_name` (`STRING`, UK): Facility name (`Detroit Assembly`, `Ohio Stamping`, `Kentucky Truck`, `Chicago Assembly`, `Dearborn Engine`, `Kansas City Assembly`, `Buffalo Stamping`). Joins to `warranty_claims.build_plant_name` (as final assembly plant) and `warranty_claims.part_source_plant_name` (as component supplier plant).
- `location` (`STRING`): City and state (`MI`, `OH`, `KY`, `IL`, `MO`, `NY`).
- `annual_capacity` (`INTEGER`): Nameplate annual production capacity.
- `manager_name` (`STRING`): Plant director name.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "doc_type": "context-overlay",
          "title": "assembly_line_status",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/assembly_line_status.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.assembly_line_status`

## Purpose
Operational telemetry for active manufacturing lines (`35` rows, 5 lines per active plant `plant_id` 1..7).

## Columns & Metrics
- `line_id` (`INTEGER`, PK): Unique assembly line identifier (`1..35`).
- `plant_id` (`INTEGER`, FK -> `plants.plant_id`): Parent manufacturing plant (`1..7`).
- `line_name` (`STRING`): Line designation (`Body Shop`, `Paint Shop`, `Final Assembly`, `Powertrain`, `Trim & Chassis`).
- `status` (`STRING`): Operational status (`Running`, `Maintenance`, `Downtime`).
- `operational_efficiency` (`FLOAT`): Overall Equipment Effectiveness (OEE) ratio (`0.0..1.0`).
- `daily_output` (`INTEGER`): Units produced per day.
- `last_maintenance_date` (`DATE`): Date of last scheduled preventative maintenance.
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "doc_type": "context-overlay",
          "title": "parts_inventory",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/parts_inventory.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.parts_inventory`

## Purpose
Manufacturing component catalog and plant inventory (`50` rows) linking `part_number` to its manufacturing `source_plant_id`.

## Columns & Metrics
- `part_id` (`INTEGER`, PK): Numeric part ID (`1..50`).
- `part_number` (`STRING`, UK): Canonical part code (`PART-100..PART-149`, joins to `auto_aftersales_data.service_parts_usage.part_number`).
- `part_name` (`STRING`): Component description.
- `category` (`STRING`): Subsystem category.
- `source_plant_id` (`INTEGER`, FK -> `plants.plant_id`): Plant that manufactures this component (`1..7`).
- `quantity_on_hand` (`INTEGER`): Current warehouse stock level.
- `reorder_threshold` (`INTEGER`): Minimum safety stock threshold.
- `unit_cost` (`FLOAT`): Manufacturing unit cost (`USD`).
""",
          "queries": [],
      },
      {
          "id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections",
          "entry_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections",
          "parent_id": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data",
          "doc_type": "context-overlay",
          "title": "quality_inspections",
          "catalog_path": "catalog/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections.md",
          "bundle_path": "bundle/assets/bigquery/sa-demo-agentic/auto_manufacturing_data/quality_inspections.md",
          "overview": """# Context Overlay: `sa-demo-agentic.auto_manufacturing_data.quality_inspections`

## Purpose
End-of-line plant quality audit log (`500` rows) recording in-plant defect detections prior to vehicle shipment.

## Columns & Metrics
- `inspection_id` (`INTEGER`, PK): Unique inspection record ID (`1..500`).
- `plant_id` (`INTEGER`, FK -> `plants.plant_id`): Inspected manufacturing plant (`1..7`).
- `line_id` (`INTEGER`, FK -> `assembly_line_status.line_id`): Inspected assembly line (`1..35`).
- `inspection_date` (`DATE`): Date of audit.
- `inspector_name` (`STRING`): Quality engineer identifier.
- `passed` (`BOOLEAN`): `TRUE` if unit passed without rework; `FALSE` if defect was logged.
- `defect_type` (`STRING`): Logged failure mode (`Weld Porosity`, `Paint Blemish`, `Torque Spec Deviation`, `Electrical Short`, `Panel Gap`, `Fluid Leak`).
- `defect_severity` (`STRING`): Severity tier (`Critical`, `Major`, `Minor`, `Cosmetic`).
- `corrective_action` (`STRING`): Plant disposition (`Line Stop & Recalibrate`, `Rework Bay`, `Scrap Part`, `Supplier Containment`).
""",
          "queries": [],
      },
      # Documents Spine
      {
          "id": "documents",
          "entry_id": "documents",
          "parent_id": "agents",
          "doc_type": "knowledge-base-index",
          "title": "Domain Knowledge & Tribal Documents Index",
          "catalog_path": "catalog/documents/index.md",
          "bundle_path": "bundle/documents/index.md",
          "overview": """# Domain Knowledge & Tribal Documents Index

## Purpose
Organizes enterprise domain ontologies, semantic business concepts, diagnostic SQL playbooks, and analyst curation learnings.

## Sub-Collections
- `documents/ontology`: Domain entity lifecycle & state machine rules.
- `documents/concepts`: Canonical business metrics, supplier chargeback formulas, and dimension padding guardrails.
- `documents/playbooks`: Cross-dataset analytical SQL playbooks.
- `documents/learnings`: Empirical corrections from Conversational Analytics agent benchmarking.
""",
          "queries": [],
      },
      {
          "id": "documents/ontology",
          "entry_id": "documents/ontology",
          "parent_id": "documents",
          "doc_type": "knowledge-base-index",
          "title": "Domain Ontologies Index",
          "catalog_path": "catalog/documents/ontology/index.md",
          "bundle_path": "bundle/documents/ontology/index.md",
          "overview": """# Domain Ontologies Index

## Purpose
Houses formal entity-relationship and state-machine ontologies across Manufacturing, Retail Sales, and After-Sales Warranty.

## Documents
- `documents/ontology/automotive-lifecycle-ontology`: End-to-end VIN lifecycle, dual-plant role (`build_plant_name` vs `part_source_plant_name`), and warranty entitlement state transitions.
""",
          "queries": [],
      },
      {
          "id": "documents/ontology/automotive-lifecycle-ontology",
          "entry_id": "documents/ontology/automotive-lifecycle-ontology",
          "parent_id": "documents/ontology",
          "doc_type": "knowledge-base",
          "title": "Automotive Enterprise Lifecycle Ontology",
          "catalog_path": "catalog/documents/ontology/automotive-lifecycle-ontology.md",
          "bundle_path": "bundle/documents/ontology/automotive-lifecycle-ontology.md",
          "overview": """# Automotive Enterprise Lifecycle Ontology

## Purpose
Defines the authoritative domain ontology connecting **Manufacturing Plants**, **Vehicle Models**, **Sold VINs**, **Dealership Service Orders**, **Replaced Parts**, and **Warranty Claims** in `sa-demo-agentic`.

## Dual Plant Attribution Ontology
Every warranty claim (`warranty_claims`) links to `auto_manufacturing_data.plants` along **two distinct causal axes**:
1. **Final Vehicle Assembly Axis (`build_plant_name = plants.plant_name`)**: Identifies the facility that assembled the complete vehicle (`vin`). Governs internal OEM assembly quality (`WHERE supplier_fault = FALSE`).
2. **Component Manufacturing Axis (`part_source_plant_name = plants.plant_name`)**: Identifies the stamping/powertrain facility or external tier-1 vendor hub that produced the failed component (`part_number`). Governs component containment and supplier recovery (`WHERE supplier_fault = TRUE`).

## Warranty Adjudication & Supplier Recovery Ontology
- **Gross Claim Volume (`$1,798,306.90`)** is divided into:
  - **Realized Warranty Cost (`claim_status = 'Approved'`, `$1,254,786.01`)**
  - **Open Warranty Reserve Exposure (`claim_status IN ('Pending', 'Under Review')`, `$404,016.42`)**
  - **Denied Claims (`claim_status = 'Denied'`, `$139,504.47`, zero OEM liability)**
- **Supplier Chargeback Contract Rule**: For `'Approved'` claims with `supplier_fault = TRUE` (`$464,191.35`), the OEM recovers **70% of `claim_amount`** (`$42,415.72`) when `LOGICAL_AND(defective_part_returned) = TRUE` on `service_parts_usage` for that `service_order_id`. When any replaced part on the order has `defective_part_returned = FALSE`, the 70% recovery (`$282,518.23`) is forfeited as **Unrecovered Supplier Leakage**, resulting in a **Net OEM Warranty Burden of `$1,212,370.29`**.
""",
          "queries": [],
      },
      {
          "id": "documents/concepts",
          "entry_id": "documents/concepts",
          "parent_id": "documents",
          "doc_type": "knowledge-base-index",
          "title": "Business Concepts & Metric Rules Index",
          "catalog_path": "catalog/documents/concepts/index.md",
          "bundle_path": "bundle/documents/concepts/index.md",
          "overview": """# Business Concepts & Metric Rules Index

## Purpose
Defines canonical financial formulas, fleet eligibility rules, and schema guardrails.

## Concepts
- `documents/concepts/net-oem-warranty-burden`: Realized Warranty Cost, 70% Supplier Chargeback Recovery, and Unrecovered Supplier Leakage.
- `documents/concepts/active-warranty-entitlement-fleet`: Secondary-market resale transfer rule (`4,650` entitled vehicles).
- `documents/concepts/dimension-catalog-padding-guardrail`: Mandatory filter for 259-row padded dimension tables (`7` active plants, `8` active models, `8` active dealerships).
""",
          "queries": [],
      },
      {
          "id": "documents/concepts/net-oem-warranty-burden",
          "entry_id": "documents/concepts/net-oem-warranty-burden",
          "parent_id": "documents/concepts",
          "doc_type": "knowledge-base",
          "title": "Net OEM Warranty Burden & Supplier Chargeback Recovery",
          "catalog_path": "catalog/documents/concepts/net-oem-warranty-burden.md",
          "bundle_path": "bundle/documents/concepts/net-oem-warranty-burden.md",
          "overview": """# Net OEM Warranty Burden & Supplier Chargeback Recovery

## Purpose
Establishes the CFO-approved accounting formula for **Realized Warranty Cost**, **Recoverable Supplier Chargeback**, **Unrecovered Supplier Leakage**, and **Net OEM Warranty Burden**.

## Mathematical Specification
1. **Realized Warranty Cost**:
   $$\\text{Realized Warranty Cost} = \\sum_{c \\in \\text{Approved}} \\text{claim\\_amount}_c = \\$1,254,786.01$$
2. **Order-Level Core Return Compliance (`all_defective_parts_returned`)**:
   Pre-aggregate `service_parts_usage` by `service_order_id` using `LOGICAL_AND(defective_part_returned)`.
3. **Recoverable Supplier Chargeback**:
   $$\\text{Recoverable Chargeback} = \\sum_{\\substack{c \\in \\text{Approved} \\\\ \\text{supplier\\_fault}=\\text{TRUE} \\\\ \\text{all\\_returned}=\\text{TRUE}}} 0.70 \\times \\text{claim\\_amount}_c = \\$42,415.72$$
4. **Unrecovered Supplier Leakage**:
   $$\\text{Unrecovered Leakage} = \\sum_{\\substack{c \\in \\text{Approved} \\\\ \\text{supplier\\_fault}=\\text{TRUE} \\\\ \\text{all\\_returned}=\\text{FALSE}}} 0.70 \\times \\text{claim\\_amount}_c = \\$282,518.23$$
5. **Net OEM Warranty Burden**:
   $$\\text{Net OEM Warranty Burden} = \\$1,254,786.01 - \\$42,415.72 = \\$1,212,370.29$$
""",
          "queries": [],
      },
      {
          "id": "documents/concepts/active-warranty-entitlement-fleet",
          "entry_id": "documents/concepts/active-warranty-entitlement-fleet",
          "parent_id": "documents/concepts",
          "doc_type": "knowledge-base",
          "title": "Active Warranty Entitlement Fleet Rule",
          "catalog_path": "catalog/documents/concepts/active-warranty-entitlement-fleet.md",
          "bundle_path": "bundle/documents/concepts/active-warranty-entitlement-fleet.md",
          "overview": """# Active Warranty Entitlement Fleet Rule

## Purpose
Defines which vehicles in `sa-demo-agentic.auto_aftersales_data.vehicle_ownership` (`5,000` total VINs) are actively entitled to OEM warranty coverage (`4,650` vehicles).

## Entitlement Rules by `ownership_status`
- `'Active'` (`4,582` VINs): **Entitled** when `warranty_end_date >= CURRENT_DATE()`.
- `'Transferred'` (`304` VINs): Standard 3-year factory warranty does NOT transfer to second-hand buyers. **Entitled ONLY IF `extended_warranty_purchased = TRUE` (`68` VINs)**; the remaining `236` transferred vehicles are out of coverage.
- `'Buyback'` (`114` VINs): Lemon-law/manufacturer buybacks; **Never entitled** to active customer warranty coverage.
- **Total Active Entitled Fleet**: `4,582 + 68 = 4,650` vehicles.
""",
          "queries": [],
      },
      {
          "id": "documents/concepts/dimension-catalog-padding-guardrail",
          "entry_id": "documents/concepts/dimension-catalog-padding-guardrail",
          "parent_id": "documents/concepts",
          "doc_type": "knowledge-base",
          "title": "Dimension Catalog Padding Guardrail (259 Rows Trap)",
          "catalog_path": "catalog/documents/concepts/dimension-catalog-padding-guardrail.md",
          "bundle_path": "bundle/documents/concepts/dimension-catalog-padding-guardrail.md",
          "overview": """# Dimension Catalog Padding Guardrail (259 Rows Trap)

## Purpose
Prevents 32x aggregation distortion caused by unallocated ERP placeholder rows in `plants`, `vehicle_models`, and `dealerships`.

## Active vs Padded Entity Counts
- `auto_manufacturing_data.plants`: `259` total rows -> **7 active plants** (`plant_id BETWEEN 1 AND 7`, total capacity `1,250,000` units/yr vs `45,860,000` padded).
- `auto_sales_data.vehicle_models`: `259` total rows -> **8 active models** (`model_id BETWEEN 1 AND 8`).
- `auto_sales_data.dealerships`: `259` total rows -> **8 active dealerships** (`dealership_id BETWEEN 1 AND 8`).
""",
          "queries": [],
      },
      {
          "id": "documents/playbooks",
          "entry_id": "documents/playbooks",
          "parent_id": "documents",
          "doc_type": "knowledge-base-index",
          "title": "Analytical Playbooks Index",
          "catalog_path": "catalog/documents/playbooks/index.md",
          "bundle_path": "bundle/documents/playbooks/index.md",
          "overview": """# Analytical Playbooks Index

## Purpose
Step-by-step SQL investigation playbooks for multi-dataset root-cause analysis.

## Playbooks
- `documents/playbooks/cross-domain-root-cause-playbook`: Tracing field warranty spikes back to assembly plant OEE and component source plants.
""",
          "queries": [],
      },
      {
          "id": "documents/playbooks/cross-domain-root-cause-playbook",
          "entry_id": "documents/playbooks/cross-domain-root-cause-playbook",
          "parent_id": "documents/playbooks",
          "doc_type": "knowledge-base",
          "title": "Cross-Domain Warranty & Manufacturing Root-Cause Playbook",
          "catalog_path": "catalog/documents/playbooks/cross-domain-root-cause-playbook.md",
          "bundle_path": "bundle/documents/playbooks/cross-domain-root-cause-playbook.md",
          "overview": """# Cross-Domain Warranty & Manufacturing Root-Cause Playbook

## Purpose
Guides Data Agents through a 4-stage investigation joining `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.

## Investigation Protocol
1. **Isolate Approved Spend & Split Fault Axis**: Query `warranty_claims` with `claim_status = 'Approved'` and segment into **OEM Assembly Fault (`supplier_fault = FALSE`, `$790,594.66`)** vs **Supplier Component Fault (`supplier_fault = TRUE`, `$464,191.35`)**.
2. **Attribute Assembly Faults to `build_plant_name`**: Join `warranty_claims.build_plant_name = plants.plant_name` and correlate with `assembly_line_status.operational_efficiency` and `quality_inspections`.
3. **Attribute Component Faults to `part_source_plant_name` & Audit Dealership Core Return**: Pre-aggregate `service_parts_usage` by `service_order_id` (`LOGICAL_AND(defective_part_returned)`) and identify which dealerships (`service_orders.dealership_id`) are failing to return defective supplier cores (`$282,518.23` in forfeited supplier recovery).
""",
          "queries": [],
      },
      {
          "id": "documents/learnings",
          "entry_id": "documents/learnings",
          "parent_id": "documents",
          "doc_type": "knowledge-base-index",
          "title": "Curation Loop Learnings Index",
          "catalog_path": "catalog/documents/learnings/index.md",
          "bundle_path": "bundle/documents/learnings/index.md",
          "overview": """# Curation Loop Learnings Index

## Purpose
Captures empirical failure modes observed during Data Agent benchmarking and encodes deterministic SQL guardrails.

## Learnings
- `documents/learnings/warranty-fanout-and-absorption-learnings`: Fixes `service_parts_usage` 1.78x fan-out and `service_type` 48% warranty absorption undercount.
""",
          "queries": [],
      },
      {
          "id": "documents/learnings/warranty-fanout-and-absorption-learnings",
          "entry_id": "documents/learnings/warranty-fanout-and-absorption-learnings",
          "parent_id": "documents/learnings",
          "doc_type": "knowledge-base",
          "title": "Warranty Join Fan-Out & Service Absorption Learnings",
          "catalog_path": "catalog/documents/learnings/warranty-fanout-and-absorption-learnings.md",
          "bundle_path": "bundle/documents/learnings/warranty-fanout-and-absorption-learnings.md",
          "overview": """# Warranty Join Fan-Out & Service Absorption Learnings

## Purpose
Prevents the three most common SQL calculation errors when querying `sa-demo-agentic.auto_aftersales_data`:

## Verified Guardrails
1. **Never join `warranty_claims` to `service_parts_usage` without pre-aggregating `service_parts_usage` to `service_order_id` grain**: Direct join multiplies `claim_amount` by 1.77x (`$2,226,419.83` instead of `$1,254,786.01`).
2. **Never filter `service_orders` by `service_type = 'Warranty Repair'` to measure total warranty-covered service cost**: Always filter `WHERE is_warranty_covered = TRUE` (`$1,591,386.85` across 1,894 orders vs `$826,977.80` on 922 `'Warranty Repair'` orders).
3. **Always reconcile `customer_identity_crosswalk` with `match_confidence >= 0.85` and `promo_code_received IN ('PLATINUM-VIP', 'PLATNUM-VIP')`**.
""",
          "queries": [],
      },
  ]

  links = [
      {
          "id": "link-join-claims-service-orders",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "target": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "source_col": "service_order_id",
          "target_col": "service_order_id",
          "directed": False,
      },
      {
          "id": "link-join-parts-service-orders",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage",
          "target": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "source_col": "service_order_id",
          "target_col": "service_order_id",
          "directed": False,
      },
      {
          "id": "link-join-claims-ownership",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "target": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "source_col": "vin",
          "target_col": "vin",
          "directed": False,
      },
      {
          "id": "link-join-ownership-sales",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "target": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_sales",
          "source_col": "vin",
          "target_col": "vin",
          "directed": False,
      },
      {
          "id": "link-join-ownership-models",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "target": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models",
          "source_col": "model_id",
          "target_col": "model_id",
          "directed": False,
      },
      {
          "id": "link-join-models-plants",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_sales_data/vehicle_models",
          "target": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants",
          "source_col": "plant_id",
          "target_col": "plant_id",
          "directed": False,
      },
      {
          "id": "link-join-claims-build-plant",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "target": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants",
          "source_col": "build_plant_name",
          "target_col": "plant_name",
          "directed": False,
      },
      {
          "id": "link-join-service-dealerships",
          "type": "schema-join",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "target": "assets/bigquery/sa-demo-agentic/auto_sales_data/dealerships",
          "source_col": "dealership_id",
          "target_col": "dealership_id",
          "directed": False,
      },
      {
          "id": "link-rel-claims-net-burden",
          "type": "related",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "target": "documents/concepts/net-oem-warranty-burden",
          "directed": False,
      },
      {
          "id": "link-rel-ownership-entitlement",
          "type": "related",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "target": "documents/concepts/active-warranty-entitlement-fleet",
          "directed": False,
      },
      {
          "id": "link-rel-plants-padding",
          "type": "related",
          "source": "assets/bigquery/sa-demo-agentic/auto_manufacturing_data/plants",
          "target": "documents/concepts/dimension-catalog-padding-guardrail",
          "directed": False,
      },
      {
          "id": "link-rel-claims-ontology",
          "type": "related",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "target": "documents/ontology/automotive-lifecycle-ontology",
          "directed": False,
      },
      {
          "id": "link-rel-parts-learnings",
          "type": "related",
          "source": "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage",
          "target": "documents/learnings/warranty-fanout-and-absorption-learnings",
          "directed": False,
      },
  ]
  return nodes, links, entry_group_res, glossary_res


def build_okf_and_kcmd_files() -> None:
  """Writes both the kcmd catalog/ tree and the strict OKF v0.2 bundle/ tree."""
  nodes, links, entry_group_res, _ = get_catalog_nodes()
  node_by_id = {n["id"]: n for n in nodes}

  # 1. Write catalog.yaml (kcmd format)
  write_text(
      "catalog.yaml",
      f"""name: {entry_group_res}
layout: okf
""",
  )

  # Map children per node for index listings and links per node
  children_map = {n["id"]: [] for n in nodes}
  for n in nodes:
    if n["parent_id"]:
      children_map[n["parent_id"]].append(n["id"])

  links_by_source = {n["id"]: [] for n in nodes}
  for lk in links:
    links_by_source[lk["source"]].append(lk)

  # 2. Write each node in both catalog/ (kcmd) and bundle/ (OKF v0.2)
  for n in nodes:
    full_entry_name = f"{entry_group_res}/entries/{n['entry_id']}"
    parent_entry_name = (
        f"{entry_group_res}/entries/{n['parent_id']}" if n["parent_id"] else None
    )
    is_leaf = len(children_map[n["id"]]) == 0

    # Build links frontmatter for OKF v0.2
    node_links = []
    for lk in links_by_source.get(n["id"], []):
      target_node = node_by_id[lk["target"]]
      rel_target = os.path.relpath(
          BASE_DIR / target_node["bundle_path"],
          (BASE_DIR / n["bundle_path"]).parent,
      )
      link_obj = {
          "target": rel_target,
          "type": lk["type"],
      }
      if "source_col" in lk:
        link_obj["source_column"] = lk["source_col"]
        link_obj["target_column"] = lk["target_col"]
      node_links.append(link_obj)

    # OKF v0.2 compliant frontmatter
    frontmatter = {
        "okf_version": "0.2",
        "title": n["title"],
        "type": n["doc_type"],
        "status": "stable" if is_leaf else "draft",
        "generated": {
            "by": "agent:dataplex-enrichment-agent/okf-serializer-0.2",
            "at": TIMESTAMP,
        },
        "sources": [
            f"bigquery://projects/{PROJECT_ID}/datasets/auto_aftersales_data",
            f"bigquery://projects/{PROJECT_ID}/datasets/auto_sales_data",
            f"bigquery://projects/{PROJECT_ID}/datasets/auto_manufacturing_data",
        ],
    }
    if is_leaf:
      frontmatter["verified"] = [
          {"by": "human:asudesh@google.com", "at": TIMESTAMP}
      ]
    if node_links:
      frontmatter["links"] = node_links
    if n["queries"]:
      frontmatter["queries"] = n["queries"]

    frontmatter["x-kcmd"] = {
        "name": full_entry_name,
        "entryType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/entryTypes/document",
        "parentEntry": parent_entry_name,
        "documentType": n["doc_type"],
    }

    yaml_lines = ["---"]
    yaml_lines.append(f'okf_version: "0.2"')
    yaml_lines.append(f'title: {json.dumps(n["title"])}')
    yaml_lines.append(f'type: "{n["doc_type"]}"')
    yaml_lines.append(f'status: "{frontmatter["status"]}"')
    yaml_lines.append("generated:")
    yaml_lines.append('  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"')
    yaml_lines.append(f'  at: "{TIMESTAMP}"')
    if is_leaf:
      yaml_lines.append("verified:")
      yaml_lines.append('  - by: "human:asudesh@google.com"')
      yaml_lines.append(f'    at: "{TIMESTAMP}"')
    yaml_lines.append("sources:")
    for src in frontmatter["sources"]:
      yaml_lines.append(f'  - "{src}"')
    if node_links:
      yaml_lines.append("links:")
      for lk_obj in node_links:
        yaml_lines.append(f'  - target: "{lk_obj["target"]}"')
        yaml_lines.append(f'    type: "{lk_obj["type"]}"')
        if "source_column" in lk_obj:
          yaml_lines.append(f'    source_column: "{lk_obj["source_column"]}"')
          yaml_lines.append(f'    target_column: "{lk_obj["target_column"]}"')
    if n["queries"]:
      yaml_lines.append("queries:")
      for q in n["queries"]:
        yaml_lines.append(f'  - title: {json.dumps(q["title"])}')
        yaml_lines.append(f'    description: {json.dumps(q["description"])}')
        yaml_lines.append("    sql: |")
        for sql_line in q["sql"].splitlines():
          yaml_lines.append(f"      {sql_line}")
    yaml_lines.append("x-kcmd:")
    yaml_lines.append(f'  name: "{full_entry_name}"')
    yaml_lines.append(
        f'  entryType: "projects/{DATAPLEX_TYPES_NUM}/locations/global/entryTypes/document"'
    )
    if parent_entry_name:
      yaml_lines.append(f'  parentEntry: "{parent_entry_name}"')
    yaml_lines.append(f'  documentType: "{n["doc_type"]}"')
    yaml_lines.append("---")

    doc_content = "\n".join(yaml_lines) + "\n\n" + n["overview"].strip() + "\n"
    write_text(n["catalog_path"], doc_content)
    write_text(n["bundle_path"], doc_content)

  # 3. Write bundle/index.md and catalog/index.md (OKF v0.2 Backbone Index)
  index_table_rows = []
  for n in nodes:
    rel_p = n["bundle_path"].replace("bundle/", "")
    status = "stable" if len(children_map[n["id"]]) == 0 else "draft"
    index_table_rows.append(
        f"| [`{n['id']}`]({rel_p}) | `{n['doc_type']}` | `{status}` | {n['title']} |"
    )

  backbone_index = f"""---
okf_version: "0.2"
title: "Automotive Enterprise OKF v0.2 Context Set Index"
type: "knowledge-base-index"
status: "stable"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "{TIMESTAMP}"
verified:
  - by: "human:asudesh@google.com"
    at: "{TIMESTAMP}"
x-kcmd:
  name: "{entry_group_res}/entries/index"
  entryType: "projects/{DATAPLEX_TYPES_NUM}/locations/global/entryTypes/document"
  documentType: "knowledge-base-index"
---

# Automotive Enterprise OKF v0.2 Context Set Index (`sa-demo-agentic`)

## Purpose
Root Open Knowledge Format (`OKF v0.2`) backbone index cataloging all **26 progressive-disclosure entries** and **13 semantic/join entry links** across `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.

## Bundle Manifest ({len(nodes)} Entries)

| Entry ID | OKF Document Type | Status | Title |
| :--- | :--- | :--- | :--- |
""" + "\n".join(index_table_rows)

  write_text("bundle/index.md", backbone_index)
  write_text("catalog/index.md", backbone_index)

  # 4. Write bundle/log.md and catalog/log.md (OKF v0.2 Operational Audit Log)
  backbone_log = f"""---
okf_version: "0.2"
title: "OKF v0.2 Curation & Verification Log"
type: "knowledge-base"
status: "stable"
generated:
  by: "agent:dataplex-enrichment-agent/okf-serializer-0.2"
  at: "{TIMESTAMP}"
---

# OKF v0.2 Curation & Verification Log

## [{TIMESTAMP}] publish — Context Set `auto-enterprise-okf-context-set`
- **Target Project**: `sa-demo-agentic` (`{PROJECT_NUMBER}`)
- **Target Location**: `{LOCATION}`
- **Profile**: `PROGRESSIVE` (`progressive_disclosure`)
- **Entries Curated**: `{len(nodes)}` (`14` BigQuery `context-overlay` table nodes, `6` `knowledge-base` domain/concept/playbook/learning nodes, `7` `knowledge-base-index` hierarchy nodes)
- **EntryLinks Created**: `{len(links)}` (`8` `schema-join` links, `5` `related` tribal knowledge links, plus glossary `definition` links)
- **Empirical Verification**: Verified against live BigQuery datasets `auto_aftersales_data`, `auto_sales_data`, and `auto_manufacturing_data`.
"""
  write_text("bundle/log.md", backbone_log)
  write_text("catalog/log.md", backbone_log)

  # Save machine-readable manifest for the publisher script
  manifest = {
      "project_id": PROJECT_ID,
      "project_number": PROJECT_NUMBER,
      "location": LOCATION,
      "entry_group_id": ENTRY_GROUP_ID,
      "nodes": nodes,
      "links": links,
  }
  write_text("bundle/okf_manifest.json", json.dumps(manifest, indent=2))


def build_html_visualizer() -> None:
  """Generates an interactive HTML5 Knowledge Graph Visualizer for the OKF v0.2 Bundle."""
  nodes, links, _, _ = get_catalog_nodes()
  html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OKF v0.2 Knowledge Catalog Graph — sa-demo-agentic</title>
<style>
  :root {{
    --bg: #0f172a;
    --panel: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --overlay: #22c55e;
    --concept: #a855f7;
    --index: #f59e0b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: grid;
    grid-template-columns: 340px 1fr 420px;
    height: 100vh;
    overflow: hidden;
  }}
  .sidebar, .inspector {{
    background: var(--panel);
    border-right: 1px solid var(--border);
    padding: 20px;
    overflow-y: auto;
  }}
  .inspector {{
    border-right: none;
    border-left: 1px solid var(--border);
  }}
  h1 {{ font-size: 18px; margin: 0 0 8px 0; color: var(--accent); }}
  h2 {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--muted); margin: 20px 0 10px 0; }}
  .badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
  }}
  .badge-overlay {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
  .badge-kb {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; }}
  .badge-index {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
  .node-item {{
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .node-item:hover, .node-item.active {{
    border-color: var(--accent);
    background: rgba(56, 189, 248, 0.1);
  }}
  .canvas-wrap {{
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }}
  .toolbar {{
    padding: 12px 20px;
    background: rgba(30, 41, 59, 0.85);
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  svg {{
    flex: 1;
    width: 100%;
    height: 100%;
    cursor: grab;
  }}
  pre {{
    background: #0b1120;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
    white-space: pre-wrap;
    font-size: 12px;
    color: #e2e8f0;
    line-height: 1.45;
  }}
</style>
</head>
<body>
<div class="sidebar">
  <h1>OKF v0.2 Context Set</h1>
  <div style="font-size: 12px; color: var(--muted); margin-bottom: 12px;">
    Project: <code>sa-demo-agentic</code><br>
    EntryGroup: <code>auto-enterprise-okf-context-set</code>
  </div>
  <div>
    <span class="badge badge-overlay">14 Table Overlays</span>
    <span class="badge badge-kb">6 Tribal Docs</span>
    <span class="badge badge-index">7 Indexes</span>
  </div>
  <h2>Context Set Entries</h2>
  <div id="node-list"></div>
</div>
<div class="canvas-wrap">
  <div class="toolbar">
    <div style="font-size: 13px;">
      <strong>Interactive Progressive-Disclosure Knowledge Graph</strong> · Click any node to inspect its OKF v0.2 Markdown & Golden SQL
    </div>
    <div style="font-size: 12px; color: var(--muted);">
      Solid Blue = Hierarchy · Dashed Green = <code>schema-join</code> · Dotted Purple = <code>related</code>
    </div>
  </div>
  <svg id="graph" viewBox="0 0 1000 760"></svg>
</div>
<div class="inspector">
  <h1 id="insp-title">Select a Node</h1>
  <div id="insp-meta" style="margin-bottom: 12px;"></div>
  <h2>OKF v0.2 Overview Aspect</h2>
  <pre id="insp-content"></pre>
</div>
<script>
const NODES = {json.dumps(nodes)};
const LINKS = {json.dumps(links)};

const listEl = document.getElementById('node-list');
const svg = document.getElementById('graph');

// Compute layered positions
const positions = {{}};
const layers = {{
  root: NODES.filter(n => n.id === 'agents'),
  l1: NODES.filter(n => ['assets/bigquery/sa-demo-agentic/auto_aftersales_data', 'assets/bigquery/sa-demo-agentic/auto_sales_data', 'assets/bigquery/sa-demo-agentic/auto_manufacturing_data', 'documents/ontology', 'documents/concepts', 'documents/playbooks', 'documents/learnings'].includes(n.id)),
  overlays: NODES.filter(n => n.doc_type === 'context-overlay'),
  kb: NODES.filter(n => n.doc_type === 'knowledge-base' && n.id !== 'agents')
}};

positions['agents'] = {{x: 500, y: 55}};
layers.l1.forEach((n, i) => {{
  positions[n.id] = {{x: 90 + i * 135, y: 185}};
}});
layers.overlays.forEach((n, i) => {{
  const row = i % 2;
  const col = Math.floor(i / 2);
  positions[n.id] = {{x: 80 + col * 140, y: 360 + row * 120}};
}});
layers.kb.forEach((n, i) => {{
  positions[n.id] = {{x: 110 + i * 155, y: 650}};
}});
NODES.forEach((n, i) => {{
  if (!positions[n.id]) {{
    positions[n.id] = {{x: 180 + (i * 95) % 640, y: 115}};
  }}
}});

function selectNode(node) {{
  document.querySelectorAll('.node-item').forEach(el => el.classList.toggle('active', el.dataset.id === node.id));
  document.getElementById('insp-title').textContent = node.title;
  document.getElementById('insp-meta').innerHTML = `
    <span class="badge ${{node.doc_type === 'context-overlay' ? 'badge-overlay' : node.doc_type === 'knowledge-base' ? 'badge-kb' : 'badge-index'}}">${{node.doc_type}}</span>
    <code style="font-size:11px;color:#94a3b8;">${{node.id}}</code>
  `;
  document.getElementById('insp-content').textContent = node.overview;
}}

// Render edges
NODES.forEach(n => {{
  if (n.parent_id && positions[n.parent_id] && positions[n.id]) {{
    const p1 = positions[n.parent_id], p2 = positions[n.id];
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', p1.x); line.setAttribute('y1', p1.y);
    line.setAttribute('x2', p2.x); line.setAttribute('y2', p2.y);
    line.setAttribute('stroke', '#334155');
    line.setAttribute('stroke-width', '1.5');
    svg.appendChild(line);
  }}
}});

LINKS.forEach(lk => {{
  const p1 = positions[lk.source], p2 = positions[lk.target];
  if (!p1 || !p2) return;
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', p1.x); line.setAttribute('y1', p1.y);
  line.setAttribute('x2', p2.x); line.setAttribute('y2', p2.y);
  line.setAttribute('stroke', lk.type === 'schema-join' ? '#22c55e' : '#a855f7');
  line.setAttribute('stroke-width', '2');
  line.setAttribute('stroke-dasharray', lk.type === 'schema-join' ? '6,4' : '2,4');
  svg.appendChild(line);
}});

// Render nodes
NODES.forEach(n => {{
  const item = document.createElement('div');
  item.className = 'node-item';
  item.dataset.id = n.id;
  const badgeClass = n.doc_type === 'context-overlay' ? 'badge-overlay' : n.doc_type === 'knowledge-base' ? 'badge-kb' : 'badge-index';
  item.innerHTML = `<span class="badge ${{badgeClass}}">${{n.doc_type}}</span><div style="font-weight:600;font-size:13px;margin-top:4px;">${{n.title}}</div><div style="font-size:11px;color:#94a3b8;word-break:break-all;">${{n.id}}</div>`;
  item.onclick = () => selectNode(n);
  listEl.appendChild(item);

  const pos = positions[n.id];
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.style.cursor = 'pointer';
  g.onclick = () => selectNode(n);

  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', pos.x);
  circle.setAttribute('cy', pos.y);
  circle.setAttribute('r', n.id === 'agents' ? 22 : n.doc_type === 'context-overlay' ? 16 : 14);
  circle.setAttribute('fill', n.doc_type === 'context-overlay' ? '#16a34a' : n.doc_type === 'knowledge-base' ? '#9333ea' : '#d97706');
  circle.setAttribute('stroke', '#f8fafc');
  circle.setAttribute('stroke-width', '2');
  g.appendChild(circle);

  const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  label.setAttribute('x', pos.x);
  label.setAttribute('y', pos.y + 28);
  label.setAttribute('text-anchor', 'middle');
  label.setAttribute('fill', '#e2e8f0');
  label.setAttribute('font-size', '11');
  label.textContent = n.title.length > 22 ? n.title.slice(0, 20) + '…' : n.title;
  g.appendChild(label);

  svg.appendChild(g);
}});

selectNode(NODES.find(n => n.id === 'assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims'));
</script>
</body>
</html>
"""
  write_text("okf_graph_visualizer.html", html)


if __name__ == "__main__":
  build_raw_tribal_knowledge()
  build_okf_and_kcmd_files()
  build_html_visualizer()
  print("Successfully built OKF v0.2 bundle, kcmd catalog, raw tribal knowledge corpus, and interactive HTML visualizer in", BASE_DIR)
