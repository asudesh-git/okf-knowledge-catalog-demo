#!/usr/bin/env python3
"""Publishes the OKF v0.2 Bundle, Business Glossary, and BigQuery Schema Enrichments to sa-demo-agentic.

Also executes the empirical Before-vs-After OKF SQL Benchmark against BigQuery in sa-demo-agentic.
"""

import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_DIR = Path("/usr/local/google/home/asudesh/ace/okf-knowledge-catalog-demo")
MANIFEST_PATH = BASE_DIR / "bundle" / "okf_manifest.json"
PROJECT_ID = "sa-demo-agentic"
PROJECT_NUMBER = "229419534491"
DATAPLEX_TYPES_NUM = "655216118709"
LOCATION = "us-central1"
GLOSSARY_ID = "auto-enterprise-okf-glossary"
TIMESTAMP = "2026-10-19T15:40:00Z"


def get_token() -> str:
  return subprocess.check_output(
      ["gcloud", "auth", "print-access-token"], text=True
  ).strip()


def api_call(
    method: str, url: str, token: str, body: dict | None = None
) -> tuple[int, dict]:
  headers = {
      "Authorization": f"Bearer {token}",
      "x-goog-user-project": PROJECT_ID,
      "Content-Type": "application/json",
  }
  data = json.dumps(body).encode("utf-8") if body is not None else None
  req = urllib.request.Request(url, data=data, headers=headers, method=method)
  try:
    with urllib.request.urlopen(req, timeout=30) as resp:
      raw = resp.read().decode("utf-8")
      return resp.status, json.loads(raw) if raw else {}
  except urllib.error.HTTPError as e:
    raw = e.read().decode("utf-8", errors="replace")
    try:
      return e.code, json.loads(raw)
    except Exception:
      return e.code, {"raw_error": raw}


def run_bq_query(token: str, sql: str) -> list[dict]:
  url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT_ID}/queries"
  status, resp = api_call(
      "POST",
      url,
      token,
      {"query": sql, "useLegacySql": False, "timeoutMs": 30000},
  )
  if status != 200:
    raise RuntimeError(f"BQ query failed ({status}): {resp}")
  fields = [f["name"] for f in resp.get("schema", {}).get("fields", [])]
  rows = []
  for r in resp.get("rows", []):
    vals = [c.get("v") for c in r.get("f", [])]
    rows.append(dict(zip(fields, vals)))
  return rows


def ensure_glossary_and_terms(token: str) -> dict:
  """Creates or updates the Business Glossary and 6 canonical terms in global location."""
  glossary_parent = f"projects/{PROJECT_ID}/locations/global"
  glossary_name = f"{glossary_parent}/glossaries/{GLOSSARY_ID}"
  url_get = f"https://dataplex.googleapis.com/v1/{glossary_name}"
  st, res = api_call("GET", url_get, token)
  if st == 404:
    url_create = f"https://dataplex.googleapis.com/v1/{glossary_parent}/glossaries?glossaryId={GLOSSARY_ID}"
    st, res = api_call(
        "POST",
        url_create,
        token,
        {
            "displayName": "Automotive Enterprise OKF v0.2 Glossary",
            "description": (
                "Canonical business metrics, warranty adjudication formulas,"
                " and fleet entitlement definitions curated via Open Knowledge"
                " Format (OKF v0.2)."
            ),
            "labels": {"okf-version": "v0-2", "domain": "automotive-enterprise"},
        },
    )
    print(f"Glossary create status={st}: {res.get('name')}")
    time.sleep(3)
  else:
    print(f"Glossary already exists: {glossary_name}")

  terms = [
      (
          "net_oem_warranty_burden",
          "Net OEM Warranty Burden",
          "Realized Approved Warranty Cost ($1,254,786.01) minus 70% Recoverable Supplier Chargeback ($42,415.72, requiring all defective parts returned on the service order) = $1,212,370.29.",
      ),
      (
          "realized_warranty_cost",
          "Realized Warranty Cost",
          "SUM(claim_amount) WHERE claim_status = 'Approved' ($1,254,786.01 across 1,331 claims). Excludes Pending, Under Review, and Denied claims.",
      ),
      (
          "open_warranty_exposure",
          "Open Warranty Reserve Exposure",
          "SUM(claim_amount) WHERE claim_status IN ('Pending', 'Under Review') ($404,016.42 across 419 claims).",
      ),
      (
          "unrecovered_supplier_leakage",
          "Unrecovered Supplier Chargeback Leakage",
          "70% of Approved supplier_fault=TRUE claim_amount forfeited when dealerships fail to return defective parts (defective_part_returned=FALSE in service_parts_usage): $282,518.23.",
      ),
      (
          "oem_warranty_absorption",
          "Total OEM Warranty-Covered Service Absorption",
          "SUM(total_cost - customer_paid_amount) WHERE is_warranty_covered = TRUE in service_orders ($1,591,386.85 across 1,894 orders, including Warranty Repair, covered Repair, and Recall Service).",
      ),
      (
          "active_warranty_entitlement_fleet",
          "Active Warranty Entitlement Fleet",
          "Vehicles with warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE)): 4,650 vehicles.",
      ),
  ]

  created_terms = {}
  for term_id, display_name, desc in terms:
    term_name = f"{glossary_name}/terms/{term_id}"
    st_t, _ = api_call("GET", f"https://dataplex.googleapis.com/v1/{term_name}", token)
    if st_t == 404:
      url_tc = f"https://dataplex.googleapis.com/v1/{glossary_name}/terms?termId={term_id}"
      st_tc, res_tc = api_call(
          "POST",
          url_tc,
          token,
          {
              "displayName": display_name,
              "description": desc,
              "parent": glossary_name,
          },
      )
      print(f"  Created term {term_id}: status={st_tc}")
    else:
      print(f"  Term already exists: {term_id}")

    # Also update overview aspect on the @dataplex mirrored entry for this term
    dataplex_term_entry = (
        f"projects/{PROJECT_ID}/locations/global/entryGroups/@dataplex/entries/"
        f"projects/{PROJECT_NUMBER}/locations/global/glossaries/{GLOSSARY_ID}/terms/{term_id}"
    )
    created_terms[term_id] = dataplex_term_entry
  return created_terms


def ensure_entry_group(token: str, entry_group_id: str) -> str:
  """Ensures the EntryGroup exists in us-central1 (creating with type=context-set if supported)."""
  parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
  eg_name = f"{parent}/entryGroups/{entry_group_id}"
  st, res = api_call("GET", f"https://dataplex.googleapis.com/v1/{eg_name}", token)
  if st == 200:
    print(f"EntryGroup exists: {eg_name}")
    return eg_name

  url_create = f"https://dataplex.googleapis.com/v1/{parent}/entryGroups?entryGroupId={entry_group_id}"
  # Try with type="context-set" first (Knowledge Studio Context Set spec)
  body_with_type = {
      "displayName": "Automotive Enterprise OKF v0.2 Context Set",
      "description": (
          "Open Knowledge Format (OKF v0.2) progressive-disclosure Context Set"
          " for sa-demo-agentic (auto_aftersales_data, auto_sales_data,"
          " auto_manufacturing_data)."
      ),
      "type": "context-set",
      "labels": {
          "okf-version": "v0-2",
          "entrygroup-type": "context-set",
          "created-by": "okf-publisher",
      },
  }
  st, res = api_call("POST", url_create, token, body_with_type)
  if st in (200, 201):
    print(f"Created EntryGroup with type=context-set: {eg_name}")
    time.sleep(3)
    return eg_name

  print(f"Create with type='context-set' returned {st} ({res}); creating via standard v1 schema...")
  body_std = {
      "displayName": "Automotive Enterprise OKF v0.2 Context Set",
      "description": (
          "Open Knowledge Format (OKF v0.2) progressive-disclosure Context Set"
          " for sa-demo-agentic (auto_aftersales_data, auto_sales_data,"
          " auto_manufacturing_data)."
      ),
      "labels": {
          "okf-version": "v0-2",
          "entrygroup-type": "context-set",
          "created-by": "okf-publisher",
      },
  }
  st2, res2 = api_call("POST", url_create, token, body_std)
  print(f"Created EntryGroup {eg_name}: status={st2}")
  time.sleep(3)
  return eg_name


def build_dataplex_entry_payload(
    eg_name: str,
    entry_id: str,
    parent_id: str | None,
    title: str,
    doc_type: str,
    overview_md: str,
) -> dict:
  entry_name = f"{eg_name}/entries/{entry_id}"
  payload = {
      "name": entry_name,
      "entryType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/entryTypes/document",
      "entrySource": {
          "displayName": title,
          "description": f"OKF v0.2 {doc_type}: {title}",
          "system": "OKF Knowledge Catalog",
          "platform": "Dataplex Context Set",
      },
      "aspects": {
          f"{DATAPLEX_TYPES_NUM}.global.overview": {
              "aspectType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/aspectTypes/overview",
              "data": {
                  "content": overview_md,
                  "contentType": "MARKDOWN",
              },
          },
          f"{DATAPLEX_TYPES_NUM}.global.document": {
              "aspectType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/aspectTypes/document",
              "data": {
                  "type": doc_type,
                  "job": {
                      "name": "enrichment-agent/okf-v0.2-publish",
                      "runTime": TIMESTAMP,
                  },
              },
          },
      },
  }
  if parent_id:
    payload["parentEntry"] = f"{eg_name}/entries/{parent_id}"
  return payload


def upsert_entry(token: str, eg_name: str, entry_id: str, payload: dict) -> tuple[int, str]:
  """Creates or updates a hierarchical entry in Dataplex Knowledge Catalog."""
  entry_name = f"{eg_name}/entries/{entry_id}"
  encoded_id = urllib.parse.quote(entry_id, safe="")
  create_url = f"https://dataplex.googleapis.com/v1/{eg_name}/entries?entryId={encoded_id}"
  st, res = api_call("POST", create_url, token, payload)
  if st in (200, 201):
    return st, res.get("name", entry_name)
  if st == 409:
    # Already exists -> PATCH aspects and entrySource
    patch_url = f"https://dataplex.googleapis.com/v1/{entry_name}?updateMask=aspects,entrySource"
    st_p, res_p = api_call("PATCH", patch_url, token, payload)
    return st_p, res_p.get("name", entry_name)
  return st, json.dumps(res)


def upsert_entry_link(
    token: str,
    eg_name: str,
    link_id: str,
    link_type: str,
    source_entry: str,
    target_entry: str,
    source_col: str | None = None,
    target_col: str | None = None,
    directed: bool = False,
) -> tuple[int, str]:
  link_name = f"{eg_name}/entryLinks/{link_id}"
  src_ref = {
      "name": source_entry,
      "type": "SOURCE" if directed else "UNSPECIFIED",
  }
  tgt_ref = {
      "name": target_entry,
      "type": "TARGET" if directed else "UNSPECIFIED",
  }
  # Only attach Schema.<col> path when referencing a @bigquery entry (which carries a Schema aspect)
  if source_col and "/entryGroups/@bigquery/" in source_entry:
    src_ref["path"] = f"Schema.{source_col}"
  if target_col and "/entryGroups/@bigquery/" in target_entry:
    tgt_ref["path"] = f"Schema.{target_col}"

  payload = {
      "name": link_name,
      "entryLinkType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/entryLinkTypes/{link_type}",
      "entryReferences": [src_ref, tgt_ref],
  }
  if link_type == "schema-join":
    payload["aspects"] = {
        f"{DATAPLEX_TYPES_NUM}.global.schema-join": {
            "aspectType": f"projects/{DATAPLEX_TYPES_NUM}/locations/global/aspectTypes/schema-join",
            "data": {
                "userManaged": True,
                "joins": [
                    {
                        "type": "FOREIGN_KEY",
                        "inferenceSource": "AGENT",
                        "source": {"name": source_entry, "fields": [source_col or "id"]},
                        "target": {"name": target_entry, "fields": [target_col or "id"]},
                    }
                ],
            },
        }
    }
  create_url = f"https://dataplex.googleapis.com/v1/{eg_name}/entryLinks?entryLinkId={link_id}"
  st, res = api_call("POST", create_url, token, payload)
  if st == 409:
    # Delete and recreate so references stay fresh
    api_call("DELETE", f"https://dataplex.googleapis.com/v1/{link_name}", token)
    st, res = api_call("POST", create_url, token, payload)
  return st, res.get("name", json.dumps(res))


def publish_bundle_to_entry_group(
    token: str, eg_name: str, manifest: dict, term_entries: dict
) -> dict:
  """Publishes all OKF v0.2 entries and entryLinks into the specified EntryGroup."""
  nodes = manifest["nodes"]
  links = manifest["links"]

  published_entries = []
  # Also publish the updated top-level 'index' entry (so enrichment-entry-group's index is updated too!)
  index_md = (BASE_DIR / "bundle" / "index.md").read_text(encoding="utf-8").split("---", 2)[-1].strip()
  idx_payload = build_dataplex_entry_payload(
      eg_name,
      "index",
      None,
      "Automotive Enterprise OKF v0.2 Context Set Index",
      "knowledge-base-index",
      index_md,
  )
  st_idx, name_idx = upsert_entry(token, eg_name, "index", idx_payload)
  published_entries.append({"entry_id": "index", "status": st_idx, "name": name_idx})

  # Publish nodes in topological order (parents before children)
  for n in nodes:
    payload = build_dataplex_entry_payload(
        eg_name,
        n["entry_id"],
        n["parent_id"],
        n["title"],
        n["doc_type"],
        n["overview"],
    )
    st, name = upsert_entry(token, eg_name, n["entry_id"], payload)
    published_entries.append({"entry_id": n["entry_id"], "status": st, "name": name})
    print(f"  [{eg_name.split('/')[-1]}] Upserted entry {n['entry_id']} -> {st}")

  published_links = []
  for lk in links:
    src_entry = f"{eg_name}/entries/{lk['source']}"
    tgt_entry = f"{eg_name}/entries/{lk['target']}"
    st_l, name_l = upsert_entry_link(
        token,
        eg_name,
        lk["id"],
        lk["type"],
        src_entry,
        tgt_entry,
        lk.get("source_col"),
        lk.get("target_col"),
        lk.get("directed", False),
    )
    published_links.append({"link_id": lk["id"], "type": lk["type"], "status": st_l, "name": name_l})
    print(f"  [{eg_name.split('/')[-1]}] Upserted link {lk['id']} ({lk['type']}) -> {st_l}")

  # Also create 'definition' EntryLinks binding table overlays to @dataplex Business Glossary terms
  glossary_bindings = [
      (
          "link-def-claims-net-burden",
          "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "claim_amount",
          term_entries["net_oem_warranty_burden"],
      ),
      (
          "link-def-claims-realized-cost",
          "assets/bigquery/sa-demo-agentic/auto_aftersales_data/warranty_claims",
          "claim_status",
          term_entries["realized_warranty_cost"],
      ),
      (
          "link-def-parts-leakage",
          "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_parts_usage",
          "defective_part_returned",
          term_entries["unrecovered_supplier_leakage"],
      ),
      (
          "link-def-orders-absorption",
          "assets/bigquery/sa-demo-agentic/auto_aftersales_data/service_orders",
          "is_warranty_covered",
          term_entries["oem_warranty_absorption"],
      ),
      (
          "link-def-ownership-entitlement",
          "assets/bigquery/sa-demo-agentic/auto_aftersales_data/vehicle_ownership",
          "ownership_status",
          term_entries["active_warranty_entitlement_fleet"],
      ),
  ]
  for link_id, src_rel, src_col, tgt_term_entry in glossary_bindings:
    src_entry = f"{eg_name}/entries/{src_rel}"
    st_g, name_g = upsert_entry_link(
        token,
        eg_name,
        link_id,
        "definition",
        src_entry,
        tgt_term_entry,
        source_col=None,
        target_col=None,
        directed=True,
    )
    published_links.append({"link_id": link_id, "type": "definition", "status": st_g, "name": name_g})
    print(f"  [{eg_name.split('/')[-1]}] Upserted glossary definition link {link_id} -> {st_g}")

  return {"entries": published_entries, "links": published_links}


def enrich_bigquery_table_schemas(token: str) -> list[dict]:
  """Patches BigQuery table and column descriptions on auto_aftersales_data so BQ & Dataplex reflect OKF."""
  table_enrichments = {
      "warranty_claims": {
          "description": (
              "OKF v0.2 Enriched: Dealership warranty claim financial adjudication"
              " (1,894 rows; 1:1 with service_orders where is_warranty_covered=TRUE)."
              " Filter claim_status='Approved' ($1,254,786.01) for realized spend."
              " Supplier fault claims recover 70% ONLY when all replaced parts in"
              " service_parts_usage have defective_part_returned=TRUE."
          ),
          "columns": {
              "claim_id": "Primary key warranty claim identifier (1..1894).",
              "service_order_id": "Foreign key to service_orders.service_order_id (1:1 grain).",
              "vin": "17-character Vehicle Identification Number (joins to vehicle_ownership.vin and auto_sales_data.vehicle_sales.vin).",
              "claim_date": "Date warranty claim was submitted for adjudication.",
              "failure_component": "Failed subsystem (Engine, Battery, Electrical, Brakes, Transmission, Suspension, HVAC, Infotainment, Steering, Exhaust, Fuel System).",
              "claim_amount": "Requested claim USD. Caveat: Filter claim_status='Approved' ($1,254,786.01) for realized spend; raw sum ($1,798,306.90) includes Pending, Under Review, and Denied.",
              "claim_status": "Adjudication state: 'Approved' (realized expense), 'Pending' / 'Under Review' (open reserve exposure $404,016.42), 'Denied' ($0 liability).",
              "build_plant_name": "Final vehicle assembly plant name (joins to auto_manufacturing_data.plants.plant_name). Use for OEM assembly quality audits.",
              "part_source_plant_name": "Component manufacturing plant name that produced the failed replacement part.",
              "supplier_fault": "TRUE if defect originated from external supplier component (eligible for 70% chargeback recovery if defective_part_returned=TRUE in service_parts_usage); FALSE for internal OEM assembly fault.",
          },
      },
      "service_orders": {
          "description": (
              "OKF v0.2 Enriched: Dealership service bay repair and maintenance orders"
              " (6,104 rows). Caveat: Use is_warranty_covered=TRUE ($1,591,386.85 across"
              " 1,894 orders) rather than service_type='Warranty Repair' ($826,977.80)"
              " to capture all OEM-absorbed warranty repairs."
          ),
          "columns": {
              "service_order_id": "Primary key service order identifier (1..6104).",
              "vin": "Serviced vehicle VIN (joins to vehicle_ownership.vin).",
              "dealership_id": "Servicing dealership ID (joins to auto_sales_data.dealerships.dealership_id; active IDs 1..8).",
              "technician_id": "Lead technician ID (joins to technicians.technician_id).",
              "service_date": "Service completion date.",
              "service_type": "Bay category ('Routine Maintenance', 'Repair', 'Warranty Repair', 'Recall Service'). Note: 690 'Repair' and 282 'Recall Service' orders also have is_warranty_covered=TRUE.",
              "labor_hours": "Billable technician labor hours.",
              "labor_cost": "Dealership labor charge (USD).",
              "parts_cost": "Sum of replaced parts cost for this order (USD).",
              "total_cost": "Total service order cost (labor_cost + parts_cost, USD).",
              "customer_paid_amount": "Out-of-pocket USD paid by customer ($0.00 when is_warranty_covered=TRUE).",
              "is_warranty_covered": "Canonical boolean flag (TRUE for 1,894 orders, $1,591,386.85 absorbed) indicating OEM warranty absorption.",
          },
      },
      "service_parts_usage": {
          "description": (
              "OKF v0.2 Enriched: Line-item replacement parts installed during service"
              " orders (10,861 rows; N:1 to service_order_id). Pre-aggregate by"
              " service_order_id before joining to warranty_claims to avoid 1.78x fan-out."
          ),
          "columns": {
              "usage_id": "Primary key part usage line item ID (1..10861).",
              "service_order_id": "Foreign key to service_orders.service_order_id (N:1 grain; pre-aggregate before joining to warranty_claims).",
              "part_number": "Catalog part number (PART-100..PART-149; joins to auto_manufacturing_data.parts_inventory.part_number).",
              "part_name": "Replacement component description.",
              "part_category": "Component subsystem category.",
              "quantity_used": "Units installed.",
              "unit_cost": "Wholesale cost per unit (USD).",
              "total_part_cost": "Extended part cost (quantity_used * unit_cost, USD).",
              "defective_part_returned": "TRUE if defective core was returned to OEM teardown depot. Required (LOGICAL_AND(defective_part_returned)=TRUE per service_order_id) to recover 70% supplier chargeback on supplier_fault warranty claims.",
          },
      },
      "vehicle_ownership": {
          "description": (
              "OKF v0.2 Enriched: VIN-level ownership and warranty entitlement registry"
              " (5,000 rows). Active Warranty Entitlement Fleet (4,650 VINs) requires"
              " ownership_status='Active' (4,582) OR (ownership_status='Transferred'"
              " AND extended_warranty_purchased=TRUE, 68)."
          ),
          "columns": {
              "vin": "Primary key 17-character Vehicle Identification Number (1:1 with auto_sales_data.vehicle_sales.vin).",
              "customer_id": "Current vehicle owner ID.",
              "model_id": "Vehicle model ID (1..8; joins to auto_sales_data.vehicle_models.model_id).",
              "sale_date": "Original retail sale date.",
              "warranty_start_date": "Factory warranty start date.",
              "warranty_end_date": "Warranty expiration date (3yr standard, 5yr extended).",
              "extended_warranty_purchased": "TRUE if transferable 5-year extended warranty was purchased (required for coverage to survive secondary-market 'Transferred' status).",
              "current_mileage": "Latest odometer reading (miles).",
              "ownership_status": "Lifecycle status: 'Active' (4,582 covered), 'Transferred' (304; only 68 with extended_warranty_purchased=TRUE retain coverage), 'Buyback' (114 excluded).",
          },
      },
      "technicians": {
          "description": "OKF v0.2 Enriched: Certified dealership service technicians (120 rows) across 8 active dealerships.",
          "columns": {
              "technician_id": "Primary key technician ID (1..120).",
              "technician_name": "Technician identifier.",
              "dealership_id": "Assigned dealership ID (1..8; joins to auto_sales_data.dealerships.dealership_id).",
              "certification_level": "Certification tier ('Master', 'Specialist', 'Senior', 'Apprentice').",
              "specialty": "Primary technical subsystem specialty.",
              "hire_date": "Dealership hire date.",
          },
      },
      "recall_campaigns": {
          "description": "OKF v0.2 Enriched: Safety and compliance recall campaigns (40 rows) linked to affected_model_id (1..8).",
          "columns": {
              "recall_id": "Primary key recall ID (1..40).",
              "campaign_code": "Official recall bulletin code (RC-2023-001..040).",
              "issue_date": "Campaign launch date.",
              "affected_model_id": "Target vehicle model ID (1..8; joins to auto_sales_data.vehicle_models.model_id).",
              "target_component": "Recalled subsystem component.",
              "severity": "Safety severity ('Critical', 'High', 'Medium', 'Low').",
              "estimated_cost_per_vehicle": "Estimated per-VIN recall repair cost (USD).",
          },
      },
  }

  results = []
  for table_id, meta in table_enrichments.items():
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT_ID}/datasets/auto_aftersales_data/tables/{table_id}"
    st_g, tbl = api_call("GET", url, token)
    if st_g != 200:
      results.append({"table": table_id, "status": st_g})
      continue
    fields = tbl.get("schema", {}).get("fields", [])
    for f in fields:
      if f["name"] in meta["columns"]:
        f["description"] = meta["columns"][f["name"]]
    st_p, _ = api_call(
        "PATCH",
        url,
        token,
        {"description": meta["description"], "schema": {"fields": fields}},
    )
    results.append({"table": table_id, "status": st_p, "columns_enriched": len(fields)})
    print(f"  Enriched BigQuery table auto_aftersales_data.{table_id} -> status={st_p} ({len(fields)} cols)")
  return results


def run_before_after_benchmarks(token: str) -> dict:
  """Executes the Before-vs-After OKF SQL queries against sa-demo-agentic BigQuery."""
  benchmarks = {}

  # Benchmark 1: Warranty Cost & Supplier Recovery
  benchmarks["trap1_warranty_burden"] = run_bq_query(
      token,
      """
      WITH parts_by_order AS (
        SELECT
          service_order_id,
          LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned
        FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage`
        GROUP BY service_order_id
      ),
      fanout_join AS (
        SELECT ROUND(SUM(w.claim_amount), 2) AS naive_fanout_approved_sum
        FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
        JOIN `sa-demo-agentic.auto_aftersales_data.service_parts_usage` spu
          ON w.service_order_id = spu.service_order_id
        WHERE w.claim_status = 'Approved'
      )
      SELECT
        ROUND(SUM(w.claim_amount), 2) AS before_okf_gross_unfiltered_sum,
        (SELECT naive_fanout_approved_sum FROM fanout_join) AS before_okf_naive_parts_join_sum,
        ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS after_okf_realized_warranty_cost,
        ROUND(SUM(CASE WHEN w.claim_status IN ('Pending', 'Under Review') THEN w.claim_amount ELSE 0 END), 2) AS after_okf_open_reserve_exposure,
        ROUND(SUM(CASE WHEN w.claim_status = 'Denied' THEN w.claim_amount ELSE 0 END), 2) AS after_okf_denied_excluded,
        ROUND(SUM(CASE
          WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
          THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS after_okf_recoverable_supplier_chargeback,
        ROUND(SUM(CASE
          WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE
          THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS after_okf_unrecovered_supplier_leakage,
        ROUND(
          SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) -
          SUM(CASE
            WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
            THEN w.claim_amount * 0.70 ELSE 0 END),
          2
        ) AS after_okf_net_oem_warranty_burden
      FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
      LEFT JOIN parts_by_order p USING (service_order_id)
      """,
  )[0]

  # Benchmark 2: Dealership Warranty Absorption (service_type vs is_warranty_covered)
  benchmarks["trap2_service_absorption"] = run_bq_query(
      token,
      """
      SELECT
        COUNTIF(service_type = 'Warranty Repair') AS before_okf_warranty_repair_orders,
        ROUND(SUM(CASE WHEN service_type = 'Warranty Repair' THEN total_cost ELSE 0 END), 2) AS before_okf_warranty_repair_cost,
        COUNTIF(is_warranty_covered = TRUE) AS after_okf_total_covered_orders,
        ROUND(SUM(CASE WHEN is_warranty_covered = TRUE THEN total_cost - customer_paid_amount ELSE 0 END), 2) AS after_okf_total_oem_absorbed_cost,
        ROUND(
          SUM(CASE WHEN is_warranty_covered = TRUE THEN total_cost - customer_paid_amount ELSE 0 END) -
          SUM(CASE WHEN service_type = 'Warranty Repair' THEN total_cost ELSE 0 END),
          2
        ) AS missed_goodwill_and_recall_warranty_dollars
      FROM `sa-demo-agentic.auto_aftersales_data.service_orders`
      """,
  )[0]

  # Benchmark 3: Active Fleet Warranty Entitlement
  benchmarks["trap3_fleet_entitlement"] = run_bq_query(
      token,
      """
      SELECT
        COUNTIF(warranty_end_date >= CURRENT_DATE()) AS before_okf_date_only_fleet,
        COUNTIF(ownership_status = 'Active') AS before_okf_active_only_fleet,
        COUNTIF(
          warranty_end_date >= CURRENT_DATE()
          AND (ownership_status = 'Active'
               OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))
        ) AS after_okf_true_entitled_fleet,
        COUNTIF(ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE) AS transferred_with_extended_warranty,
        COUNTIF(ownership_status = 'Transferred' AND extended_warranty_purchased = FALSE) AS transferred_unentitled_excluded,
        COUNTIF(ownership_status = 'Buyback') AS buyback_excluded
      FROM `sa-demo-agentic.auto_aftersales_data.vehicle_ownership`
      """,
  )[0]

  # Benchmark 4: Dimension Catalog Padding (259 rows vs 7 active plants)
  benchmarks["trap4_dimension_padding"] = run_bq_query(
      token,
      """
      WITH active_plants AS (
        SELECT DISTINCT p.plant_id, p.plant_name, p.capacity
        FROM `sa-demo-agentic.auto_manufacturing_data.plants` p
        INNER JOIN `sa-demo-agentic.auto_manufacturing_data.assembly_line_status` als
          ON p.plant_name = als.plant_name
      )
      SELECT
        (SELECT COUNT(*) FROM `sa-demo-agentic.auto_manufacturing_data.plants`) AS before_okf_raw_plant_rows,
        (SELECT SUM(capacity) FROM `sa-demo-agentic.auto_manufacturing_data.plants`) AS before_okf_padded_capacity_sum,
        COUNT(*) AS after_okf_active_plant_count,
        SUM(capacity) AS after_okf_active_capacity_sum
      FROM active_plants
      """,
  )[0]

  return benchmarks


def main():
  token = get_token()
  manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

  print("=== 1. Ensuring Business Glossary & Canonical Terms in sa-demo-agentic ===")
  term_entries = ensure_glossary_and_terms(token)

  print("\n=== 2. Ensuring Context Set EntryGroup & Publishing OKF v0.2 Entries/Links ===")
  context_set_eg = ensure_entry_group(token, "auto-enterprise-okf-context-set")
  enrichment_eg = f"projects/{PROJECT_ID}/locations/{LOCATION}/entryGroups/enrichment-entry-group"

  pub_context_set = publish_bundle_to_entry_group(token, context_set_eg, manifest, term_entries)
  pub_enrichment = publish_bundle_to_entry_group(token, enrichment_eg, manifest, term_entries)

  print("\n=== 3. Enriching BigQuery Native Table & Column Descriptions (auto_aftersales_data) ===")
  bq_enrichment = enrich_bigquery_table_schemas(token)

  print("\n=== 4. Running Live Verification & Before/After SQL Benchmarks ===")
  _, list_cs = api_call(
      "GET",
      f"https://dataplex.googleapis.com/v1/{context_set_eg}/entries?pageSize=100",
      token,
  )
  _, list_enr = api_call(
      "GET",
      f"https://dataplex.googleapis.com/v1/{enrichment_eg}/entries?pageSize=100",
      token,
  )
  benchmarks = run_before_after_benchmarks(token)

  report = {
      "timestamp": TIMESTAMP,
      "project_id": PROJECT_ID,
      "location": LOCATION,
      "glossary": f"projects/{PROJECT_ID}/locations/global/glossaries/{GLOSSARY_ID}",
      "glossary_terms_count": len(term_entries),
      "context_set_entry_group": context_set_eg,
      "context_set_live_entries_count": len(list_cs.get("entries", [])),
      "enrichment_entry_group": enrichment_eg,
      "enrichment_live_entries_count": len(list_enr.get("entries", [])),
      "links_published_per_group": len(pub_context_set["links"]),
      "bigquery_tables_enriched": bq_enrichment,
      "benchmarks": benchmarks,
  }
  out_path = BASE_DIR / "bundle" / "live_verification_report.json"
  out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
  print("\n=== LIVE VERIFICATION SUMMARY ===")
  print(json.dumps(report, indent=2))


if __name__ == "__main__":
  main()
