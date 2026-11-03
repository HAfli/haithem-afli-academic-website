# Release 3.3 — QA report

**Build under test:** branch `release-3.3-multilingual-academic-website`, final local build served from `site/` at `http://127.0.0.1:8733/`.
**Browser:** headless Google Chrome 156 driven over the DevTools protocol (`qa33.mjs`). The Claude in Chrome extension was not connected, so headless Chrome was used.

## 1. Automated test suite

`python3 tests/test_site.py` (run by CI before every deploy): **PASSED** — 56 English pages plus all checks below.

| Area | Checks |
|---|---|
| Existing (Release 1–3.2) | Internal links and assets, tag balance, `lang`, alt text, privacy leaks, JSON-LD, data integrity, teaching links, publication statuses, patent wording |
| Release 3.3 i18n | Live language ⇔ complete; non-live languages not advertised; every live segment present, current and placeholder-valid; every translated page present with correct `lang`/`dir`, self-canonical, notice, `hreflang` for all live languages + `x-default`; all internal links in translated pages resolve; homepage switcher and `hreflang`; sitemap entries and alternates; internal build report not translated |

Mutation check: corrupting one Irish segment's placeholders made the suite fail with the segment ID.

## 2. Browser QA matrix

**8 languages** (en, fr, ar, tr, ga, es, pt, zh) × **18 representative pages** × **2 viewports** (desktop 1366×900; mobile 390×844 at 2×) × **2 colour schemes** (light, dark) = **576 page loads**.

Pages: index, about, research, publications, teaching, projects, supervision, talks, timeline, gallery, assistant, contact, languages, privacy, industry, theme-multilingual, event-rinn-ai-colead, conference-deadlines.

Each page load recorded:
- **Errors:** uncaught JavaScript exceptions, console errors and warnings, HTTP 4xx/5xx and failed requests.
- **Layout:** horizontal overflow (`scrollWidth − innerWidth`) and the elements causing it.
- **Document:** `lang` and `dir` on `<html>`, and images that failed to load.
- **Translation UI:** the translation notice and its link to the English page, the language switcher entries, and that translated script strings (`window.I18N`) were loaded.
- **Assistant page:** a query was typed and submitted, and the localised result line was recorded.

### Results

| Check | Result |
|---|---|
| JavaScript exceptions / console errors / failed requests | 0 |
| Horizontal overflow (desktop and mobile, incl. Arabic RTL) | 0 |
| Broken images | 0 |
| `lang`/`dir` correct (ar = rtl, others ltr) | 576 / 576 |
| Translation notice with link to English (non-English pages) | 504 / 504 |
| Language switcher lists exactly en + 7 live languages | 576 / 576 |
| Translated script strings loaded (non-English pages) | 504 / 504 |
| Assistant returns localised results | 8 / 8 languages |

### Visual review (screenshots)

Screenshots were taken for index, publications, teaching, assistant and gallery in en, fr, ar, ga and zh (light), plus every language's homepage in dark mode, on desktop and mobile.

- **Arabic RTL:** layout mirrored (navigation, lists, cards, breadcrumbs, assistant answer border). Latin names, publication titles, DOIs and identifiers render as isolated left-to-right runs. No overflow on mobile; Arabic font stack applied, without letter-spacing.
- **Irish diacritics:** síneadh fada (á é í ó ú) and mutated forms (*bhfuil*, *mhaoirseachta*, *n-eochairchainteanna*) render correctly in headings, body, navigation and buttons, on desktop and mobile.
- **Chinese:** full-width punctuation and CJK font stack; Latin terms spaced from Chinese text.
- **Dark mode:** notice, switcher and assistant readable in all languages.
- **Teaching page:** both course cards keep their external links. The Údarás na Gaeltachta card is described as Irish-medium professional training, with no accreditation or MTU-module claim.

Defects found during QA and fixed:

| Defect | Fix |
|---|---|
| Assistant showed English record-type labels ("news", "milestone") and English theme names on translated pages; English showed lowercase "news" | Labels and theme names passed through `T()`; strings added to `locales/js-strings.json` and translated |
| Arabic pages overflowed by ~999 px (off-screen skip link) | Clip-based skip link (found during development) |

Observations that are not defects:
- The open "Research" menu in the assistant screenshots appears identically in English. It is an artefact of the scripted form interaction.
- Blank photo frames in full-page screenshots are lazy-loaded images that the capture did not scroll into view; all image paths resolve (test suite).

## 3. SEO metadata (spot-checked on generated pages, all enforced by tests)

- `<title>` and `<meta name="description">` translated; descriptions end on whole words.
- `<link rel="canonical">` self-referencing (`…/fr/publications.html`; language homes as `…/fr/`).
- `<link rel="alternate" hreflang>` for en, fr, ar, tr, ga, es, pt, zh and `x-default` on every page, reciprocal.
- `og:locale` per language (fr_FR, ar_AR, tr_TR, ga_IE, es_ES, pt_PT, zh_CN) with `og:locale:alternate`.
- `sitemap.xml`: 448 URLs with `xhtml:link` alternates.

## 4. External links

134 unique external URLs checked (shared by all languages):
- **Bot-blocked, not dead (20):** publisher, DOI, ResearchGate and LinkedIn URLs that return 202, 403 or 999 to scripts.
- **Dead before this release (5):**
  - CLIN29 abstract (404).
  - Two ITFLOWS deliverable PDFs (404).
  - The DCU PDF host (unreachable).

These predate Release 3.3 and are unchanged.

## 5. Accessibility notes

- `lang` on every page lets screen readers switch voice; RTL set on `<html>` for Arabic.
- Protected Latin runs inside Arabic are marked `dir="ltr"` for correct reading order.
- Translated `alt`, `aria-label`, `title` and `placeholder` attributes.
- The translation notice is plain text with a real link (keyboard reachable).
