# Administrator Guide

For the person operating the platform (Dr Afli / group admin). No coding required for routine tasks.

## Routine tasks

**Add or correct a publication / project / role.** Edit the relevant `data/*.json` file, verify against the authoritative source, commit, push. The site, CV PDF, knowledge index, and public API all regenerate on build. Never hand-edit files in `site/`.

**Review the weekly intelligence.** The `Research Intelligence` workflow opens a PR every Monday with refreshed dashboards, analytics, digest and monitoring drafts. Read `reports/dashboard.md` and `reports/digests/weekly-<date>.md`. Merge only what you have verified; drafts are safe to discard.

**Track an in-progress paper.** Add an entry to `data/pipeline.json` (stages listed in the file). It appears in `reports/pipeline.md`. Delete the template entry once you add real ones.

**Track grant activity (private).** Add entries to `data/grants.json`. Keep sensitive budgets/consortium detail out of this repo — reference them by id and hold detail in a private store. Only aggregate counts surface in `reports/grant-dashboard.md`.

**Send a newsletter / communication.** Generated drafts live in `reports/communication/` and `reports/newsletters/`. Review, edit, then send through your approved provider. Nothing sends automatically.

**Publish a research spotlight.** Approve it in `data/communication.json` (`status: "approved"`) — see `docs/research-communication.md`. Only then does the public Spotlight page appear.

## Enabling live monitoring

1. Obtain API keys where required (e.g. Semantic Scholar).
2. Add them as **GitHub Secrets** (repo → Settings → Secrets and variables → Actions). Names are declared in `config/monitors.json` (`secret` field) and referenced in `research-intelligence.yml`.
3. The adapters activate automatically on the next run. Without keys they no-op safely.

## Analytics & subscriptions

Connect a privacy-conscious provider (e.g. Plausible / Cloudflare Web Analytics) and a mailing provider, then populate `data/analytics_summary.json` via `admin_sync.py --analytics`. Only aggregate, country-level data is ever stored (see `docs/privacy-policy.md`). Subscriber emails never enter the repo.

## What you should never do

- Don't edit files under `site/` (they are generated and overwritten).
- Don't commit student PII, private budgets, secrets, or raw analytics logs.
- Don't merge an automation PR without verifying each changed line against its source.
