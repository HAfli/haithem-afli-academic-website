# Automation Overview

All automation is **transparent, modular, reviewable, and grounded in verified data**. No automation publishes externally or modifies verified records without explicit human approval.

## GitHub Actions workflows

| Workflow | Trigger | What it does | Writes / merges? |
|---|---|---|---|
| `deploy.yml` | push to `main`, manual | Build → test → deploy public site to Pages | Deploys site only. Least-privilege: `contents:read`, `pages:write`, `id-token:write`. |
| `research-intelligence.yml` | weekly (Mon 06:00 UTC), manual | Build + public API → generate intelligence drafts → test → upload artifact → open review PR | **PR only.** Never merges. `contents:write` + `pull-requests:write` scoped to the draft branch. |
| `monitor.yml` | weekly (Mon 07:00 UTC), manual | Source monitor → proposes bibliographic data updates via PR | **PR only.** Never merges. |
| `admin-sync.yml` | scheduled/manual | Feeds/calendars/communication drafts refresh | Draft artefacts; review-gated. |
| `generate-newsletter.yml` | scheduled/manual | Newsletter draft assembly | Draft only. |
| `sync-deadlines.yml` | scheduled/manual | Conference/funding deadline refresh | PR only. |

## Governance rules (apply to every workflow)

1. **Drafts by default.** Generated content lands in `reports/` or as a PR, labelled `needs-review`.
2. **Verified records are read-only** to automation. Only humans edit `data/publications.json`, `projects.json`, `profile.json`, etc.
3. **No external posting** (email, social, press) without explicit human approval per `docs/social-media-policy.md` and `docs/editorial-policy.md`.
4. **Official sources only**, respecting robots/terms/rate-limits (`docs/source-policy.md`).
5. **Secrets live in GitHub Secrets**, never the repo. Absent secrets → graceful no-op, never fabricated data.
6. **Independent of the public build.** Intelligence jobs never block or slow `deploy.yml` (see `docs/performance.md`).

## Local / on-demand commands

```bash
python3 scripts/build.py --verbose      # build public site + public API + knowledge index
python3 scripts/research_os.py --all     # all intelligence drafts + API
python3 scripts/research_os.py --dashboard --analytics   # a subset
python3 scripts/monitor.py --propose     # dry-run source monitor
python3 scripts/admin_sync.py --help     # feeds, calendars, communication drafts, CV
python3 tests/test_site.py               # full test suite
```

## Adding a new automation

1. Write a generator that **reads verified data and writes to `reports/`** (never to `data/`).
2. Add it as a `--flag` in `scripts/research_os.py::TASKS` (or a new script).
3. If it should run in CI, add a step to `research-intelligence.yml` — as a PR/artifact, never a direct merge.
4. Add a test if it produces public output. Document it here and in `docs/developer-guide.md`.
