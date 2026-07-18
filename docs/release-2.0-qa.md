# Release 2.0 — Production-Readiness & QA Report

Scope: the Research Intelligence Ecosystem added in Release 2.0 (engine, dashboards, pipeline, analytics, monitoring framework, public API, automation, docs). Audited against the standing constraints: no fabrication, no external auto-publish, verified records read-only, privacy-preserving, GitHub-Pages-compatible, no redesign of working functionality.

Verdict: **ready to ship.** Build green (29 public pages), full test suite passing, no secrets in the repo, least-privilege deploy, all intelligence output review-gated.

## 1. Functional QA

| Deliverable | Status | Evidence |
|---|---|---|
| Internal dashboard | ✅ | `reports/dashboard.md` — 27 pubs, 8 projects, 48 collaborators, live EMNLP 2026 deadlines, website health 29 pages / 0 errors. |
| Research analytics | ✅ | `reports/analytics.md` + `site/api/analytics.json` from verified pubs (by year/type/theme, co-author network). |
| Publication pipeline | ✅ | `reports/pipeline.md` from `data/pipeline.json` + verified published list. |
| Knowledge-gap detection (extended) | ✅ | `reports/knowledge-gaps.md` — missing url/doi/themes/abstract/anthology-id. |
| Student & grant dashboards (private, aggregate) | ✅ | `reports/student-dashboard.md`, `reports/grant-dashboard.md` — counts only, no PII. |
| NotebookLM source packs | ✅ | `reports/notebooklm/*.md` + manifest, regenerated from verified data. |
| Draft digests + strategic planning | ✅ | `reports/digests/weekly-*.md`, `reports/strategic-plan.md` — data-driven, no invented trends. |
| Monitoring framework | ✅ (framework) | `config/monitors.json` + `reports/monitoring/run-*.md`; official-API adapters degrade gracefully offline. |
| Public API layer | ✅ | `site/api/*.json` (7 endpoints) generated every build; manifest at `index.json`. |
| Automation (CI) | ✅ | `research-intelligence.yml` weekly, PR-only, independent of deploy. |
| Documentation | ✅ | research-intelligence, api, automation, admin-guide, developer-guide, backup-recovery, this report. |

## 2. Truthfulness / no-fabrication audit

- Every figure traces to `data/*.json`; missing data is reported as missing (e.g. 0 verified open funding calls — **not** invented).
- Citation/altmetric counts deliberately excluded until a verified source is connected.
- Trend/strategy layers assert no emerging-trend claim without external evidence; they present verified internal distributions and open prompts for the human planner.
- Verified records are never modified by any generator (engine reads `data/`, writes only `reports/` + `site/api/`).

## 3. Privacy audit

- Public API and public site carry no personal/private data; `tests/test_site.py` fails on any `PRIVATE`/student/grant marker in `site/api/` and on any private report leaking into `site/`.
- Student data held as aggregate counts only; Master's-level names are not committed. Grant sensitive detail kept out of the repo by policy (reference-by-id).
- Analytics remain aggregate, country-level; no raw IPs/logs (`docs/privacy-policy.md`); no tracking scripts (tracker-blocklist test passes).

## 4. Security audit

- **Secrets:** none in the repo (scanned `data/`, `config/`, `scripts/`). API keys via GitHub Secrets only; absent keys → graceful no-op.
- **Workflow permissions:** `deploy.yml` least-privilege (`contents:read`, `pages:write`, `id-token:write`); write-capable workflows (`research-intelligence`, `monitor`, `sync-deadlines`, `admin-sync`, `newsletter`) scoped to `contents:write` + `pull-requests:write` and **open PRs only — never auto-merge**.
- **Dependencies:** core build is **stdlib-only** (no third-party imports); Pillow/reportlab optional and isolated to image/CV steps. Supply-chain surface is minimal.
- **Action pinning (recommendation):** `peter-evans/create-pull-request@v6` is tag-pinned; pin to a commit SHA for production hardening. (Noted inline in the workflows.)
- **External fetches:** official APIs/feeds only, robots/terms respected (`docs/source-policy.md`); no scraping of sources that prohibit automation.

## 5. Performance audit

- Public site is static; total `site/` ≈ 14 MB, dominated by responsive image derivatives (largest ~350 KB `-large` JPEG, with WebP + smaller srcset variants). API payload ≈ 40 KB total.
- Intelligence runs in a **separate** CI job and on demand; it never runs in the Pages deploy path, so automation cannot slow the public site.
- Build is deterministic and fast (single-pass generator; validation inline). No client-side heavy frameworks; the assistant is a small dependency-free script over a static index.

## 6. Compatibility

- 100% GitHub-Pages-compatible: no server, no runtime DB, all outputs static. `.nojekyll` present. API is plain JSON files.
- No redesign: all Release ≤1.3 pages and functionality preserved; Release 2.0 adds files (`scripts/research_os.py`, `data/pipeline.json`, `data/grants.json`, `config/monitors.json`, `site/api/`, docs, one workflow) and wires the API into the existing build without altering the public UI.

## 7. Residual risks & follow-ups

- **Live monitoring is inert without keys/network** (by design). Action: add API-key secrets to activate; then an evidenced trend section becomes available.
- **Action SHA-pinning** recommended before treating CI as fully hardened.
- **Off-Git backups** of `data/` and `assets/source/` originals recommended (`docs/backup-recovery.md`).
- Collaborator/trend *live* intelligence is scaffolded but not populated this release; it plugs into the same framework next batch.

## 8. Sign-off checklist

- [x] `python3 scripts/build.py` — green, 29 pages, 0 broken links/assets.
- [x] `python3 scripts/research_os.py --all` — 11 artefact sets generated.
- [x] `python3 tests/test_site.py` — all checks pass (incl. API + private-leak guards).
- [x] No secrets in repo; least-privilege deploy; automations PR-only.
- [x] No fabricated data; verified records untouched; privacy guards enforced.
