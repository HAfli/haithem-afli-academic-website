# Release 3.2 — QA report

Date: 2026-11-02 · Environment: macOS, Python 3.13.1 (CI uses 3.12; the code uses no 3.13-only syntax), Node for JavaScript syntax checks.

## Summary

| Check | Result | Method |
|---|---|---|
| Data validation (`build.py --check`) | PASS | `CHECK: clean` |
| Full build | PASS | 0 broken internal links, 0 missing images, 0 missing assets |
| Test suite (`tests/test_site.py`) | PASS | 56 pages: links, a11y, privacy, JSON-LD, data integrity, plus new Release 3.2 checks |
| Negative test of new checks | PASS | Injecting "European patent" into a page made the suite fail as expected |
| Local HTTP serving | PASS | All 57 HTML pages, CSS, JS, sitemap, robots, feed → 200 from a local server |
| JavaScript syntax | PASS | `node --check` on all 7 site scripts |
| Per-page metadata | PASS | Every public page has `lang`, viewport, `<title>`, description, canonical, a single `<h1>` and OG/Twitter tags. Only `build-report.html` (internal) lacks a canonical, as before this release |
| Images | PASS | Every `<img>` has `alt`; no missing image files |
| Sitemap | PASS | 56 URLs, including `teaching.html`; English-only, which is correct with no translations |
| `hreflang` / canonical | PASS | `en` and `x-default` → canonical URL on every page; no alternates advertised for untranslated languages |
| Structured data | PASS | JSON-LD parses (test suite); new `Course` entries on the teaching page; accepted papers use `creativeWorkStatus` |
| Teaching website URLs | PASS | Both return HTTP 200 and are linked from the teaching page, homepage, theme pages and (Údarás) the Innovation page |
| External links | SEE BELOW | 189 unique external URLs checked |
| Secrets / private content | PASS | Diff scanned for tokens, keys and private emails: none. No social-media exports or private archives in the change set (`content/` archives remain git-ignored) |
| Browser rendering, mobile layout, console errors, RTL visual check | **NOT TESTED** | The Claude in Chrome extension was not connected, so no real-browser session was available |

## Course website verification

| URL | HTTP (2026-11-02) | Linked from |
|---|---|---|
| https://hafli.github.io/comp9085-ml-biology/ | 200 | teaching.html, index.html, theme-bio.html |
| https://hafli.github.io/udaras-ai-course/ | 200 | teaching.html, index.html, theme-multilingual.html, innovation.html |

## External links (189 unique)

- **163 × 200 OK.** Every link added or changed in this release is in this group: both course sites, both research sites, the arXiv HTEB record, the ACL Anthology records and the CRaFT DOI target.
- **21 × bot-protection responses** (403, 202 or 999): ACM DL, MDPI, Taylor & Francis DOI, IEEE, CORE, ResearchGate, LinkedIn, DBLP and itflows.eu home. These typically block automated clients and work in a browser. They were not changed.
- **3 × 404 (already broken before this release)**. Please supply replacements; I did not guess:
  - `http://www.let.rug.nl/clin29/Pintu_Lohar_Haithem_Afli_Andy_Way.php` (CLIN 29 abstract)
  - `https://www.itflows.eu/wp-content/uploads/2022/06/22.-D3.3-ITFLOWS.pdf`
  - `https://www.itflows.eu/wp-content/uploads/2022/06/27.-D5.3-ITFLOWS.pdf`
- **2 × timeouts / unreachable** (possibly transient): `https://doi.org/10.1017/s1351324916000152` and `https://www.computing.dcu.ie/~away/PUBS/2016/Haithem.pdf`.

## Accessibility (static review)

- New resource cards use semantic headings (`h3` within section `h2`). External-link buttons have an accessible name that includes the course title (via the existing `.sr-only` utility), and the decorative arrow is `aria-hidden`.
- New focus style (`:focus-visible` outline) on the course buttons. Colours use the existing theme tokens, so dark mode is inherited.
- The module list uses a non-interactive variant of the existing chip style, without the pointer cursor or hover change that suggests clickability.
- The languages table uses `<th scope="col">`, and each language name carries `lang` and `dir` attributes.
- The on-page contents bar on the teaching page is a labelled `<nav aria-label="On this page">`.
- The existing skip link, breadcrumb and landmark structure are unchanged.

## Responsive layout (static review only)

The new cards reuse the existing `.cards` grid (`auto-fit, minmax(240px, 1fr)`), which collapses to one column on phones. No fixed widths were introduced. **This has not been verified visually.** Please check `teaching.html` and `index.html` on a phone before or after merging.

## Remaining issues and recommendations

1. Browser QA (visual, mobile, console, RTL rendering of the switcher entries) — run in a browser before merging if possible.
2. Confirm acceptance of the EMNLP 2026 Findings and AACL 2026 papers (evidenced only by your own research sites).
3. Confirm the current legal status of WO/2024/227944.
4. Replace or remove the three dead links listed above.
5. Fix the three failing scheduled workflows (see deployment readiness report).
6. Add a `pull_request` CI workflow so PRs are validated before merge.
7. `build.py` regenerates `reports/knowledge-gaps.md` with a different generator than the committed version. The change was reverted in this release to avoid noise; worth unifying.
