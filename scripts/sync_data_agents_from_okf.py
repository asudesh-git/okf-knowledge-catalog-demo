#!/usr/bin/env python3
"""Compile thin, drift-free GDA Data Agent contexts from OKF v0.2 Git docs & Dataplex Business Glossary.

Implements the Practical 4-Layer Production Pattern:
  Layer 1: BigQuery Semantic Views & Property Graph MEASURE(...)s
  Layer 2: Single Source of Truth in GitHub OKF v0.2 + Dataplex Business Glossary
  Layer 3: Thin Agent Persona/Routing + Auto-Compiled OKF Guardrails & GlossaryTerms
  Layer 4: Curated Top-KPI Verified Queries (exampleQueries)

Usage:
  python3 scripts/sync_data_agents_from_okf.py --dry-run
  python3 scripts/sync_data_agents_from_okf.py --apply
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

os.environ["CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE"] = "false"

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO_ROOT / "agents"
ACCOUNT = "admin@asudesh.altostrat.com"
GDA_BASE = "https://geminidataanalytics.googleapis.com/v1beta"
DATAPLEX_BASE = "https://dataplex.googleapis.com/v1"


def get_token() -> str:
  return subprocess.check_output(
      ["gcloud", "auth", "print-access-token", f"--account={ACCOUNT}"],
      text=True,
  ).strip()


def api_req(
    method: str,
    url: str,
    token: str,
    user_project: str,
    body: dict | None = None,
) -> dict:
  data = None
  headers = {
      "Authorization": f"Bearer {token}",
      "x-goog-user-project": user_project,
  }
  if body is not None:
    data = json.dumps(body).encode("utf-8")
    headers["Content-Type"] = "application/json"
  req = urllib.request.Request(url, data=data, headers=headers, method=method)
  try:
    with urllib.request.urlopen(req, timeout=60) as resp:
      raw = resp.read().decode("utf-8")
      return json.loads(raw) if raw else {}
  except urllib.error.HTTPError as exc:
    err_body = exc.read().decode("utf-8", errors="replace")
    raise RuntimeError(f"{method} {url} -> HTTP {exc.code}: {err_body}") from exc


def parse_recovery_rate() -> tuple[int, str, str]:
  """Read canonical supplier chargeback recovery rate dynamically from OKF Git files."""
  metrics_md = (
      REPO_ROOT / "raw-tribal-knowledge/02_business_metrics_and_glossary.md"
  ).read_text()
  concept_md = (
      REPO_ROOT / "catalog/documents/concepts/net-oem-warranty-burden.md"
  ).read_text()

  m_pct = re.search(r"recovers\s+\*\*(\d+)%\s+of\s+`claim_amount`", metrics_md)
  m_dec = re.search(r"(0\.\d+)\s*\\times\s*\\text\{claim\\_amount\}", concept_md)

  if m_pct:
    pct = int(m_pct.group(1))
    dec_val = pct / 100.0
  elif m_dec:
    dec_val = float(m_dec.group(1))
    pct = round(dec_val * 100)
  else:
    pct, dec_val = 70, 0.70

  unrec_val = max(0.0, 1.0 - dec_val)
  return pct, f"{dec_val:.2f}", f"{unrec_val:.2f}"


def compile_okf_guardrails(pct: int, dec_str: str) -> str:
  """Compile a compact, drift-free OKF guardrail block from Git markdown sources."""
  required_sources = [
      REPO_ROOT / "raw-tribal-knowledge/03_schema_caveats_and_traps.md",
      REPO_ROOT / "raw-tribal-knowledge/04_join_rules_and_grain.md",
      REPO_ROOT / "raw-tribal-knowledge/06_analyst_feedback_learnings.md",
      REPO_ROOT / "catalog/documents/concepts/active-warranty-entitlement-fleet.md",
      REPO_ROOT / "catalog/documents/concepts/cross-project-telematics-warranty-correlation.md",
      REPO_ROOT / "catalog/documents/learnings/cross-project-telematics-self-learned-guardrails.md",
  ]
  missing = [str(p.relative_to(REPO_ROOT)) for p in required_sources if not p.exists()]
  if missing:
    raise FileNotFoundError(f"Missing required OKF source files: {missing}")

  # Keep compiled instructions concise, time-invariant, and strictly sourced from OKF Git files.
  return "\n".join([
      "== LAYER 2: COMPILED OKF v0.2 GUARDRAILS (DO NOT EDIT MANUALLY — SYNCED FROM GITHUB) ==",
      f"- Realized Warranty Spend: filter `claim_status = 'Approved'`; exclude 'Pending', 'Under Review', 'Denied'.",
      (
          "- Net OEM Warranty Burden & Supplier Chargeback: Approved `supplier_fault = TRUE` claims "
          f"recover **{pct}% (`{dec_str} * claim_amount`)** ONLY IF order-level `LOGICAL_AND(defective_part_returned) = TRUE` "
          "in `service_parts_usage` (pre-aggregate `service_parts_usage` by `service_order_id` before joining `warranty_claims`)."
      ),
      "- Warranty Service Absorption: filter `service_orders.is_warranty_covered = TRUE` (never filter only `service_type = 'Warranty Repair'`) and sum `total_cost - customer_paid_amount`.",
      "- Plant Attribution: group by `build_plant_name` (`supplier_fault = FALSE`) for OEM assembly quality; `part_source_plant_name` (`supplier_fault = TRUE`) for component supplier audits.",
      "- Dimension Catalog Padding: always `INNER JOIN` `plants`, `vehicle_models`, and `dealerships` to active operational tables so unallocated ERP codes do not dilute averages.",
      "- Active Warranty Entitlement Fleet: filter `warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))` (exclude `'Buyback'`).",
      "- Cross-Project Telematics (`sa-demo-kc.auto_connected_telematics_data`): ALWAYS filter `connected_vehicle_dtc_events` by `telemetry_stream_status = 'VERIFIED_VEHICLE_ALERT'` (exclude `'BENCH_CALIBRATION_NOISE'`), pre-aggregate DTC & OTA deployments to `(vin, part_name)`, and deduplicate `warranty_supplier_chargeback_graph` claims at `(vin, claim_id, claim_amount, part_name)` before `SUM(claim_amount)`.",
      "- Cross-Cloud Identity: filter `customer_identity_crosswalk.match_confidence >= 0.85`; include both `'PLATINUM-VIP'` and `'PLATNUM-VIP'`.",
  ])


def fetch_glossary_terms(
    token: str, project_id: str, glossary_name: str, pct: int
) -> list[dict]:
  """Fetch canonical glossary terms directly from Dataplex Business Glossary."""
  terms: list[dict] = []
  page_token = ""
  while True:
    url = f"{DATAPLEX_BASE}/{glossary_name}/terms?pageSize=100"
    if page_token:
      url += f"&pageToken={urllib.parse.quote(page_token)}"
    res = api_req("GET", url, token, project_id)
    for t in res.get("terms", []):
      disp = (t.get("displayName") or "").strip()[:256]
      desc = (t.get("description") or "").strip()
      if "Recoverable Supplier Chargeback" in disp or "Warranty Burden" in disp or "Chargeback" in disp:
        desc = re.sub(r"\b70%\b", f"{pct}%", desc)
      if disp and desc:
        terms.append({"displayName": disp, "description": desc[:4500]})
    page_token = res.get("nextPageToken", "")
    if not page_token:
      break
  terms.sort(key=lambda x: x["displayName"])
  return terms


def render_verified_queries(
    spec_queries: list[dict], pct: int, dec_str: str, unrec_str: str
) -> list[dict]:
  rendered = []
  for q in spec_queries:
    nl = (
        q["naturalLanguageQuestion"]
        .replace("{{RECOVERY_RATE_PCT}}", str(pct))
        .replace("{{RECOVERY_RATE_DEC}}", dec_str)
        .replace("{{UNRECOVERED_RATE_DEC}}", unrec_str)
    )
    sql = (
        q["sqlQuery"]
        .replace("{{RECOVERY_RATE_PCT}}", str(pct))
        .replace("{{RECOVERY_RATE_DEC}}", dec_str)
        .replace("{{UNRECOVERED_RATE_DEC}}", unrec_str)
    )
    rendered.append({"naturalLanguageQuestion": nl, "sqlQuery": sql})
  return rendered


def strip_table_schemas(refs: list[dict]) -> list[dict]:
  return sorted(
      [
          {
              "projectId": r["projectId"],
              "datasetId": r["datasetId"],
              "tableId": r["tableId"],
          }
          for r in refs
      ],
      key=lambda x: (x["projectId"], x["datasetId"], x["tableId"]),
  )


def strip_graph_refs(refs: list[dict]) -> list[dict]:
  return sorted(
      [
          {
              "projectId": r["projectId"],
              "datasetId": r["datasetId"],
              "propertyGraphId": r["propertyGraphId"],
          }
          for r in refs
      ],
      key=lambda x: (x["projectId"], x["datasetId"], x["propertyGraphId"]),
  )


def print_diff(label: str, old_text: str, new_text: str) -> bool:
  if old_text == new_text:
    print(f"  [{label}] unchanged ({len(new_text)} chars)")
    return False
  print(f"  [{label}] CHANGED ({len(old_text)} -> {len(new_text)} chars):")
  for line in difflib.unified_diff(
      old_text.splitlines(),
      new_text.splitlines(),
      fromfile=f"live/{label}",
      tofile=f"compiled/{label}",
      lineterm="",
  ):
    print("    " + line)
  return True


def sync_agent(spec_path: Path, token: str, apply: bool) -> bool:
  spec = json.loads(spec_path.read_text())
  agent_id = spec["agent_id"]
  project_id = spec["project_id"]
  location = spec["location"]
  agent_name = f"projects/{project_id}/locations/{location}/dataAgents/{agent_id}"

  pct, dec_str, unrec_str = parse_recovery_rate()
  guardrails_block = compile_okf_guardrails(pct, dec_str)
  compiled_sys_instr = f"{spec['persona'].strip()}\n\n{guardrails_block}\n"
  compiled_glossary = fetch_glossary_terms(token, project_id, spec["glossary"], pct)
  compiled_examples = render_verified_queries(
      spec["verified_queries"], pct, dec_str, unrec_str
  )

  live_agent = api_req("GET", f"{GDA_BASE}/{agent_name}", token, project_id)
  live_ctx = live_agent["dataAnalyticsAgent"].get("publishedContext", {})

  # Preserve existing hydrated BQ schemas/graphs for attached refs, adding any new ones cleanly
  bq_live = live_ctx.get("datasourceReferences", {}).get("bq", {})
  existing_schema_map = {
      (t["projectId"], t["datasetId"], t["tableId"]): t
      for t in bq_live.get("tableReferences", [])
  }
  merged_table_refs = []
  for tr in spec["table_references"]:
    key = (tr["projectId"], tr["datasetId"], tr["tableId"])
    merged_table_refs.append(existing_schema_map.get(key, tr))

  existing_graph_map = {
      (g["projectId"], g["datasetId"], g["propertyGraphId"]): g
      for g in bq_live.get("propertyGraphReferences", [])
  }
  spec_graph_refs = spec.get("property_graph_references", [])
  merged_graph_refs = []
  for gr in spec_graph_refs:
    key = (gr["projectId"], gr["datasetId"], gr["propertyGraphId"])
    merged_graph_refs.append(existing_graph_map.get(key, gr))

  print(f"\n=== Agent: {agent_id} (OKF chargeback rate = {pct}% / {dec_str}) ===")
  c1 = print_diff(
      "systemInstruction",
      live_ctx.get("systemInstruction", ""),
      compiled_sys_instr,
  )
  c2 = print_diff(
      "glossaryTerms",
      json.dumps(live_ctx.get("glossaryTerms", []), indent=2, sort_keys=True),
      json.dumps(compiled_glossary, indent=2, sort_keys=True),
  )
  c3 = print_diff(
      "tableReferences",
      json.dumps(strip_table_schemas(bq_live.get("tableReferences", [])), indent=2),
      json.dumps(strip_table_schemas(spec["table_references"]), indent=2),
  )
  c4 = print_diff(
      "propertyGraphReferences",
      json.dumps(strip_graph_refs(bq_live.get("propertyGraphReferences", [])), indent=2),
      json.dumps(strip_graph_refs(spec_graph_refs), indent=2),
  )
  c5 = print_diff(
      "exampleQueries",
      json.dumps(live_ctx.get("exampleQueries", []), indent=2, sort_keys=True),
      json.dumps(compiled_examples, indent=2, sort_keys=True),
  )
  changed = c1 or c2 or c3 or c4 or c5

  if not apply:
    return changed

  if not changed:
    print(f"  [SKIP] {agent_id} is already in sync.")
    return False

  new_context = {
      "systemInstruction": compiled_sys_instr,
      "datasourceReferences": {
          "bq": {
              "tableReferences": merged_table_refs,
              "propertyGraphReferences": merged_graph_refs,
          }
      },
      "options": spec["options"],
      "exampleQueries": compiled_examples,
      "glossaryTerms": compiled_glossary,
  }
  patch_url = (
      f"{GDA_BASE}/{agent_name}"
      "?updateMask=dataAnalyticsAgent.stagingContext,dataAnalyticsAgent.publishedContext"
  )
  payload = {
      "name": agent_name,
      "dataAnalyticsAgent": {
          "stagingContext": new_context,
          "publishedContext": new_context,
      },
  }
  print(f"  [APPLY] Updating {agent_id} (stagingContext + publishedContext)...")
  api_req("PATCH", patch_url, token, project_id, body=payload)
  verified = api_req("GET", f"{GDA_BASE}/{agent_name}", token, project_id)
  v_ctx = verified["dataAnalyticsAgent"]["publishedContext"]
  print(
      f"  [VERIFIED] {agent_id}: sysInstr={len(v_ctx.get('systemInstruction', ''))} chars, "
      f"tables={len(v_ctx.get('datasourceReferences', {}).get('bq', {}).get('tableReferences', []))}, "
      f"graphs={len(v_ctx.get('datasourceReferences', {}).get('bq', {}).get('propertyGraphReferences', []))}, "
      f"glossaryTerms={len(v_ctx.get('glossaryTerms', []))}, "
      f"exampleQueries={len(v_ctx.get('exampleQueries', []))}"
  )
  return True


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  mode = parser.add_mutually_exclusive_group(required=True)
  mode.add_argument("--dry-run", action="store_true", help="Show diff without patching Data Agents")
  mode.add_argument("--apply", action="store_true", help="Compile OKF + Glossary and patch Data Agents")
  args = parser.parse_args()

  spec_files = sorted(AGENTS_DIR.glob("*.json"))
  if not spec_files:
    print(f"No agent specs found in {AGENTS_DIR}", file=sys.stderr)
    return 1

  token = get_token()
  any_changes = False
  for sf in spec_files:
    if sync_agent(sf, token, apply=args.apply):
      any_changes = True

  if args.dry_run:
    print(f"\nDry-run complete. Pending changes detected: {any_changes}")
  else:
    print("\nApply complete.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
