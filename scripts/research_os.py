#!/usr/bin/env python3
"""
Research Intelligence Ecosystem — the operational engine for the Human-Centred AI Research Group.

Turns the website's verified data into an active research operating system: internal dashboards,
publication pipeline, research analytics, extended knowledge-gap detection, NotebookLM source packs,
draft research digests, strategic-planning drafts, and a clean read-only public API layer.

GOVERNING RULES (enforced in code, not just documented):
  * Never fabricates. Every figure is computed from verified data/*.json; missing data is reported
    as missing, never invented.
  * Never auto-publishes externally. Reports are DRAFTS in reports/ (private, review-gated).
  * Never modifies verified records. This engine only reads data/ and writes reports/ + site/api/.
  * Private dashboards (student, grant) emit AGGREGATES / non-sensitive fields only.
  * Public API (site/api/) contains only already-public, aggregate-safe data.

Stdlib only. Safe to run offline. Usage:
    python3 scripts/research_os.py --all
    python3 scripts/research_os.py --dashboard --analytics --api
    python3 scripts/research_os.py --monitor      # draft monitoring report (uses official adapters if reachable)
"""
import argparse, json, pathlib, datetime, re, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
REPORTS = ROOT / "reports"
API = SITE / "api"
TODAY = datetime.date.today().isoformat()

AFLI = {"haithem afli", "h. afli", "afli, haithem", "haithem  afli"}

def load(name, default=None):
    p = DATA / name
    if not p.exists(): return default if default is not None else {}
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default if default is not None else {}

def write_report(relpath, text):
    p = REPORTS / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p

def write_api(name, obj):
    API.mkdir(parents=True, exist_ok=True)
    (API / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    return API / name

def _pubs(): return load("publications.json", {"publications": []}).get("publications", [])
def _projects(): return load("projects.json", {})
def _themes(): return {t["id"]: t["name"] for t in load("profile.json", {}).get("themes", [])}

def is_afli(name): return name.strip().lower() in AFLI

# ---------------------------------------------------------------- ANALYTICS
def analytics_data():
    pubs = _pubs(); themes = _themes()
    by_year = collections.Counter(p["year"] for p in pubs if p.get("year"))
    by_type = collections.Counter(p.get("type", "unknown") for p in pubs)
    by_theme = collections.Counter()
    for p in pubs:
        for th in p.get("themes", []): by_theme[themes.get(th, th)] += 1
    venue_words = collections.Counter()
    for p in pubs:
        for kw in ("ACL", "EMNLP", "NAACL", "COLING", "LREC", "IWSLT", "Findings", "Workshop", "EACL"):
            if kw.lower() in p.get("venue", "").lower(): venue_words[kw] += 1
    coauthors = collections.Counter()
    for p in pubs:
        for a in p.get("authors", []):
            if not is_afli(a): coauthors[a] += 1
    years = sorted(by_year)
    growth = []
    cum = 0
    for y in years:
        cum += by_year[y]; growth.append({"year": y, "count": by_year[y], "cumulative": cum})
    return {
        "generated": TODAY,
        "total_publications": len(pubs),
        "by_year": [{"year": y, "count": by_year[y]} for y in years],
        "cumulative_growth": growth,
        "by_type": dict(by_type.most_common()),
        "by_theme": dict(by_theme.most_common()),
        "venue_families": dict(venue_words.most_common()),
        "distinct_coauthors": len(coauthors),
        "top_coauthors": [{"name": n, "joint_papers": c} for n, c in coauthors.most_common(15)],
        "with_doi": sum(1 for p in pubs if p.get("doi")),
        "with_url": sum(1 for p in pubs if p.get("url")),
    }

def gen_analytics():
    a = analytics_data()
    lines = [f"# Research Analytics (draft — generated {TODAY})", "",
             "Computed entirely from verified `data/publications.json`. No external or fabricated figures. "
             "Citation/altmetric counts are intentionally omitted until a verified source is connected.", "",
             f"**Publications indexed:** {a['total_publications']} · **distinct co-authors:** {a['distinct_coauthors']} · "
             f"**with DOI:** {a['with_doi']} · **with link:** {a['with_url']}", "",
             "## Publications per year"]
    for r in a["by_year"]:
        bar = "█" * r["count"]
        lines.append(f"- {r['year']}: {bar} {r['count']}")
    lines += ["", "## Cumulative growth"]
    for r in a["cumulative_growth"]:
        lines.append(f"- through {r['year']}: {r['cumulative']}")
    lines += ["", "## By type"] + [f"- {k}: {v}" for k, v in a["by_type"].items()]
    lines += ["", "## By research theme"] + [f"- {k}: {v}" for k, v in a["by_theme"].items()]
    lines += ["", "## Venue families (keyword match)"] + [f"- {k}: {v}" for k, v in a["venue_families"].items()]
    lines += ["", "## Top collaborators (by joint publications on this record)"]
    lines += [f"- {c['name']}: {c['joint_papers']}" for c in a["top_coauthors"]]
    lines += ["", "_Collaboration counts reflect co-authorship in the verified publication list only; "
              "they are not a completeness claim about all collaborations._"]
    write_report("analytics.md", "\n".join(lines))
    return a

# ---------------------------------------------------------------- KNOWLEDGE GAPS (extended)
def gaps_data():
    pubs = _pubs(); profile = load("profile.json", {}); gaps = collections.OrderedDict()
    def miss(field, predicate):
        items = [p["title"] for p in pubs if predicate(p)]
        if items: gaps[field] = items
    miss("missing authoritative link (url)", lambda p: not p.get("url"))
    miss("missing DOI", lambda p: not p.get("doi") and p.get("type") not in ("preprint",))
    miss("missing theme tags", lambda p: not p.get("themes"))
    miss("missing abstract/summary note", lambda p: not p.get("note"))
    miss("missing anthology id (venue looks like *ACL)", lambda p: not p.get("anthology_id")
         and any(k in p.get("venue", "") for k in ("ACL", "EMNLP", "NAACL", "EACL", "Findings", "IWSLT")))
    profile_gaps = []
    if not profile.get("orcid"): profile_gaps.append("profile ORCID")
    return gaps, profile_gaps

def gen_gaps():
    gaps, profile_gaps = gaps_data()
    lines = [f"# Knowledge-gap report (PRIVATE — do not publish) — {TODAY}", "",
             "Coverage diagnostics for the verified records. No invented content — only what is missing, "
             "so records can be improved. Close a gap by adding the field in `data/*.json`, verifying it "
             "against the authoritative source, and rebuilding.", ""]
    if not gaps and not profile_gaps:
        lines.append("No structural gaps detected.")
    for field, items in gaps.items():
        shown = "; ".join(items[:10]) + (" …" if len(items) > 10 else "")
        lines.append(f"## {len(items)} record(s) — {field}\n{shown}\n")
    if profile_gaps:
        lines.append("## Profile-level gaps\n" + ", ".join(profile_gaps))
    write_report("knowledge-gaps.md", "\n".join(lines))
    return gaps

# ---------------------------------------------------------------- PUBLICATION PIPELINE
def gen_pipeline():
    pl = load("pipeline.json", {"stages": [], "papers": []})
    pubs = _pubs()
    stages = pl.get("stages", [])
    active = [p for p in pl.get("papers", []) if not p.get("id", "").startswith("example-")]
    lines = [f"# Publication Pipeline (draft — {TODAY})", "",
             "In-progress papers are human-maintained in `data/pipeline.json`. Published papers are "
             "summarised automatically from the verified record. Nothing here is fabricated.", "",
             f"**In-progress papers tracked:** {len(active)} · **published (verified):** {len(pubs)}", ""]
    if active:
        lines.append("## In progress")
        order = {s: i for i, s in enumerate(stages)}
        for p in sorted(active, key=lambda x: order.get(x.get("stage"), 99)):
            hist = f" · {len(p.get('history', []))} history event(s)" if p.get("history") else ""
            lines.append(f"- **[{p.get('stage','?')}]** {p.get('title','(untitled)')}"
                         + (f" → _{p['venue_target']}_" if p.get("venue_target") else "") + hist)
    else:
        lines.append("_No in-progress papers recorded yet. Add real working papers to `data/pipeline.json` "
                     "(the template entry is ignored)._")
    latest = sorted(pubs, key=lambda x: -x.get("year", 0))[:8]
    lines += ["", "## Recently published (verified)"]
    lines += [f"- {p['year']} · {p['title']} — {p.get('venue','')}" for p in latest]
    write_report("pipeline.md", "\n".join(lines))
    return {"in_progress": len(active), "published": len(pubs)}

# ---------------------------------------------------------------- STUDENT DASHBOARD (private, aggregate)
def gen_students():
    s = load("supervision.json", {})
    doc = s.get("doctoral_completed", []); postdoc = s.get("postdoctoral_completed", [])
    fellows = s.get("fellows_completed", []); interns = s.get("interns_visitors", [])
    masters = s.get("masters", [])
    def first_topic(m):
        t = m.get("topics")
        if isinstance(t, list): return (t[0] if t else "").strip()
        return str(t or "").split(",")[0].strip()
    areas = collections.Counter(first_topic(m) for m in masters if m.get("topics"))
    lines = [f"# Student & Mentoring Dashboard (PRIVATE — aggregate only) — {TODAY}", "",
             "Aggregate view for supervision planning. Master's-level entries are summarised as counts only "
             "(no names) to avoid holding student PII in a public repo. Doctoral/postdoctoral completions "
             "already appear publicly on the site.", "",
             "## Totals",
             f"- Completed doctoral: {len(doc)}",
             f"- Completed postdoctoral: {len(postdoc)}",
             f"- Completed fellows: {len(fellows)}",
             f"- Interns / visitors: {len(interns)}",
             f"- Master's-level supervised (aggregate): {len(masters)}", "",
             "## Master's topics (top areas, counts only)"]
    lines += [f"- {a}: {c}" for a, c in areas.most_common(12)] or ["- (none tagged)"]
    lines += ["", "_To track live PhD milestones/meetings, keep a private file outside this repo and "
              "reference students by initials or id; this dashboard intentionally holds no meeting notes or PII._"]
    write_report("student-dashboard.md", "\n".join(lines))
    return {"doctoral": len(doc), "postdoc": len(postdoc), "masters": len(masters)}

# ---------------------------------------------------------------- GRANT DASHBOARD (private, aggregate)
def gen_grants():
    g = load("grants.json", {"stages": [], "grants": []})
    active = [x for x in g.get("grants", []) if not x.get("id", "").startswith("example-")]
    by_stage = collections.Counter(x.get("stage", "?") for x in active)
    lines = [f"# Grant Dashboard (PRIVATE) — {TODAY}", "",
             "Aggregate grant-pipeline view from `data/grants.json`. Sensitive budgets and unannounced "
             "consortium detail must NOT be committed here — keep them in a private store and reference by id. "
             "Nothing here is published to the public site (test-guarded).", "",
             f"**Grant activities tracked:** {len(active)}", ""]
    if active:
        lines.append("## By stage")
        lines += [f"- {s}: {c}" for s, c in by_stage.most_common()]
        lines += ["", "## Items"]
        for x in active:
            lines.append(f"- **[{x.get('stage','?')}]** {x.get('working_title','(untitled)')}"
                         + (f" — {x['funder']}" if x.get("funder") else "")
                         + (f" · deadline {x['deadline']}" if x.get("deadline") else ""))
    else:
        lines.append("_No grant activity recorded yet. Add entries to `data/grants.json` (template ignored)._")
    write_report("grant-dashboard.md", "\n".join(lines))
    return {"tracked": len(active), "by_stage": dict(by_stage)}

# ---------------------------------------------------------------- FUNDING / CONFERENCE INTELLIGENCE
def _verified_open(items, datefield):
    out = []
    for c in items or []:
        d = c.get(datefield)
        if d and c.get("verification_status", c.get("verified")) in ("verified", True) and str(d) >= TODAY:
            out.append(c)
    return out

def funding_intel():
    f = load("funding_calls.json", {})
    calls = f.get("calls", [])
    open_calls = _verified_open(calls, "deadline")
    return open_calls, calls

def conference_intel():
    c = load("conference_deadlines.json", {})
    editions = c.get("editions", c.get("conferences", []))
    if isinstance(editions, dict): editions = [editions]
    upcoming = []
    for ed in editions or []:
        name = ed.get("edition") or ed.get("name") or ed.get("series", "conference")
        for dl in ed.get("deadlines", []) or []:
            d = dl.get("date")
            if d and str(d)[:10] >= TODAY and dl.get("verification_status", "verified") == "verified":
                upcoming.append((str(d)[:10], name, dl.get("label", dl.get("type", "deadline"))))
    return sorted(upcoming)

# ---------------------------------------------------------------- INTERNAL DASHBOARD
def website_health():
    br = SITE / "build-report.json"
    if br.exists():
        try:
            d = json.load(open(br, encoding="utf-8"))
            pages = d.get("pages")
            npages = len(pages) if isinstance(pages, list) else pages
            return {"pages": npages, "errors": len(d.get("broken_references", d.get("errors", [])) or []),
                    "build_date": d.get("build_date"), "duration_sec": d.get("duration_sec")}
        except Exception: pass
    return {"pages": None, "errors": None, "build_date": None}

def dashboard_data():
    proj = _projects(); pubs = _pubs()
    nat = [p for p in proj.get("national_projects", []) if "WITHHELD" not in p.get("note", "")]
    eu = [p for p in proj.get("eu_projects", []) if "WITHHELD" not in p.get("note", "")]
    open_calls, all_calls = funding_intel()
    upcoming = conference_intel()
    pl = load("pipeline.json", {"papers": []})
    active_pl = [x for x in pl.get("papers", []) if not x.get("id", "").startswith("example-")]
    gaps, _ = gaps_data()
    return {
        "generated": TODAY,
        "projects": {"national": len(nat), "eu": len(eu)},
        "publications": len(pubs),
        "pipeline_in_progress": len(active_pl),
        "funding_open_calls": len(open_calls),
        "next_conference_deadlines": upcoming[:5],
        "gap_categories": len(gaps),
        "website": website_health(),
    }

def gen_dashboard():
    d = dashboard_data()
    a = analytics_data()
    open_calls, _ = funding_intel()
    lines = [f"# Internal Research Dashboard (PRIVATE) — {TODAY}", "",
             "A single-glance operational snapshot built from verified data. Figures are computed, not entered. "
             "This lives in `reports/` (never in the public site).", "",
             "## Portfolio",
             f"- National projects (verified, public): {d['projects']['national']}",
             f"- EU projects (verified, public): {d['projects']['eu']}",
             f"- Publications (verified): {d['publications']}",
             f"- Papers in progress (pipeline): {d['pipeline_in_progress']}",
             f"- Distinct collaborators (co-authorship): {a['distinct_coauthors']}", "",
             "## Opportunities & deadlines",
             f"- Open funding calls (verified, future-dated): {d['funding_open_calls']}"]
    for c in open_calls[:6]:
        lines.append(f"    - {c.get('deadline')} · {c.get('name', c.get('programme','call'))}")
    lines.append("- Next conference deadlines:")
    for dt, name, kind in d["next_conference_deadlines"]:
        lines.append(f"    - {dt} · {name} ({kind})")
    w = d["website"]
    lines += ["", "## Website health",
              f"- Pages: {w.get('pages')} · build errors: {w.get('errors')} · last build: {w.get('build_date')}",
              f"- Knowledge-gap categories open: {d['gap_categories']}", "",
              "## Readiness",
              "- Communication drafts: see `reports/communication-dashboard.md`",
              "- Monitoring drafts: see `reports/monitoring/`",
              "- Publication pipeline: see `reports/pipeline.md`",
              "- Students (aggregate): see `reports/student-dashboard.md`",
              "- Grants (aggregate): see `reports/grant-dashboard.md`"]
    write_report("dashboard.md", "\n".join(lines))
    return d

# ---------------------------------------------------------------- NOTEBOOKLM SOURCE PACKS
def gen_notebooklm():
    pubs = _pubs(); proj = _projects(); themes = _themes()
    profile = load("profile.json", {}); rinn = load("rinn.json", {})
    packs = {}
    pub_lines = ["# NotebookLM source pack — Publications", f"_Generated {TODAY} from verified records._", ""]
    for p in sorted(pubs, key=lambda x: -x.get("year", 0)):
        pub_lines.append(f"## {p['title']} ({p.get('year')})")
        pub_lines.append(f"Authors: {', '.join(p.get('authors', []))}")
        pub_lines.append(f"Venue: {p.get('venue','')}. Type: {p.get('type','')}.")
        if p.get("themes"): pub_lines.append("Themes: " + ", ".join(themes.get(t, t) for t in p["themes"]))
        if p.get("doi"): pub_lines.append(f"DOI: {p['doi']}")
        if p.get("url"): pub_lines.append(f"Link: {p['url']}")
        if p.get("note"): pub_lines.append(p["note"])
        pub_lines.append("")
    packs["publications.md"] = "\n".join(pub_lines)
    proj_lines = ["# NotebookLM source pack — Projects & Funding", f"_Generated {TODAY} from verified records._", ""]
    for grp, label in [("national_projects", "National"), ("eu_projects", "EU"), ("innovation", "Innovation")]:
        for p in proj.get(grp, []):
            if "WITHHELD" in p.get("note", ""): continue
            proj_lines.append(f"## {p.get('short_name') or p.get('name','')} [{label}]")
            proj_lines.append(f"{p.get('name','')}")
            if p.get("funder") or p.get("programme"): proj_lines.append(f"Funder/Programme: {p.get('funder') or p.get('programme')}")
            if p.get("role"): proj_lines.append(f"Role: {p['role']}")
            if p.get("period"): proj_lines.append(f"Period: {p['period']}")
            if p.get("url"): proj_lines.append(f"Link: {p['url']}")
            proj_lines.append("")
    packs["projects.md"] = "\n".join(proj_lines)
    prof_lines = ["# NotebookLM source pack — Profile & Themes", f"_Generated {TODAY}._", "",
                  f"Title: {profile.get('title','')}", f"ORCID: {profile.get('orcid','')}", ""]
    for t in profile.get("themes", []):
        prof_lines.append(f"## Theme: {t.get('name','')}")
        if t.get("summary"): prof_lines.append(t["summary"])
        prof_lines.append("")
    if rinn:
        prof_lines.append("## Rinn Artificial Intelligence")
        prof_lines.append(f"Funder: {rinn.get('funder','')}. "
                          f"National investment: {rinn.get('facts',{}).get('national_investment','')}.")
    packs["profile-themes.md"] = "\n".join(prof_lines)
    manifest = {"generated": TODAY, "packs": list(packs), "note": "Regenerate on new publication/project/theme. "
                "Human review before uploading to NotebookLM. Built from verified records only."}
    for name, text in packs.items():
        write_report(f"notebooklm/{name}", text)
    write_report("notebooklm/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest

# ---------------------------------------------------------------- DRAFT DIGESTS & STRATEGY
def gen_digests():
    a = analytics_data(); d = dashboard_data(); open_calls, _ = funding_intel()
    upcoming = conference_intel()
    latest = sorted(_pubs(), key=lambda x: -x.get("year", 0))[:5]
    lines = [f"# Weekly Research Digest (DRAFT — human review required) — {TODAY}", "",
             "Auto-assembled from verified records and open calls. **Draft only** — verify before sending. "
             "No external claims or fabricated news are included.", "",
             "## Portfolio at a glance",
             f"- {d['publications']} publications · {d['projects']['national']+d['projects']['eu']} funded projects · "
             f"{a['distinct_coauthors']} collaborators · {d['pipeline_in_progress']} papers in progress", "",
             "## Recent publications (verified)"]
    lines += [f"- {p['year']} · {p['title']} — {p.get('venue','')}" for p in latest]
    lines += ["", "## Upcoming deadlines"]
    for dt, name, kind in upcoming[:6]:
        lines.append(f"- {dt} · {name} ({kind})")
    for c in open_calls[:6]:
        lines.append(f"- {c.get('deadline')} · funding: {c.get('name', c.get('programme','call'))}")
    lines += ["", "## Suggested human-authored sections (to complete before sending)",
              "- Group news / milestones this week", "- Student highlights", "- One 'why it matters' paragraph"]
    write_report(f"digests/weekly-{TODAY}.md", "\n".join(lines))
    return {"digest": f"digests/weekly-{TODAY}.md"}

def gen_strategy():
    a = analytics_data(); themes = _themes(); open_calls, _ = funding_intel()
    by_theme = a["by_theme"]
    strong = [k for k, v in by_theme.items() if v >= 3]
    thin = [name for tid, name in themes.items() if by_theme.get(name, 0) < 2]
    call_lines = [f"- {c.get('deadline')} · {c.get('name', c.get('programme','call'))}" for c in open_calls[:8]] \
                 or ["- (no verified open calls dated in the future)"]
    lines = [f"# Strategic Planning (DRAFT — data-driven, human review required) — {TODAY}", "",
             "Observations derived strictly from verified internal data (publication distribution, open calls, "
             "deadlines). Forward-looking judgements are left for you to confirm — this is a scaffold, not a forecast.", "",
             "## Evidenced research strengths (by publication volume)",
             ("- " + ", ".join(strong)) if strong else "- (no theme yet has >=3 indexed publications)", "",
             "## Under-represented themes (publication gaps to consider)",
             ("- " + ", ".join(thin)) if thin else "- (all themes have >=2 publications)", "",
             "## Live funding opportunities to weigh",
             *call_lines,
             "", "## Prompts for the human planner (not auto-answered)",
             "- Which strength should anchor the next flagship grant?",
             "- Which thin theme is strategic vs. peripheral?",
             "- Which collaborators/partners de-risk the next consortium?",
             "", "_No emerging-trend claims are asserted here without external evidence; connect the monitoring "
             "layer (config/monitors.json) to populate an evidenced trend section._"]
    write_report("strategic-plan.md", "\n".join(lines))
    return {"strong": strong, "thin": thin}

# ---------------------------------------------------------------- MONITORING (draft, graceful)
def gen_monitor():
    cfg = json.load(open(ROOT / "config/monitors.json", encoding="utf-8"))
    stamp = TODAY
    fetched = None
    try:
        import importlib.util as il
        spec = il.spec_from_file_location("admin_sync", ROOT / "scripts/admin_sync.py")
        m = il.module_from_spec(spec); spec.loader.exec_module(m)
        results = {}
        for fn in ("adapter_arxiv", "adapter_crossref", "adapter_openalex"):
            if hasattr(m, fn):
                try: results[fn] = len(getattr(m, fn)() or [])
                except Exception as e: results[fn] = f"unreachable ({type(e).__name__})"
        fetched = results
    except Exception as e:
        fetched = f"adapters not loaded ({type(e).__name__})"
    lines = [f"# Research Monitoring run (DRAFT) — {stamp}", "",
             "Modular monitor over official APIs/feeds declared in `config/monitors.json`. Degrades gracefully: "
             "with no network / no API keys it reports 'no data' rather than inventing records. All findings are "
             "DRAFTS for human review; nothing is auto-published and no verified record is modified.", "",
             "## Publication sources"]
    for s in cfg["publication_sources"]:
        lines.append(f"- {s['id']} — {s['api']} (cadence {s['cadence']}"
                     + (f", secret {s['secret']}" if s.get("secret") else "") + ")")
    lines += ["", "## Adapter probe (this run)", f"```\n{json.dumps(fetched, indent=1)}\n```",
              "", "## Funding sources"] + [f"- {s['id']} — {s.get('api') or s.get('feed')}" for s in cfg["funding_sources"]]
    lines += ["", "## Conference sources"] + [f"- {s['id']} — {s.get('feed') or s.get('api')}" for s in cfg["conference_sources"]]
    lines += ["", "## Trend topics watched"] + ["- " + ", ".join(cfg["trend_topics"])]
    lines += ["", "## Governance",
              f"- auto_publish_external: {cfg['governance']['auto_publish_external']}",
              f"- auto_modify_verified_records: {cfg['governance']['auto_modify_verified_records']}",
              "- New candidate records (when online) are written here and, for high-confidence bibliographic "
              "metadata only, proposed via pull request by scripts/monitor.py — never merged automatically."]
    write_report(f"monitoring/run-{stamp}.md", "\n".join(lines))
    return fetched

# ---------------------------------------------------------------- PUBLIC API LAYER
def gen_api():
    """Read-only public API: only already-public, aggregate-safe data. Enables future integrations."""
    pubs = _pubs(); proj = _projects(); themes = _themes()
    open_calls, all_calls = funding_intel()
    # themes.json
    write_api("themes.json", {"generated": TODAY,
        "themes": [{"id": t["id"], "name": t["name"], "summary": t.get("summary", "")}
                   for t in load("profile.json", {}).get("themes", [])]})
    # publications.json (public fields only)
    write_api("publications.json", {"generated": TODAY, "count": len(pubs),
        "publications": [{"title": p["title"], "year": p.get("year"), "venue": p.get("venue"),
                          "type": p.get("type"), "authors": p.get("authors", []),
                          "themes": [themes.get(t, t) for t in p.get("themes", [])],
                          "doi": p.get("doi"), "url": p.get("url")} for p in pubs]})
    # projects.json (public, withheld excluded)
    pj = []
    for grp, kind in [("national_projects", "national"), ("eu_projects", "eu"), ("innovation", "innovation")]:
        for p in proj.get(grp, []):
            if "WITHHELD" in p.get("note", ""): continue
            pj.append({"kind": kind, "name": p.get("short_name") or p.get("name"),
                       "funder": p.get("funder") or p.get("programme"), "role": p.get("role"),
                       "period": p.get("period"), "url": p.get("url")})
    write_api("projects.json", {"generated": TODAY, "count": len(pj), "projects": pj})
    # funding.json (verified open calls only — public)
    write_api("funding.json", {"generated": TODAY,
        "open_calls": [{"name": c.get("name"), "programme": c.get("programme"),
                        "deadline": c.get("deadline"), "url": c.get("url")} for c in open_calls]})
    # analytics.json (public aggregate; no personal data)
    a = analytics_data()
    write_api("analytics.json", {"generated": TODAY, "total_publications": a["total_publications"],
        "by_year": a["by_year"], "by_type": a["by_type"], "by_theme": a["by_theme"],
        "distinct_coauthors": a["distinct_coauthors"]})
    # dashboard.json (public-safe subset only)
    d = dashboard_data()
    write_api("dashboard.json", {"generated": TODAY, "publications": d["publications"],
        "projects": d["projects"], "funding_open_calls": d["funding_open_calls"],
        "website": d["website"]})
    # manifest
    write_api("index.json", {"generated": TODAY, "version": "2.0",
        "endpoints": ["themes.json", "publications.json", "projects.json", "funding.json",
                      "analytics.json", "dashboard.json"],
        "note": "Read-only public aggregates generated from verified data. No personal or private data. "
                "Regenerated on every build."})
    return ["themes.json", "publications.json", "projects.json", "funding.json", "analytics.json", "dashboard.json", "index.json"]

# ---------------------------------------------------------------- CLI
TASKS = {
    "api": gen_api, "analytics": gen_analytics, "gaps": gen_gaps, "pipeline": gen_pipeline,
    "students": gen_students, "grants": gen_grants, "dashboard": gen_dashboard,
    "notebooklm": gen_notebooklm, "digests": gen_digests, "strategy": gen_strategy, "monitor": gen_monitor,
}

def main():
    ap = argparse.ArgumentParser(description="Research Intelligence Ecosystem engine")
    ap.add_argument("--all", action="store_true", help="run every generator")
    for t in TASKS: ap.add_argument(f"--{t}", action="store_true")
    args = ap.parse_args()
    chosen = [t for t in TASKS if getattr(args, t)] or (list(TASKS) if args.all else [])
    if not chosen:
        ap.print_help(); return 1
    REPORTS.mkdir(exist_ok=True)
    for t in chosen:
        TASKS[t](); print(f"  ✓ {t}")
    print(f"Research Intelligence: generated {len(chosen)} artefact set(s) on {TODAY}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
