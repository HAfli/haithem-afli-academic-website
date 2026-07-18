#!/usr/bin/env python3
"""Academic source monitor (skeleton, safe by default).
Reads data/sources.json, checks each Tier 1-2 source for new records, and writes
PROPOSED changes to data/*.json for human review via pull request. It never publishes
directly and never writes to unverified/withheld fields.

This is a governance-first skeleton: the network-fetching functions are defined with
clear contracts but are conservative — without network access in CI they no-op and
report, rather than inventing data. Wire real fetchers (ORCID/Crossref/OpenAlex/
Anthology public APIs) where CI network policy allows.

Usage: python3 scripts/monitor.py --propose
"""
import json, pathlib, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOG = ROOT / "docs" / "provenance-log.md"

def load(n): return json.load(open(DATA/n, encoding="utf-8"))

def check_sources():
    sources = load("sources.json")["sources"]
    active = [s for s in sources if s.get("access","").startswith(("public"))]
    return active

def propose():
    """Contract for each source fetcher:
    - fetch only public metadata (respect robots/rate limits/terms);
    - resolve identity via ORCID/DBLP/Anthology linkage, never name-similarity alone;
    - emit CANDIDATE records with source + retrieval date + confidence;
    - high-confidence structured metadata (new DOI/Anthology id) -> data update;
    - anything touching funding/role/bio/contact -> flag for explicit human approval, never auto-fill.
    """
    active = check_sources()
    stamp = datetime.date.today().isoformat()
    report = [f"# Source monitor run {stamp}", "",
              f"Checked {len(active)} public sources. No network fetch performed in this "
              "environment; when enabled, candidates are written here and to data/*.json as "
              "proposals only.", "",
              "Sources in scope this run:"]
    for s in active:
        report.append(f"- {s['name']} (tier {s['tier']}, {s['frequency']})")
    report += ["", "Governance: automations never write the epistemic/withheld fields; "
               "funding, role, biography and contact changes require explicit human approval "
               "(docs/editorial-policy.md)."]
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("\n\n" + "\n".join(report) + "\n")
    print("\n".join(report))

if __name__ == "__main__":
    if "--propose" in sys.argv:
        propose()
    else:
        print("usage: monitor.py --propose")
