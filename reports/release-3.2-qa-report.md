# Release 3.2 — QA report

Date: 2026-11-02 (final pre-merge review) · Environment: macOS; Python 3.13.1 (CI uses 3.12; the code uses no 3.13-only syntax); Node 24; Google Chrome 156 (headless).

## Summary

| Check | Result | Method |
|---|---|---|
| Data validation (`build.py --check`) | PASS | `CHECK: clean` |
| Full build | PASS | 0 broken internal links, 0 missing images, 0 missing assets |
| Test suite (`tests/test_site.py`) | PASS | 56 pages: links, a11y, privacy, JSON-LD, data integrity, plus Release 3.2 checks |
| Negative tests of new checks | PASS | Injecting "European patent" into a page, or a BibTeX block into the forthcoming AACL item, made the suite fail as expected |
| Browser rendering — desktop (1366×900) and phone (390×844, touch, 2× DPR) | PASS | Headless Chrome 156 via the DevTools protocol, **in both light and dark colour schemes**: index, teaching, publications, innovation, languages and theme-bio (24 page × viewport × scheme runs) |
| Horizontal overflow / clipped elements | PASS | `scrollWidth == innerWidth` on every run; no element extends past the viewport |
| Console and runtime errors | PASS | No JavaScript exceptions, console errors or warnings. The only network error is `/favicon.ico` 404, which predates this release (no favicon is shipped) |
| Images | PASS | 35 images on teaching, index, talks and gallery force-loaded and decoded; none broken. Lazy-loaded images appear empty in full-page screenshots only because they are off-screen |
| Mobile navigation | PASS | "About" group opens and its menu stays within the viewport (right edge 369 px of 390). Teaching is in the primary nav and marked `aria-current="page"` on its page. *Fixed in this review:* on phones, "Publications" and "Teaching" shared a line; single links are now full width like the groups |
| Teaching cards and links | PASS | Both cards render 429 px wide (desktop) and 356 px (phone); buttons are 43 px tall; accessible names are "Visit the course website for <title>"; both `href`s are correct |
| Language switcher / RTL | PASS | 13 entries (English + 12). Arabic, Persian and Hebrew compute `direction: rtl` in the switcher and the Languages table |
| Local HTTP serving | PASS | All 57 HTML pages, CSS, JS, sitemap, robots and feed → 200 |
| JavaScript syntax | PASS | `node --check` on all 7 site scripts |
| Per-page metadata | PASS | Every public page has `lang`, viewport, `<title>`, description, canonical, one `<h1>` and OG/Twitter tags (internal `build-report.html` excepted, as before) |
| Sitemap / `hreflang` / canonical | PASS | 56 URLs, including `teaching.html`. `en` and `x-default` only, which is correct with no translated pages |
| Structured data | PASS | JSON-LD parses. `Course` entries on the teaching page. The forthcoming paper uses `creativeWorkStatus: Forthcoming` with no `datePublished` |
| Publication counts | PASS | 66 peer-reviewed · 1 forthcoming · 81 outputs — identical in `data/publications.json`, the Publications page, `api/publications.json` (81, with `status`), `api/analytics.json` (81) and the Ask Me index |
| Duplicate publications | PASS | No duplicate titles (normalised), IDs or DOIs |
| PDF CV | PASS | Regenerated: published-only "Selected publications" (HTEB, Findings EMNLP 2026 and CRaFT lead), a separate "Forthcoming" heading for AACL 2026, and both course websites listed under Teaching |
| Unintended changes | PASS | On pages not otherwise touched, the only differences are the shared header (Teaching nav item and data-driven language switcher) and the build date |
| Secrets / private content | PASS | No tokens, keys, private emails, social exports or private archives in the change set |

Browser testing used **headless Chrome** (the same Blink engine as desktop Chrome) because the Claude in Chrome extension was not connected. Still not covered: Safari/iOS WebKit, Firefox, a physical phone, and an actual screen-reader session.

## Publication verification (final)

| Paper | Source checked | Status on site | Notes |
|---|---|---|---|
| The Harder Text Embedding Benchmark (HTEB) — Frank, Afli | ACL Anthology `2026.emnlp-main.1044` (.bib): EMNLP 2026 proceedings, pp. 23973–24005, DOI 10.18653/2026.emnlp-main.1044 → resolves | published | Title, authors, venue, pages and DOI match |
| The Benchmark Is Not the Construct — Afli, Frank | ACL Anthology `2026.findings-emnlp.1992`: Findings of EMNLP 2026, pp. 42441–42465, DOI 10.18653/2026.findings-emnlp.1992 → resolves | published | Matches |
| CRaFT — Hossain, Afli | ACL Anthology `2026.lrec-1.406`: LREC 2026, pp. 5192–5202, DOI 10.63317/583qrad7zvbi | published | DOI is registered and resolves to ELRA (`lrec.elra.info/lrec2026-main-406`, 200 with a browser user agent) |
| Structural vs Cultural Reasoning — Hossain, Bouamor, Afli | Author confirmation (to appear in AACL 2026 proceedings); study page 200; not yet on ACL Anthology | **Forthcoming — AACL 2026** | No DOI, pages, Anthology ID or BibTeX. Shown as "AACL 2026 (scheduled to appear in the proceedings)" |

## Course website verification

| URL | HTTP | Linked from |
|---|---|---|
| https://hafli.github.io/comp9085-ml-biology/ | 200 | teaching.html, index.html, theme-bio.html, PDF CV |
| https://hafli.github.io/udaras-ai-course/ | 200 | teaching.html, index.html, theme-multilingual.html, innovation.html, PDF CV |

The Údarás programme is labelled "Professional training · delivered through Irish". It is never called a degree, accredited course or MTU academic module, and it is not listed under "Modules taught".

## External links (195 unique, re-checked in the final review)

- **170 × 200.** All ACL Anthology, arXiv, DOI (ACL) and `hafli.github.io` links return 200.
- **21 × bot-protection responses** (403, 202 or 999): ACM DL, MDPI, Taylor & Francis, IEEE, CORE, ResearchGate, LinkedIn, DBLP and itflows.eu. These block automated clients and are not broken.
- **3 × 404, all already broken before this release.** Please supply replacements:
  - `http://www.let.rug.nl/clin29/Pintu_Lohar_Haithem_Afli_Andy_Way.php`
  - `https://www.itflows.eu/wp-content/uploads/2022/06/22.-D3.3-ITFLOWS.pdf`
  - `https://www.itflows.eu/wp-content/uploads/2022/06/27.-D5.3-ITFLOWS.pdf`
- **1 × unreachable host, already failing before this release:** `https://www.computing.dcu.ie/~away/PUBS/2016/Haithem.pdf`.

## Accessibility

- New resource cards use `h3` inside section `h2`. External-link buttons carry the course title in their accessible name (`.sr-only`), and the arrow is `aria-hidden`. Buttons have a `:focus-visible` outline and are 43 px tall.
- The module list is a static chip style, without a pointer cursor or hover change. The languages table uses `<th scope="col">` plus `lang` and `dir` on each language name. The teaching page's contents bar is `<nav aria-label="On this page">`.
- Smallest rendered text on checked pages is 12.2 px (publication metadata, as before this release).

## Remaining issues (not blockers)

1. **Patent wording awaits your decision.** See the implementation report, section 3.
2. AACL 2026 paper: switch to `published` once the official proceedings record appears.
3. Three dead links and one unreachable host, all already broken before this release (listed above).
4. Already failing before this release, unrelated to it: three scheduled workflows fail daily, and two workflow files have invalid YAML (see the deployment readiness report).
5. CI cannot regenerate the PDF CV because ReportLab is not installed in `deploy.yml`. The committed PDF is what deploys, and it was regenerated for this release.
6. No `pull_request` CI workflow; no favicon.
7. `build.py` regenerates `reports/knowledge-gaps.md` with a different generator than the committed one. The regenerated file was not committed.
