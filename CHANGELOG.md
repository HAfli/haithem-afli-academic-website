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

## [v3] — 2026-07-18
### Added — Rinn Artificial Intelligence
- New page rinn-ai.html (nav: Research area) — programme facts (verified), Dr Afli's involvement, Inclusive Language Model & Translation Methods theme with 6 priority areas, MTU contribution, Rinn/ADAPT/HAI ecosystem.
- Structured Rinn roles in profile.json (not one jobTitle string); JSON-LD now uses hasOccupation[], affiliation[], memberOf[].
- Home: current-roles hero + "New national research leadership" feature card + positioning statement.
- About: rewritten biography + Current Roles section.
- Research: Rinn-connected framing + Current Research Agenda (7 items).
- Projects & Funding: Rinn AI national programme entry (€121,752,497 total — explicitly NOT personal/MTU allocation).
- News: Rinn appointment item (month-dated; roles user-confirmed, programme Research-Ireland-verified).
- CV: Current Appointments / Research Centres incl. Rinn; note that the April 2026 PDF predates these roles.
- sources.json: Research Ireland Rinn source (Tier 1, verified).
### Media pipeline (prepared, not published)
- 7 photographs approved by Dr Afli and recorded in gallery.json as awaiting-file (no image bytes on disk); assets/source/README.md + scripts/process_images.py ready; none published.
### Verified
- Rinn AI: award €121,752,497; 15 organisations; 33 themes; 7 clusters; funder Taighde Éireann–Research Ireland (Research Ireland + DCU/UCC, 2026-06). National director Prof. Noel O'Connor (DCU) — Dr Afli is institutional, not national, lead.
### Withheld (unchanged)
- GenDAI role title; €32M ARC Hub meaning; HEA GenAI Lab; MTU profile URL; ADAPT SIGMA→HAI correction; two student programme details. Wuhan talk title/venue held pending confirmation.

## [v4] — 2026-07-18 — De-duplication, links and photo gallery
### Changed
- About page rebuilt: concise biography + single "Current roles and affiliations" set of linked role cards (no repeated role lists); Rinn presented as ONE institutional appointment (Co-Lead; Deputy Theme Lead; PI), likewise ADAPT and HAI as single cards.
- Homepage hero trimmed to lead roles + portrait; role list no longer duplicated across Home/About.
- Institutional links added at first mention (MTU, Research Ireland/Rinn, ADAPT, REA, IEEE, ACM, ACL).
- Removed all public internal/verification language ("canonical MTU… not confirmed", "confirmation pending", withheld notes); simplified footer to "© 2026 Haithem Afli. Last updated July 2026."
### Added — photographs (22 curated, from photos.zip)
- EXIF-stripped, WebP + JPEG derivatives at thumb/medium/large with responsive srcset; originals kept private (git-ignored).
- Placed by page: portrait (home, about); talks/outreach (BIBM 2025, UKCI 2024, Wuhan 2025, Age-Friendly AI, Cork Prison session, Seminar Series, Cantillon 2022, Tech Industry); teaching (teaching, INGENIUM, promoting AI/CS, CIT seminar); research/projects (ITFLOWS 2023, Political NLP 2022 & 2024, BlueTensor, DELL, Ulster collaboration); HAI group (team building); supervision (Dr Praveen Joshi PhD — public, named in CV); gallery categorised.
- 8 near-duplicates withheld (extra Political NLP, Wuhan, Age-Friendly, Cork Prison, CIT, Praveen variants); embedded About PDF ignored; no __MACOSX.
### Tests
- New checks: every <img> has alt text; no internal verification phrases on public pages; About role cards unique per organisation.
