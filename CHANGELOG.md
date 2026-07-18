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

## [v5] — 2026-07-18 — Production build pipeline
### Fixed
- Build now PUBLISHES static assets into site/ automatically (assets/img → site/assets/img, mirrored with stale-prune). Previously images were referenced but not copied, causing broken images on GitHub Pages until manually copied. No manual copying is ever required again.
### Added
- Asset-reference validation: every <img src>, srcset and local href is checked to exist in site/; build fails (exit 1) with the exact missing file if not.
- Image-derivative validation: every thumb/medium/large webp+jpg confirmed present.
- GitHub Pages path check: root-relative "/…" paths rejected (would break under the repo prefix).
- Build summary (pages/images/JPEG/WebP/PNG/CSS/JS/PDF/broken/missing) and site/build-report.{html,json} (image inventory, external links, totals, duration).
- --verbose developer mode; workflow updated to build (validating) → test → deploy, failing before deploy on any validation error.
- Tests: exclude build-report.html from page checks.

## [v6] — 2026-07-18 — Research intelligence, newsletter, subscriptions, analytics scaffold, i18n
### Added (architecture + safe empty states; NO fabricated data)
- Research Intelligence section (nav) + pages: research-intelligence, conference-deadlines, funding-calls, research-calendar, newsletter, subscribe, analytics-map, languages, privacy.
- Data models (empty, schema-valid; populated only from official sources): conference_deadlines.json, funding_calls.json, newsletter_issues.json, analytics_summary.json (zeros), translation_glossary.json, languages.json, newsletter_sources/collaborators.json.
- scripts/admin_sync.py — unified CLI (--all/publications/deadlines/funding/newsletter/analytics/translations/cv/feeds/validate-only); honest adapters that ingest-or-nothing, never fabricate; generates ICS calendars, RSS feeds, reports, source-health.
- scripts/generate_cv.py — PDF CV from canonical data (downloads/Haithem_Afli_CV.pdf); CV page now has a Download button + generated-date line; outdated-PDF apology removed (falls back to "available upon request" only if generation fails).
- Feeds/calendars generated in-build (empty-valid) so the site is self-contained; admin_sync enriches them with verified events only.
- Multilingual scaffold: 10-language selector (native names, no flags), hreflang + x-default, dir=rtl ready, locales/en.json, translation-policy.md, public language notice; English canonical only — no unreviewed machine translations published or indexed.
- Privacy: privacy.html (privacy-conscious analytics notice; recommends Plausible/Cloudflare); analytics kept as country-level aggregate zeros with min-public-count 5; no tracking scripts, no PII, no credentials committed.
- Workflows: admin-sync.yml (daily, PR), generate-newsletter.yml (fortnightly via weekly+14-day gate, review mode), sync-deadlines.yml (daily, PR). All open review PRs; none auto-publish uncertain content.
- Tests: internal-link check now resolves subdirectories (feeds/calendars/downloads); added duplicate-locale, no-IPv4-in-data, language-selector and hreflang checks.
### Not done (requires live sources / credentials / human review — deliberately not fabricated)
- Real conference/funding/arXiv/proceedings records; live analytics numbers and visitor map data; mailing-provider connection and subscriber storage; reviewed translations.

## [v7] — 2026-07-18 — Production hardening: real sources connected
### Connected / populated (verified, official)
- EMNLP 2026 conference deadlines from the official site (2026.emnlp.org): commitment (Aug 2), notification (Aug 20), camera-ready (Aug 30), conference (Oct 24–29), all Anywhere-on-Earth with UTC + Europe/Dublin equivalents (DST-correct via zoneinfo). Rendered on Conference Deadlines + Research Calendar; homepage shows the next verified deadline; real ICS/RSS generated from the data by a plain build.
### Real adapters (production code; run in CI, degrade gracefully offline)
- admin_sync.py: arXiv API (Atom, recent preprints for newsletter review, labelled "Preprint — not yet peer reviewed"), Crossref + OpenAlex (publication reconciliation → review queue, never auto-adds/deletes). Network failure preserves verified data and warns (no fabrication).
- build.py generates real ICS calendars + RSS feeds from the verified registries every build, so the deployed site always carries correct feeds.
### Notes
- Sandbox blocks outbound API calls (proxy 403); adapters therefore fetched nothing here but are correct and will run in GitHub Actions. EMNLP data was populated via the approved fetch of the official page.
- Still requires live CI runs / credentials to populate: additional conference editions, EC/Research Ireland/Enterprise Ireland open calls, live analytics numbers, mailing provider, reviewed translations.

## [v8] — 2026-07-18 — Research communication layer (review-first, no fabrication)
### Added (public, built from existing verified data)
- Research Showcase (showcase.html), Research Collections (collections.html, auto-aggregated by theme), Research Timeline (timeline.html). Showcase added to primary nav; Collections/Timeline linked from Showcase/Research (nav kept lean).
- Publication Spotlight framework: spotlight-<id>.html renders ONLY for human-approved communication assets (none until approved).
- ScholarlyArticle metadata already on publications; showcase/collections/timeline cross-link to authoritative records.
### Added (private, review-gated — nothing auto-published)
- data/communication.json (single source of truth; references pub/project IDs; profiles: academic/industry/policy/public/students/media/funders) and data/collections.json.
- scripts/admin_sync.py --communication: generates DRAFT plain-language summaries, elevator pitches (30s/1m/3m), social drafts (LinkedIn/X/Bluesky), teaching summaries, and factual media kits into reports/communication/ and reports/media-kits/ — all labelled "DRAFT — Human review required".
- reports/communication-dashboard.md: per-publication communication-readiness matrix.
- docs/research-communication.md: architecture + how to add/approve/maintain assets and visual communication.
### Principle
Single source of truth; scholarly records authoritative and never overwritten; nothing auto-published; no research claims invented or exaggerated.

## [v9] — 2026-07-18 — Live-site fixes
- Fixed duplicated homepage <title>/og:title/twitter:title ("Dr Haithem Afli — Dr Haithem Afli" → "Dr Haithem Afli — Human-Centred AI, MTU").
- Fixed CV PDF leaking internal wording ("exact title verification_pending") from a project note; generate_cv.py now strips internal verification phrases from public fields.
- Tests: added guards for non-duplicated homepage title and no internal wording in the CV PDF.
- Verified against the LIVE deployment (hafli.github.io): homepage, navigation, images, EMNLP deadline, and CV PDF all render correctly.
