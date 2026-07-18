# Changelog

## [Unreleased] — 2026-07-17
### Added
- Initial website: 14 pages generated from verified structured data.
- Publications database (27 selected/recent records; Anthology-verified entries carry live URLs + BibTeX).
- Supervision dataset: 3 doctoral, 5 postdoctoral, 2 fellows, 7 interns/visitors, 41 Master's projects.
- Projects & funding with total-vs-MTU qualification; unverified national claims withheld pending confirmation.
- JSON-LD (Person), sitemap, Atom feed, robots, Open Graph.
- GitHub Actions: build+test+deploy, weekly source monitor (PR-only).
- Policies: editorial, privacy, source, image, security, accessibility, maintenance, deployment, rollback.
- Test suite: links, accessibility, privacy leaks, JSON-LD, data integrity.
### Verified this release
- IWSLT 2026 paper (Sonawane & Afli, 2026.iwslt-1.6) — ACL Anthology, Tier 1.
- ORCID 0000-0002-7449-4707; ACL Anthology author page; ADAPT/DBLP/Scholar/ACM/OpenReview profiles.
### Pending (not published)
- Funding: GenDAI role title, I3/13 ARC Hub amount meaning, HEA GenAI Lab — awaiting CORDIS/Research Ireland/HEA.
- Canonical MTU staff-profile URL (visibility gap).
- Approved professional photograph.
- ADAPT profile "SIGMA" → "HAI" correction (draft prepared; not yet sent).

## [v2] — 2026-07-17
### Added
- Media gallery page (empty until rights-cleared images exist).
- News page: category + research-theme filters, date sort, original-post + authoritative-source links, image support.
- Labelled profile links (incl. LinkedIn, X) on About and Contact.
- data/social-content.json (LinkedIn/X registry; schema present, zero records — no access/no posts supplied).
- data/gallery.json (media registry; zero images).
- Digital-twin schema: stable ids on publications and news; related_entities graph edges; docs/digital-twin-schema.md + migration plan.
- Policies: social-media-policy.md, deployment-readiness.md; test now blocks social tracking/embed scripts.
### Blocked (stated, not worked around)
- GitHub write access (no connector) → not deployed.
- LinkedIn and X automated access (no connector) → no posts/images imported.
