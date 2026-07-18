# Developer Guide

## Architecture in one paragraph

A dependency-free Python static-site generator (`scripts/build.py`) reads `data/*.json` (single source of truth) and emits `site/`. The same build generates the knowledge index (`site/data/`), the client-side Research Assistant (`site/assistant.js`), and the read-only public API (`site/api/`). A separate, independent intelligence engine (`scripts/research_os.py`) reads the same verified data and writes private drafts to `reports/`. CI builds, tests, and deploys the public site; a separate CI job refreshes intelligence as review PRs. Stdlib only (Pillow/reportlab optional for images/CV).

## Repository map

```
data/            verified source of truth (human-owned) + private pipelines (pipeline.json, grants.json)
config/          admin_sync.json, monitors.json
scripts/
  build.py       site + knowledge index + public API + validation + reports
  research_os.py Research Intelligence engine (dashboards, analytics, digests, api, monitor)
  admin_sync.py  feeds, calendars, communication drafts, adapters (arXiv/Crossref/OpenAlex)
  monitor.py     source monitor (proposes bibliographic PRs)
  generate_cv.py CV PDF from canonical data
  process_images.py  image pipeline (EXIF-stripped, responsive derivatives)
site/            GENERATED — never hand-edit (html, style.css, *.js, data/, api/)
reports/         GENERATED private drafts — review-gated, not published
tests/test_site.py  post-build test suite (stdlib)
docs/            policies + guides
.github/workflows/  deploy, research-intelligence, monitor, admin-sync, newsletter, sync-deadlines
```

## Invariants (do not break)

1. `data/` is written only by humans; generators read it and never write back.
2. `site/` and `reports/` are outputs; treat as disposable/regenerable.
3. No fabricated values anywhere — compute from verified data or omit.
4. Public output (`site/`, including `site/api/`) contains no personal/private data.
5. Every public page passes `tests/test_site.py` (links, a11y, privacy, JSON-LD, API, no-private-leak).
6. Stdlib-only for core build; optional deps degrade gracefully.

## Adding an intelligence generator

Add a `gen_x()` in `research_os.py` that reads verified data and calls `write_report(...)` (private) or `write_api(...)` (public, aggregate-safe only), then register it in `TASKS`. If public, add a test. Keep it pure (no writes to `data/`).

## Public API contract

`site/api/index.json` is the manifest (`version`, `endpoints`). Additive changes only within a version; bump `version` for breaking changes. See `docs/api.md`.

## Testing

`python3 scripts/build.py && python3 scripts/research_os.py --all && python3 tests/test_site.py`. The suite covers structure, internal links (incl. subdirs), accessibility, privacy/tracker leaks, JSON-LD validity, the public API, and the private-report-leak guard.
