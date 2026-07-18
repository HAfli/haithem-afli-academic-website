# Source Authority Policy

## Hierarchy (highest to lowest)
- **Tier 1 — Primary authoritative**: official university profile, publisher page, DOI registration, ACL Anthology, Crossref, ORCID, CORDIS, official project/conference/funding/patent pages, repositories owned by the researcher.
- **Tier 2 — Strong aggregators**: Google Scholar, Semantic Scholar, OpenAlex, DBLP, Scopus, Web of Science.
- **Tier 3 — Professional self-reported**: LinkedIn, ResearchGate, academic social media, personal GitHub, CV, presentation.
- **Tier 4 — Secondary coverage**: university news, recognised professional media, partner announcements, conference reports.
- **Tier 5 — Low-confidence discovery**: unverified websites, scraped bios, people-search services, reposts, unattributed social content. Discovery leads only — never published without stronger confirmation.

## Identity resolution
Match on ORCID / DBLP / Anthology linkage or co-author/venue overlap. Never infer identity from name similarity alone. Monitored name variants: Haithem Afli, H. Afli, Afli Haithem, هيثم عفلي.

## Conflict resolution
When sources disagree: (1) state the conflict; (2) prefer the most authoritative, most recent primary source; (3) check whether the difference is dates/definitions; (4) never silently pick a value; (5) add to the verification queue; (6) request human confirmation where it materially affects the site. Citation counts and statistics always display a retrieval date.

## Current conflicts
See `docs/verification-queue.md`.

## Platform respect
Respect authentication, robots policies, rate limits, licences and terms. Never bypass anti-automation measures. Google Scholar and social media are treated as discovery and discrepancy-detection signals, not canonical authorities for metadata, funding, titles, or employment.
