# Release 3.3 — Implementation report

**Branch:** `release-3.3-multilingual-academic-website` (from `main` at `ed0f68b`, Release 3.2).
**Languages:** English (canonical) + French `fr`, Arabic `ar` (right-to-left), Turkish `tr`, Irish `ga`, Spanish `es` (Spain), Portuguese `pt` (Portugal, AO 1990), Chinese `zh` (Simplified).
**Output:** 56 public English pages; 7 × 56 = 392 translated pages under `site/<code>/`. The build rewrites all 448 pages (English included) to add the language switcher, `hreflang` and canonical metadata.

## 1. Architecture

```
data/*.json ──► scripts/build.py ──► site/*.html (English, canonical)
                                         │
                       scripts/i18n.py ◄─┘  segments every public page
                         │  locales/source.json   (extracted English segments, hash-keyed)
                         │  locales/<code>.json   (translations + status per segment)
                         │  locales/js-strings.json (strings used by page scripts)
                         ▼
                site/<code>/*.html  + sitemap alternates + site/api/translation-status.json
```

- `build.py` runs `i18n.build()` after its own validation, and the build fails (exit 1) on any translation error (placeholder mismatch, malformed markup). CI (`.github/workflows/deploy.yml`) needs no change: build → test → deploy.
- `python3 scripts/i18n.py extract` refreshes `locales/source.json` after English edits; `python3 scripts/i18n.py status` prints coverage per language.

## 2. Segmentation and translation model

- **Segments:** block-level text runs of the rendered English HTML, plus the translatable attributes `alt`, `title`, `aria-label` and `placeholder`, and the `description`, `og:title`, `og:description`, `twitter:*` metadata and `<title>`.
- **Inline markup** becomes numbered placeholders (`{1}…{/1}` for paired tags, `{2/}` for void or protected elements), so translations can reorder phrases. Placeholders are validated (same set, correctly nested) at import, at build time and in the tests.
- **IDs** are `sha1(source)[:12]`: editing an English sentence produces a new ID, so the old translation is no longer used. The segment shows as missing and the language is withdrawn until it is translated again.
- **Protected content** carries `translate="no"` and is never extracted: publication titles, authors, venues, abstracts and link labels (DOI, arXiv, ACL Anthology, BibTeX, PDF); project names; supervisee names and thesis titles; talk titles and events; the patent title; counts; build and deadline dates and UTC times; the obfuscated e-mail address; the language switcher.
- **Status per segment:** `ai-assisted` for all Release 3.3 translations. A native-speaker reviewer changes a segment to `reviewed`; `reports/translation-coverage.md` counts reviewed segments.

### Volume

| | Count |
|---|---|
| English source segments | 1,181 (11,950 words), including 53 JavaScript and system strings |
| Page-level segment occurrences | 3,450 across 56 pages |
| Segments translated per language | 1,181 / 1,181 for each of fr, ar, tr, ga, es, pt, zh |

## 3. Page generation per language (`scripts/i18n.py`)

| Step | What it does |
|---|---|
| `_translate` | Replaces each segment and attribute; protected fragments are kept as-is. |
| `_relocate` | Prefixes relative asset paths with `../` for pages one folder down. Links to other pages stay inside the language folder. |
| `_notice` | Inserts the visible AI-assisted translation notice with a link to the English original. |
| `_ltr_islands` | In Arabic, isolates protected and Latin-only inline runs (`dir="ltr"`) so names, titles and identifiers render correctly inside RTL text. |
| `_jsonld` | Localises `inLanguage` and translatable fields in JSON-LD (including BreadcrumbList); titles and identifiers are untouched. |
| `_js_i18n` | Writes `window.I18N` (translated JavaScript strings) and `window.I18N_BASE` (`../`) for scripts that fetch data. |
| `_head` | Sets `<html lang dir>`, the self-referencing canonical URL, reciprocal `hreflang` (all live languages + `x-default` → English), `og:locale` and `og:locale:alternate`. |
| `_switcher` | Language switcher listing English plus live languages only, each with `lang`/`dir`/`hreflang`, linking to the same page in that language. |
| `_sitemap` | One `<url>` per page and language, with `xhtml:link` alternates. |
| `_report` | `site/api/translation-status.json`: per-language segment and page completeness. |

**Completeness gate:** `available()` returns true only if every public page is fully translated; only those languages are generated, offered or advertised. Stale language folders are removed at each build.

## 4. Changes to `scripts/build.py`

- New helpers: `nt()` (wrap a fragment in `translate="no"`), `short_desc()` (whole-word meta descriptions ending in "…"), `pub_venue()` returning protected HTML, and `link(..., notr=True)`.
- Protected markup applied across publications, projects, supervision, talks, events, the patent, counts, dates and deadline cells.
- English source fixes made while preparing segments: topic labels "NLP"/"Responsible AI"; "split-federated-learning line behind the 2024 international patent application"; supervision record reads "Patent application WO/2024/227944".
- JavaScript: `T()` helper in the publications, gallery, timeline, e-mail and assistant scripts. The assistant fetches its index from `(window.I18N_BASE||'')+'data/assistant-index.json'`, so it works from language folders.
- CSS: `[dir=rtl]` block (mirrored padding, borders, list markers and arrows); clip-based skip link (removes about 999 px of RTL overflow); Arabic and CJK font stacks; no letter-spacing for Arabic; `.i18n-notice` style.
- Languages page: real status per language ("Published — AI-assisted translation, checked with automated language tools; native-speaker review pending"), rewritten lede and principles, native names and codes marked `translate="no"`.

## 5. Data, configuration and documentation

| File | Change |
|---|---|
| `data/languages.json` | fr, ar, tr, ga, es, pt, zh → `status: "ai-assisted"` with `variety`; ru, fa, he, de, it remain `untranslated`. |
| `data/translation_glossary.json` | Rewritten: 34 terms with preferred form and accepted variants in all seven languages, notes and sources, plus 30 protected names. |
| `locales/` | `source.json`, `js-strings.json` and seven language catalogues. |
| `docs/translation-policy.md` | Updated for the Release 3.3 model (AI-assisted, tool-checked, completeness gate, indexing, labelling, review status). |
| `config/admin_sync.json` | Adds tr, pt, zh and documents the live-translation model. |
| `scripts/admin_sync.py` | `--translations` now computes coverage, live languages and reviewed-segment counts from the i18n engine instead of writing a fixed "English only" text. |
| `tests/test_site.py` | Release 3.2 switcher check replaced by i18n checks (§6). |

## 6. Tests added (`tests/test_site.py`, section 16)

- **Live languages:** a language is live if and only if every page and segment is complete; non-live languages have no folder and no `hreflang`.
- **Catalogues:** every source segment of each live language exists, matches the current English source and is non-empty; placeholders are checked with `check_placeholders()`.
- **Every translated page:**
  - Present, with the correct `lang`/`dir` and a self-referencing canonical.
  - Carries the translation notice and `hreflang` for en, `x-default` and every live language.
  - Every internal link and asset resolves.
- **Homepage and sitemap:**
  - The homepage advertises every live language in the switcher and `hreflang`.
  - The sitemap lists each language with alternates.
  - The internal build report is not translated.

The checks were mutation-tested: corrupting one Irish segment's placeholders made the suite fail with the exact segment ID.

## 7. Preserved facts (unchanged in every language)

Verified by script across all seven catalogues:

- Publication titles, authors, venues, DOIs and statuses are protected. The AACL 2026 paper remains "forthcoming", rendered as À paraître / قيد النشر / Yayımlanacak / Le foilsiú / De próxima publicación / A publicar / 即将发表.
- Patent: the identifier WO/2024/227944 is kept verbatim in all 14 segments that carry it, in every language. Every language renders it as an international (PCT) patent application (filed 3 May 2024, published 7 November 2024; applicant MTU), with dates localised. No translation contains "granted" or "European patent" wording.
- The two course websites keep their URLs. The four Údarás na Gaeltachta segments describe Irish-medium AI literacy training delivered by MTU for Údarás na Gaeltachta. No translation calls it accredited or an MTU module.
