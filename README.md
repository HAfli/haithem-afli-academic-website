# Dr Haithem Afli — Academic Website

Verified academic and professional research profile of Dr Haithem Afli (Lecturer & Principal Investigator in AI and Human-Centred Computing, Munster Technological University). Part of the HAI ResearchOS academic-presence subsystem.

## What this is
A dependency-free static website generated from structured, source-verified JSON data. Every material claim is traceable to a source recorded in `data/sources.json`. Content optimises for academic credibility, factual accuracy and privacy — not attention.

## Build
```bash
python3 scripts/build.py          # generate site/ from data/ + content/
python3 scripts/build.py --check  # validate data schemas only
python3 tests/test_site.py        # links, accessibility, privacy, JSON-LD, data integrity
```
No dependencies beyond Python 3 standard library. Output in `site/` is generated — never hand-edit it.

## Structure
- `data/` — structured records (publications, supervision, projects, news, profile, sources). Source of truth.
- `scripts/build.py` — the generator (content/templates separated, HTML escaped, URLs validated, fails safe).
- `scripts/monitor.py` — weekly source monitor (proposes updates via PR; never publishes directly).
- `tests/` — post-build validation.
- `docs/` — architecture, editorial, source, privacy, image, security, accessibility, maintenance, deployment, rollback policies + provenance log.
- `.github/workflows/` — `deploy.yml` (build+test+Pages), `monitor.yml` (weekly source PR).

## Deployment
GitHub Pages via `deploy.yml` on push to `main`. See `docs/deployment.md` and `docs/rollback.md`.

## Governance
Updates follow confidence-based governance (`docs/editorial-policy.md`): high-confidence structured metadata may auto-merge after tests; funding/role/biography/contact/photograph changes require explicit human approval. Full audit trail in git history and `docs/provenance-log.md`.

## Status
Built and tested locally; **not yet deployed** (awaiting GitHub repository access). Several funding claims are withheld from public display pending official confirmation (see `docs/verification-queue.md`).
