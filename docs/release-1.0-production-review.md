# Release 1.0 — Final Production Review & Polish

Final review before Release 1.2 (Multimedia & Research Communication). No new features — accuracy, consistency, usability, accessibility, performance and presentation only. Build green (29 pages), all tests pass, no fabricated metadata.

## Summary of improvements

**1. Publication provenance banner (professional).** The technical reconciliation note was replaced with visitor-facing wording: records are maintained on an ongoing basis, metadata comes from authoritative scholarly sources (ACL Anthology, Crossref, publishers), and the record is continuously updated. No mention of CV/LaTeX, source tags, flags or internal reconciliation. Technical provenance remains in `docs/publication-metadata-model.md` and the private `reports/`.

**2. Email obfuscated sitewide.** The raw address no longer appears in any page HTML source. A reusable component holds the address in two `data-` attributes and displays `Haithem.Afli [at] mtu.ie`; a small script (`email.js`) reconstructs the address only on user action for a **Copy** button (with an accessible status message) and the mailto link. Removed the address from JSON-LD and from the homepage, contact, privacy and subscribe pages. Enforced by a test that fails on any raw address or `mailto:` in the HTML. (The downloadable CV PDF retains a real contact email, as is standard for a CV — noted under manual items.)

**3. "Research Assistant" → "Ask Me".** Renamed consistently across navigation, menu, page title, headings, aria-labels, meta description and internal links (0 occurrences of the old label remain in the site). The feature now reads as personal rather than technical while keeping its trust framing.

**4. Planned languages.** Added **Türkçe** (LTR) to the list and the language selector, in the requested order. RTL rendering for Arabic, Persian and Hebrew is unchanged and verified present on every page.

**5. Feeds & calendars.** The bare link list became four described cards — Conference Deadlines (RSS), Funding Opportunities (RSS), Research Updates (RSS) and Research Calendar (ICS) — each with purpose, audience and typical use. The raw XML/ICS feeds are unchanged.

**6. Funding accuracy.** GenDAI role corrected to **"Beneficiary"** (the previous "MTU Institutional Lead" wording and an internal verification tag were removed). Verified the rest: ITFLOWS, WARIFA, STOP, SliceNet = Beneficiary; ELITE-S = Linked Third Party; ADAPT = PI & MTU Lead; Rinn AI roles user-confirmed; ARC Hub and HEA GenAI Lab remain **withheld** pending official confirmation. No overstated roles; official programme wording preserved. No internal verification terms leak to any public page.

**7. Contact page.** Retains the obfuscated email and now lists scholarly profiles — ORCID, Google Scholar, DBLP, ACL Anthology, LinkedIn, plus **GitHub** — complementing the existing contact details.

**8. Homepage.** Simplified the contact section (no inline email; a single clear route to the contact page) and kept the hero focused on who, what, the group and how to engage. Implementation-oriented language reduced.

**9. Footer.** Now carries grouped links — Institutions (MTU, Human-Centred AI Group, Rinn AI, ADAPT) and Scholarly profiles (ORCID, Google Scholar, ACL Anthology, DBLP, GitHub) — plus "Last updated automatically: <date>" driven by the build date.

**10. Accessibility & UX.** Copy button has an `aria-label` and an `aria-live` status; footer navigation is labelled; skip link, single `h1`, `main` landmark and per-image alt text remain enforced by tests. Focus-visible outlines and reduced-motion handling retained.

**11. Internal consistency.** Every publication statistic derives from the single source (`data/publications.json`) — verified equal at **77** across the publications page, timeline, public API, analytics, knowledge graph and Ask Me index.

**12. Public vs internal separation.** Scanned the built site: no `latex-canonical`, `reconciliation`, `verification_pending`, `WITHHELD`, `per CV`, or `source=` terms appear on any public page. Developer detail lives only in `docs/` and private `reports/`.

**13. Professional writing.** Reviewed wording for British/Irish English and a factual, non-promotional tone; removed implementation phrasing from the subscribe and privacy notes.

**14. Visual consistency.** The new email control, footer and feed cards reuse the existing card/button/typography system and CSS variables — consistent spacing, colour and hierarchy.

**15. SEO & metadata.** Per-page titles and meta descriptions are unique (no duplicates found); Open Graph, Twitter cards, canonical URLs, hreflang, sitemap and robots remain intact and valid.

**16. Performance.** Non-hero images already use responsive `srcset`/`sizes`, `loading="lazy"` and explicit dimensions (no layout shift); added `decoding="async"` to those and `fetchpriority="high"` to the hero. No redesign. Static site; API payload ~40 KB.

## Final quality gate

- ✓ Build passes (29 pages, 0 broken links, 0 missing assets)
- ✓ Tests pass (links, accessibility, privacy, JSON-LD, API, private-leak, email-obfuscation, Ask Me, Türkçe)
- ✓ No broken links · ✓ Accessibility checks pass
- ✓ Funding verified (GenDAI = Beneficiary; withheld items still withheld)
- ✓ Publication statistics verified consistent (77 everywhere)
- ✓ RSS valid · ✓ ICS valid (unchanged)
- ✓ Türkçe added · ✓ "Ask Me" implemented · ✓ Email obfuscated
- ✓ Homepage simplified · ✓ Contact page improved · ✓ Footer improved
- ✓ Internal consistency maintained

## Remaining manual verification items

These are accuracy items only I cannot fully confirm from an authoritative source without you; none blocks launch:

- **Funding amounts/dates** for GenDAI, ITFLOWS, WARIFA, STOP, ELITE-S, SliceNet are shown per CV pending a CORDIS cross-check; ADAPT centre total and ARC Hub/HEA remain withheld until official confirmation.
- **CV PDF email:** the downloadable CV keeps a real contact email (standard practice). Say the word and I will obfuscate or remove it there too.
- **MTU staff-profile URL:** none located; recommend requesting an official page to link.
- **20 publication records** flagged in the earlier reconciliation still await manual metadata confirmation (grey literature, host links, one malformed title).

## Production readiness assessment

**Ready for public launch.** The site is accurate, internally consistent, accessible, privacy-respecting (obfuscated contact, no trackers, no internal terminology exposed), performant and professionally presented. Deployment requires the usual `git push` from your machine. Release 1.2 has **not** been started.
