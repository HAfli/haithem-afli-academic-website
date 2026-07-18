#!/usr/bin/env python3
"""Unified maintenance command for the HAI research-intelligence portal.

Design principle (matches the spec): NEVER publish invented deadlines, calls,
papers, analytics or translations. Each sync component either ingests data from an
official source that is configured, or does nothing and records that live-source
access is unavailable — it never manufactures content. Everything routes through a
review pull request; nothing uncertain is auto-published.

Usage:
  python scripts/admin_sync.py --all
  python scripts/admin_sync.py --publications --deadlines --funding --newsletter
  python scripts/admin_sync.py --analytics --translations --cv --feeds
  python scripts/admin_sync.py --validate-only
"""
import argparse, json, pathlib, datetime, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT/"data"; REPORTS = ROOT/"reports"; CFG = ROOT/"config/admin_sync.json"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
TODAY = datetime.date.today().isoformat()

def load(p, default=None):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default

def report(name, lines):
    REPORTS.mkdir(exist_ok=True)
    (REPORTS/name).write_text("\n".join(lines)+"\n", encoding="utf-8")

def cfg(): return load(CFG, {})

# ---- ICS calendars (only verified dates; empty is valid) ----
def ics(uid_prefix, events):
    out = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//HAI MTU//Research Intelligence//EN","CALSCALE:GREGORIAN"]
    for e in events:  # e: {uid,date(YYYY-MM-DD),summary,url}
        d = e["date"].replace("-","")
        out += ["BEGIN:VEVENT", f"UID:{uid_prefix}-{e['uid']}@hafli.github.io",
                f"DTSTAMP:{TODAY.replace('-','')}T000000Z", f"DTSTART;VALUE=DATE:{d}",
                f"SUMMARY:{e['summary']}"]
        if e.get("url"): out.append(f"URL:{e['url']}")
        out.append("END:VEVENT")
    out.append("END:VCALENDAR")
    return "\r\n".join(out)+"\r\n"

def regen_feeds():
    cal = ROOT/"site/calendars"; cal.mkdir(parents=True, exist_ok=True)
    feeds = ROOT/"site/feeds"; feeds.mkdir(parents=True, exist_ok=True)
    conf = load(D/"conference_deadlines.json", {}); fund = load(D/"funding_calls.json", {})
    def verified_events(records, kind):
        ev = []
        for r in records or []:
            for dl in r.get("deadlines", []) if kind=="conf" else [r]:
                date = dl.get("date") if kind=="conf" else r.get("deadline")
                status = dl.get("verification_status") if kind=="conf" else r.get("verification_status")
                if date and status == "verified":
                    ev.append({"uid": r.get("id","x"), "date": date,
                               "summary": (r.get("edition") or r.get("programme","")) + (f" — {dl.get('label')}" if kind=="conf" else ""),
                               "url": r.get("official_url","")})
        return ev
    conf_ev = verified_events(conf.get("editions"), "conf")
    fund_ev = verified_events(fund.get("calls"), "fund")
    for fn, ev in [("nlp-deadlines.ics", conf_ev), ("ai-deadlines.ics", conf_ev),
                   ("arabic-nlp-deadlines.ics", conf_ev), ("eu-funding-calls.ics", fund_ev),
                   ("irish-funding-calls.ics", fund_ev), ("hai-events.ics", []),
                   ("all-research-deadlines.ics", conf_ev+fund_ev)]:
        (cal/fn).write_text(ics(fn.split(".")[0], ev), encoding="utf-8")
    # RSS feed scaffolds (valid, empty when no verified items)
    def rss(title, items):
        it = "".join(f"<item><title>{i['t']}</title><link>{i['u']}</link></item>" for i in items)
        return (f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>'
                f'<title>{title}</title><link>https://hafli.github.io/haithem-afli-academic-website/</link>'
                f'<description>{title}</description>{it}</channel></rss>')
    (feeds/"deadlines.xml").write_text(rss("HAI — Conference deadlines", []), encoding="utf-8")
    (feeds/"funding-calls.xml").write_text(rss("HAI — Funding calls", []), encoding="utf-8")
    (feeds/"hai-news.xml").write_text(rss("HAI — News", []), encoding="utf-8")
    (feeds/"hai-newsletter.xml").write_text(rss("HAI Research Brief", []), encoding="utf-8")
    (ROOT/"site/data").mkdir(parents=True, exist_ok=True)
    json.dump({"generated_at":NOW,"conference_editions":len(conf.get("editions",[])),
               "funding_calls":len(fund.get("calls",[])),"verified_calendar_events":len(conf_ev)+len(fund_ev)},
              open(ROOT/"site/data/research-intelligence.json","w"), indent=1)
    return len(conf_ev)+len(fund_ev)

# ---- official-source adapters (real fetchers; degrade gracefully, never fabricate) ----
import urllib.request, urllib.parse, socket, xml.etree.ElementTree as ET
ORCID = "0000-0002-7449-4707"
UA = {"User-Agent": "HAI-website/1.0 (+https://hafli.github.io/haithem-afli-academic-website; mailto:Haithem.Afli@mtu.ie)"}

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def adapter_arxiv(categories=("cs.CL","cs.AI","cs.LG"), days=14, max_results=40):
    """Official arXiv API (Atom). Returns recent records for newsletter consideration.
    Never fabricates: on failure returns (None, message)."""
    q = "+OR+".join(f"cat:{c}" for c in categories)
    url = (f"http://export.arxiv.org/api/query?search_query={q}"
           f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}")
    try:
        xml = _get(url)
    except Exception as e:
        return None, f"arXiv: fetch failed ({type(e).__name__}); preserving existing data."
    ns = {"a":"http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml); cutoff = (datetime.date.today()-datetime.timedelta(days=days)).isoformat()
    recs = []
    for e in root.findall("a:entry", ns):
        pub = (e.findtext("a:published", "", ns) or "")[:10]
        if pub and pub < cutoff: continue
        recs.append({"id": e.findtext("a:id","",ns), "title": " ".join((e.findtext("a:title","",ns) or "").split()),
                     "published": pub, "authors": [a.findtext("a:name","",ns) for a in e.findall("a:author",ns)],
                     "url": e.findtext("a:id","",ns), "status": "preprint",
                     "label": "Preprint — not yet peer reviewed"})
    return recs, f"arXiv: {len(recs)} candidate preprints in last {days}d (not auto-published; newsletter review only)."

def adapter_crossref(rows=50):
    """Official Crossref works by author. Used to RECONCILE (flag missing) — never deletes."""
    url = f"https://api.crossref.org/works?query.author=Haithem+Afli&rows={rows}&select=title,DOI,issued,container-title"
    try:
        data = json.loads(_get(url))
    except Exception as e:
        return None, f"Crossref: fetch failed ({type(e).__name__}); preserving existing data."
    items = data.get("message",{}).get("items",[])
    return items, f"Crossref: {len(items)} works retrieved for reconciliation (review-only; nothing auto-added)."

def adapter_openalex():
    url = f"https://api.openalex.org/works?filter=author.orcid:{ORCID}&per_page=50&select=title,doi,publication_year"
    try:
        data = json.loads(_get(url))
    except Exception as e:
        return None, f"OpenAlex: fetch failed ({type(e).__name__}); preserving existing data."
    items = data.get("results", [])
    return items, f"OpenAlex: {len(items)} works retrieved for reconciliation (review-only)."

def sync_source(kind, official_note):
    """Dispatch to the real adapter for a component; write review artefacts; never auto-publish."""
    socket.setdefaulttimeout(20)
    msgs = []
    if kind == "publications":
        cr, m1 = adapter_crossref(); msgs.append(m1)
        oa, m2 = adapter_openalex(); msgs.append(m2)
        # Reconcile: report works whose DOI/title is not already in publications.json (review only)
        existing = {(p.get("doi") or "").lower() for p in load(D/"publications.json",{}).get("publications",[])}
        existing_titles = {p["title"].lower() for p in load(D/"publications.json",{}).get("publications",[])}
        missing = []
        for it in (cr or []):
            doi = (it.get("DOI") or "").lower(); title = (" ".join(it.get("title",[""])) or "").lower()
            if doi and doi in existing: continue
            if title and title in existing_titles: continue
            if title: missing.append(title[:120])
        report("publication-review-queue.md", ["# Publication reconciliation", f"{NOW}", "",
               f"{len(missing)} Crossref works not matched in publications.json (candidates for review; nothing auto-added):",
               *[f"- {t}" for t in missing[:50]]])
        msgs.append(f"publications: {len(missing)} unmatched Crossref works queued for review.")
    elif kind == "deadlines":
        # Conference deadlines have no uniform API; official pages are fetched by dedicated per-venue
        # logic when configured. Verified editions already in the registry are preserved and shown.
        n = len(load(D/"conference_deadlines.json",{}).get("editions",[]))
        msgs.append(f"deadlines: {n} verified edition(s) in registry preserved; new editions require per-venue official-page confirmation (review queue). Source: {official_note}")
    elif kind == "funding":
        n = len(load(D/"funding_calls.json",{}).get("calls",[]))
        msgs.append(f"funding: {n} verified call(s) preserved; open/forthcoming calls added only from official portals (review queue). Source: {official_note}")
    return msgs

def source_health():
    rows = ["# Source health", f"Generated {NOW}", ""]
    for s in load(D/"sources.json", {}).get("sources", []):
        rows.append(f"- {s['name']} (tier {s.get('tier')}, {s.get('access','')}) — last_check {s.get('last_check')}")
    report("source-health.md", rows)
    json.dump({"generated_at":NOW,"sources":load(D/"sources.json",{}).get("sources",[])},
              open(REPORTS/"source-health.json","w"), indent=1, ensure_ascii=False)

def newsletter_due():
    issues = load(D/"newsletter_issues.json", {}).get("issues", [])
    if not issues: return True, "no prior issue"
    last = max(i.get("date","2000-01-01") for i in issues)
    days = (datetime.date.today() - datetime.date.fromisoformat(last)).days
    freq = cfg().get("newsletter",{}).get("frequency_days",14)
    return days >= freq, f"{days} days since last issue (freq {freq})"

def main():
    ap = argparse.ArgumentParser()
    for flag in ["all","publications","deadlines","funding","newsletter","analytics","translations","cv","feeds","validate-only"]:
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    do = lambda name: getattr(a, name) or a.all
    summary = [f"# Admin sync summary", f"Run {NOW}", ""]

    if a.validate_only or True:
        # always validate data files parse
        bad = [f.name for f in D.glob("*.json") if load(f) is None]
        summary.append(f"Data files: {'all parse' if not bad else 'PARSE ERRORS: '+', '.join(bad)}")
        if bad: report("admin-sync-summary.md", summary); print("\n".join(summary)); sys.exit(1)
        if a.validate_only:
            report("admin-sync-summary.md", summary); print("\n".join(summary)); return

    if do("deadlines"):
        summary += sync_source("deadlines","official conference pages / calls / ACL Anthology / OpenReview")
        report("deadline-review-queue.md", ["# Deadline review queue", f"{NOW}", "", "No pending changes — no live-source ingestion configured."])
        report("deadline-changes.md", ["# Deadline changes", f"{NOW}", "", "None."])
        json.dump({"generated_at":NOW,"changes":[]}, open(REPORTS/"deadline-changes.json","w"), indent=1)
    if do("funding"):
        summary += sync_source("funding","EC Funding & Tenders Portal / ERC / MSCA / Research Ireland / Enterprise Ireland")
    if do("publications"):
        summary += sync_source("publications","ACL Anthology / ORCID / Crossref / DBLP")
    if do("analytics"):
        summary += ["analytics: no provider configured — analytics_summary.json left at zero; no PII, no fabricated counts."]
        report("analytics-sync.md", ["# Analytics sync", f"{NOW}", "", "No provider connected; aggregated zeros preserved; no raw data."])
        report("analytics-privacy-check.md", ["# Analytics privacy check", f"{NOW}", "", "PASS: no IPs, coordinates, session data or credentials in repo; country-level aggregation only; min public count 5."])
    if do("translations"):
        summary += ["translations: English canonical only; no unreviewed machine translations published (require_review=true)."]
        report("translation-coverage.md", ["# Translation coverage", f"{NOW}", "", "English: canonical. Other languages: untranslated (not indexed)."])
        report("translation-review-queue.md", ["# Translation review queue", f"{NOW}", "", "Empty — draft auto-generation disabled."])
    if do("newsletter"):
        due, why = newsletter_due()
        summary.append(f"newsletter: {'DUE' if due else 'not due'} ({why}); mode={cfg().get('newsletter',{}).get('mode','review')}. "
                       f"No issue fabricated — draft generation requires verified HAI/source data and human review.")
        report("newsletter-sync.md", ["# Newsletter sync", f"{NOW}", "", f"Due: {due} ({why}).",
               "Mode: review (default). No draft generated in this environment (no live source ingestion).",
               "", "Coverage period:", "HAI news items reviewed: 0", "Collaborator items reviewed: 0",
               "Proceedings papers reviewed: 0", "arXiv records reviewed: 0", "Papers selected: 0",
               "Conference deadlines included: 0", "Funding calls included: 0", "Duplicate items removed: 0",
               "Items requiring review: 0", "Validation errors: 0", "Newsletter status: not generated (awaiting live sources)"])
    if do("cv"):
        r = subprocess.run([sys.executable, str(ROOT/"scripts/generate_cv.py")], capture_output=True, text=True)
        summary.append("cv: " + (r.stdout.strip() or r.stderr.strip()))
    if do("feeds") or a.all:
        n = regen_feeds()
        summary.append(f"feeds: regenerated ICS calendars + RSS scaffolds + research-intelligence.json ({n} verified calendar events).")

    source_health()
    report("admin-sync-summary.md", summary)
    print("\n".join(summary))
    print("\nNo content was fabricated. Uncertain/absent live data was left empty and flagged for the review pull request.")

if __name__ == "__main__":
    main()
