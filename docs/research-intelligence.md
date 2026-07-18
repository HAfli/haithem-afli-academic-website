# Research Intelligence Ecosystem (Release 2.0)

Release 2.0 turns the website from a passive repository into the **operational digital hub** for the Human-Centred AI Research Group — without redesigning the public site or replacing any working functionality. It adds an intelligence engine that continuously turns the group's *verified* data into dashboards, analytics, pipelines, monitoring drafts, reports, and a clean public API.

## Non-negotiable guarantees (enforced in code)

- **No fabrication.** Every figure is computed from `data/*.json`. Missing data is reported as missing, never invented. Citation/altmetric counts are omitted until a verified source is connected.
- **No external auto-publishing.** All generated reports are DRAFTS in `reports/` (private). External channels require explicit human approval.
- **Verified records are never modified** by automation. The engine reads `data/` and writes only `reports/` and `site/api/`.
- **Private stays private.** Student and grant dashboards emit aggregates / non-sensitive fields only; test-guarded so they never reach the public site.
- **GitHub-Pages-compatible.** The public site remains static. Intelligence runs in CI / on demand, independently of the public build path.

## Components

| Area | Producer | Output (private unless noted) |
|---|---|---|
| Internal dashboard | `research_os.py --dashboard` | `reports/dashboard.md` |
| Research analytics | `--analytics` | `reports/analytics.md` + **public** `site/api/analytics.json` |
| Knowledge-gap detection | `--gaps` | `reports/knowledge-gaps.md` |
| Publication pipeline | `--pipeline` (+ `data/pipeline.json`) | `reports/pipeline.md` |
| Student dashboard (aggregate) | `--students` | `reports/student-dashboard.md` |
| Grant dashboard (aggregate) | `--grants` (+ `data/grants.json`) | `reports/grant-dashboard.md` |
| NotebookLM source packs | `--notebooklm` | `reports/notebooklm/*.md` |
| Draft digests | `--digests` | `reports/digests/weekly-<date>.md` |
| Strategic planning (data-driven) | `--strategy` | `reports/strategic-plan.md` |
| Monitoring run (graceful) | `--monitor` (+ `config/monitors.json`) | `reports/monitoring/run-<date>.md` |
| Public API layer | `--api` (also run every build) | **public** `site/api/*.json` |

Run everything: `python3 scripts/research_os.py --all`. Run a subset: `--dashboard --analytics --api`.

## Monitoring framework

`config/monitors.json` declares what to watch (publication, funding and conference sources; trend topics; collaborators by public identifier) and the governance flags. Adapters use **only official APIs/feeds** and **degrade gracefully**: with no network or no API keys they report "no data fetched" instead of inventing records. High-confidence *bibliographic* candidates (new DOI / Anthology id) may be proposed via pull request by `scripts/monitor.py`; anything touching funding, role, biography or contact requires explicit human approval and is never auto-filled. Secrets (API keys) come from GitHub Secrets, never the repo.

Live coverage today: arXiv, Crossref, OpenAlex adapters already exist in `admin_sync.py` and are probed by the monitor; ORCID, DBLP, Semantic Scholar, OpenReview, CORDIS, Research Ireland, Enterprise Ireland and the EC Funding & Tenders portal are declared and wired for activation when keys/network are available.

## Automation (CI)

`.github/workflows/research-intelligence.yml` runs weekly (and on demand): it builds the site + public API, regenerates all intelligence drafts, runs the tests, uploads everything as a workflow artifact, and opens a **review pull request**. Nothing merges automatically. This is independent of `deploy.yml`, so intelligence work never slows or blocks the public site.

## Data inputs (single source of truth)

Verified, human-owned: `publications.json`, `projects.json`, `profile.json`, `rinn.json`, `supervision.json`, `conference_deadlines.json`, `funding_calls.json`, `sources.json`. Human-maintained pipelines (private): `pipeline.json`, `grants.json`. The engine never writes back to any of these.

## Extending to more groups (future, no redesign)

The engine is data-driven and namespace-agnostic. To serve an additional group/department, point it at a second data directory (or a `group` key) and a second `reports/<group>/` output root; the generators and API layer are unchanged. The public API's `index.json` manifest is the stable integration contract. See `docs/api.md` and `docs/developer-guide.md`.

## Limitations (honest)

- Analytics are limited to what the verified records contain; they are not a completeness claim about all outputs or collaborations.
- Trend analysis asserts **no** emerging-trend claims without external evidence; it becomes evidenced only once the monitoring layer is connected with keys.
- Live monitoring cannot run in a sandbox without network; it is designed for CI with secrets.
