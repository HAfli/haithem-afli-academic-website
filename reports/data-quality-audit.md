# Data Quality Audit — 2026-07-18 (post-enrichment)

Full audit of the research corpus after the publication enrichment pass. Measured against `data/*.json` and the generated `site/`. Build is green (29 pages, 0 broken links/assets); the automated suite (`tests/test_site.py`) passes.

## Summary table

| Check | Result | Detail |
|---|---|---|
| Duplicate publications (title) | **0** | 27 unique titles. |
| Duplicate publication ids | **0** | 27 unique ids. |
| Broken internal links | **0** | Verified by build validator + test suite (incl. subdirectories & `site/api`). |
| Broken/dead external links | Not exhaustively crawled | All publication URLs are official DOI/anthology/arXiv resolvers; spot-verified during enrichment. A periodic link-check is recommended (see below). |
| Publications without a research theme | **0** | Every publication carries ≥1 theme. |
| Publications without a URL | **0** | Was 12; now 0 after enrichment. |
| Publications without a DOI | 16 | 15 ACL Anthology papers (canonical anthology URLs present); 1 CEUR-WS workshop paper (no DOI exists). Reported, not fabricated. |
| Publications without an abstract | 24 | Abstracts added only where the publisher deposited one (3). Others require authoritative full text. |
| Publications without explicit keywords | 27 | Theme tags act as controlled keywords; free-text keywords intentionally empty (no authoritative source). |
| Inconsistent theme tags | **0** | All theme ids resolve to the profile taxonomy (`hcai, multilingual, trustworthy, evaluation, bio, innovation`). |
| Orphan pages (unreachable) | **0** | All 29 pages are reachable from the primary nav and/or breadcrumb trails. |
| Private data leaked to `site/` | **0** | Test-guarded: no `dashboard/student/grant/strategic` reports and no `reports/` dir under `site/`. |
| Withheld/unverified claims public | **0** | Funding-withheld terms test passes; no `verification_pending` wording in output. |
| Email/PII exposure | Only approved address | `Haithem.Afli@mtu.ie` only; no phone/PII patterns. |

## Theme distribution (verified)

multilingual 14 · trustworthy 7 · bio 5 · evaluation 3 · hcai 1 · innovation 0 (theme retained for projects/agenda; no publication currently tagged `innovation`).

Observation: `hcai` (1) and `innovation` (0) are thin at publication level. This is **reported, not corrected by re-tagging** — reassigning papers to inflate a theme would be inaccurate. If any existing paper genuinely belongs to `hcai`/`innovation`, tag it in `data/publications.json`; otherwise the thinness is a true reflection of the indexed corpus.

## Internal linking (added this pass)

- Publication → research theme: 27 publications × theme tags now link to `research.html#<theme>`.
- Publication → collection: every publication shows a "More in this theme" link to `collections.html#<collection>`.
- Research theme → collection: all 5 themed sections link to "Browse N publications in this theme" (counts: multilingual 14, trustworthy 7, bio 5, evaluation 3, hcai 1).
- Publication → sources: DOI/PDF/arXiv/BibTeX links per entry where available.

## Cross-links still worth adding (deferred, need human-verified mappings)

- Publication ↔ project (e.g. NADI-2022 paper ↔ ITFLOWS; gaHealth ↔ ADAPT programmes). Requires explicit `related_projects` ids verified against each project record — deferred to avoid asserting an unverified association.
- Publication ↔ dataset/software (adaptNMT, adaptMLLM, gaHealth, TransCasm all reference open resources) — add authoritative repo/dataset URLs when confirmed.
- Publication ↔ talk/news/media — link where a talk or news item verifiably concerns a specific paper.

## Recommended periodic checks

- **External link health:** run a scheduled link-checker over publication URLs (DOI resolvers rarely rot, but venue/PDF hosts can move).
- **New-output detection:** the monitoring framework (once anonymous sources are enabled) will flag new DOIs/preprints as review drafts.
- **Re-run this audit** after any data edit: `python3 scripts/research_os.py --gaps` refreshes `reports/knowledge-gaps.md`; the build + test suite re-validate links, privacy and structure.

## Verdict

The core research corpus is **complete, de-duplicated, well-linked, and production-ready**: every publication is a resolvable, theme-linked knowledge object with verified provenance. Remaining gaps (16 DOIs by venue design, 24 abstracts, keywords, and per-paper dataset/project links) are **genuine data-availability limits, documented rather than fabricated**, and each has a clear, authoritative path to closure.
