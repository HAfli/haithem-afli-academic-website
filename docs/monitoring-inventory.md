# Monitoring Inventory

Complete inventory of every monitor declared in `config/monitors.json`, to be reviewed **before** any repository secret is configured. No API keys are assumed. Where anonymous access is possible, the monitor is already configured to run **without credentials** (`secret: null` in config). Only one source (Semantic Scholar) has an *optional* key for higher limits.

Rate limits and auth models below reflect each provider's public documentation as of July 2026; treat the exact numbers as **verify-before-relying** — they change, and each provider's Terms are authoritative. All monitors respect robots/terms and write **draft** outputs only (`reports/monitoring/`); none publishes externally or edits verified records.

## Legend
Auth = authentication needed for the data we use · Key = API key required · OAuth = OAuth flow required · Anon = can operate anonymously · Free = free tier available.

---

## Publication sources

### arXiv API
- **Purpose:** detect new/updated preprints by the author.
- **API / docs:** https://info.arxiv.org/help/api/index.html (endpoint `http://export.arxiv.org/api/query`).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** ~1 request/3 seconds; bulk use should burst-limit and cache (verify).
- **Expected secret:** none.
- **Retrieves:** preprint title, authors, abstract, arXiv id, categories, dates, PDF link.
- **Frequency:** weekly.
- **Privacy/security:** public metadata only; no personal data; identify politely via a descriptive User-Agent.

### Crossref REST API
- **Purpose:** verified DOIs, publisher, venue, dates, page numbers, sometimes abstracts (used for this release's enrichment).
- **API / docs:** https://api.crossref.org (docs https://www.crossref.org/documentation/retrieve-metadata/rest-api/).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** no hard public limit; use the **polite pool** by sending a `mailto` (configured: `Haithem.Afli@mtu.ie`) for better service (verify).
- **Expected secret:** none (mailto is not a secret).
- **Retrieves:** DOI, title, container-title, publisher, issued date, volume/issue/page, ISSN, links, abstract (JATS, when deposited).
- **Frequency:** weekly.
- **Privacy/security:** public bibliographic data; the mailto is already public contact info.

### OpenAlex API
- **Purpose:** aggregate works, concepts (keywords), open-access PDF locations, citation counts.
- **API / docs:** https://docs.openalex.org (endpoint `https://api.openalex.org/works`).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** ~100,000 requests/day and ~10/second; join the polite pool with a `mailto` (verify).
- **Expected secret:** none.
- **Retrieves:** work metadata, `concepts` (candidate keywords), `open_access.oa_url`, `cited_by_count`, ids (DOI/MAG/PMID).
- **Frequency:** weekly.
- **Privacy/security:** public data; aggregate. Citation counts recorded only with a retrieval date, never presented as permanent facts.
- **Note:** OpenAlex JSON did not return through the current fetch tooling in this environment; Crossref was used for enrichment instead. OpenAlex remains valid in CI.

### ORCID public API
- **Purpose:** author-curated works list; identity anchor for disambiguation.
- **API / docs:** https://info.orcid.org/documentation/ (public API `https://pub.orcid.org/v3.0`).
- **Auth:** Partial — the **public** record is readable without user login, but ORCID recommends a **public API client** (2-legged OAuth) to obtain a read-public token · **Key/OAuth:** a public-API client id/secret is recommended for production (verify) · **Anon:** limited/possible for basic reads · **Free:** Yes.
- **Rate limits:** provider-defined; use a token to avoid throttling (verify).
- **Expected secret (if enabled):** `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET`.
- **Retrieves:** works, external ids (DOI), employment/education (public only).
- **Frequency:** weekly.
- **Privacy/security:** only the researcher's own public record; no third-party personal data.

### DBLP
- **Purpose:** authoritative CS bibliography; venue/author disambiguation.
- **API / docs:** https://dblp.org/faq/ (author XML `https://dblp.org/pid/120/2260.xml`; search API available).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** polite use expected; heavy querying may be throttled (verify).
- **Expected secret:** none.
- **Retrieves:** publication list, venue, year, co-authors, DOI/ee links.
- **Frequency:** weekly.
- **Privacy/security:** public bibliographic data.

### Semantic Scholar (Graph API)
- **Purpose:** citations, references, influential-citation signals, TLDR summaries.
- **API / docs:** https://api.semanticscholar.org (docs https://www.semanticscholar.org/product/api).
- **Auth:** Optional · **Key:** Optional (anonymous works at a lower shared rate limit; a free key raises it) · **OAuth:** No · **Anon:** Yes (reduced limits) · **Free:** Yes (key by request form).
- **Rate limits:** shared/low without a key; higher with a key (verify current numbers).
- **Expected secret (optional):** `SEMANTIC_SCHOLAR_API_KEY`.
- **Retrieves:** paper metadata, citation/reference graph, citation counts.
- **Frequency:** weekly.
- **Privacy/security:** public data; key (if used) stored only as a GitHub Secret.

### OpenReview API
- **Purpose:** submission/review status for ARR-linked venues.
- **API / docs:** https://docs.openreview.net (API `https://api.openreview.net` / api2).
- **Auth:** Partial — public notes readable anonymously; some content requires a logged-in profile · **Key:** No · **OAuth:** No (username/password login for private content) · **Anon:** Yes for public data · **Free:** Yes.
- **Rate limits:** provider-defined; page results and back off (verify).
- **Expected secret (only if private data needed):** `OPENREVIEW_USERNAME`, `OPENREVIEW_PASSWORD`.
- **Retrieves:** public submissions/decisions for tracked venues.
- **Frequency:** per submission cycle.
- **Privacy/security:** only public venue data; never scrape private reviews.

---

## Funding sources

### CORDIS (EU projects & results)
- **Purpose:** Horizon Europe / EU project records, partners, outcomes.
- **API / docs:** https://cordis.europa.eu/ (open data at https://data.europa.eu; bulk datasets).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** dataset download / portal; no key (verify).
- **Expected secret:** none.
- **Retrieves:** project id, title, programme, partners, dates, status.
- **Frequency:** monthly.
- **Privacy/security:** public open data.

### Research Ireland (Taighde Éireann)
- **Purpose:** national calls, announcements, programme news.
- **Source:** https://www.researchireland.ie/ (news/announcements; RSS where available).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** ordinary web politeness; respect robots.txt (verify presence of an official API/feed).
- **Expected secret:** none.
- **Retrieves:** call titles, deadlines, eligibility (as published).
- **Frequency:** monthly.
- **Privacy/security:** public pages only; monitor via official feeds, never automated scraping where prohibited.

### Enterprise Ireland
- **Purpose:** national innovation/commercialisation funding.
- **Source:** https://www.enterprise-ireland.com/ (news/funding pages; feed where available).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** web politeness; respect robots.txt.
- **Expected secret:** none.
- **Retrieves:** funding programme announcements and deadlines.
- **Frequency:** monthly.
- **Privacy/security:** public pages only; official feeds only.

### EC Funding & Tenders (SEDIA) — Horizon Europe, MSCA, ERC, Digital Europe, AI Office, Health, Cybersecurity
- **Purpose:** open EU calls across relevant programmes.
- **API / docs:** https://ec.europa.eu/info/funding-tenders/opportunities/ (SEDIA search; some APIs require **EU Login**).
- **Auth:** Partial — public call search is open; programmatic SEDIA endpoints and submission require **EU Login** · **Key:** No · **OAuth:** EU Login for authenticated endpoints · **Anon:** Yes for public call browsing · **Free:** Yes.
- **Rate limits:** provider-defined (verify).
- **Expected secret (only if authenticated API used):** `EU_LOGIN_*` (not needed for public call monitoring).
- **Retrieves:** call id, topic, deadline, programme, budget (as published).
- **Frequency:** monthly.
- **Privacy/security:** public call data; no personal data.

---

## Conference sources

### ACL / *ACL calls
- **Purpose:** submission/notification/camera-ready dates for relevant venues.
- **Source:** https://aclweb.org/ and official venue sites (already verified for EMNLP 2026 in `conference_deadlines.json`).
- **Auth:** No · **Key:** No · **OAuth:** No · **Anon:** Yes · **Free:** Yes.
- **Rate limits:** web politeness.
- **Expected secret:** none.
- **Retrieves:** deadlines, locations, tracks (human-verified before publishing).
- **Frequency:** monthly.
- **Privacy/security:** public pages; deadlines are human-verified against the official source before they appear on the site.

### OpenReview venues
- As per the OpenReview entry above; used to track venue submission windows.

---

## Trend topics (no external service)
`trend_topics` in config are keywords for the (future) trend layer. **No live claim is made** about trends until a source above is connected with the appropriate access; the trend section stays empty rather than asserting anything unverified.

## Collaborators (no external service beyond the above)
Tracked only via **public identifiers** (ORCID/DBLP); names come from already-public co-authorship in `publications.json`. No private contact data is collected.

---

## Summary: what can run anonymously today

| Source | Anonymous now? | Optional key for more | 
|---|---|---|
| arXiv, Crossref, OpenAlex, DBLP, CORDIS, Research Ireland, Enterprise Ireland, EC F&T (public), ACL calls, OpenReview (public) | **Yes** | — |
| Semantic Scholar | Yes (low limits) | `SEMANTIC_SCHOLAR_API_KEY` |
| ORCID (production) | Basic reads | `ORCID_CLIENT_ID/SECRET` (recommended) |
| OpenReview (private content) | No | `OPENREVIEW_USERNAME/PASSWORD` |

**Recommendation:** enable the fully-anonymous sources first (no secrets needed). Add the Semantic Scholar key only if citation coverage needs higher throughput. Add ORCID client credentials only when moving ORCID monitoring to production volume. Do not configure any secret until this inventory is reviewed and approved.
