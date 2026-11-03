# Release 3.3 — Translation completeness

**Source of truth:** `locales/source.json` (extracted from the built English site) and `site/api/translation-status.json` (written by every build). The figures below come from the final build of this release.

## 1. Summary

| Language | Variety | Segments translated | Page segments | Pages complete | Status | Live |
|---|---|---|---|---|---|---|
| French `fr` | France | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Arabic `ar` | Modern Standard Arabic, RTL | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Turkish `tr` | Türkiye (TDK orthography) | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Irish `ga` | An Caighdeán Oifigiúil | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Spanish `es` | Spain | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Portuguese `pt` | Portugal (AO 1990) | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Chinese `zh` | Simplified (Mainland) | 1,181 / 1,181 | 3,450 / 3,450 | 56 / 56 | AI-assisted, tool-checked | yes |
| Russian, Persian, Hebrew, German, Italian | — | 0 | — | 0 | untranslated | no (not offered) |

- **Native-speaker review:** none has taken place for any language. All 1,181 segments in each language have status `ai-assisted`; 0 are `reviewed`.
- **Source volume:** 1,181 unique segments (about 12,000 English words). 53 of them are strings used by page scripts (publication filters, gallery, timeline, assistant, e-mail link). They recur as 3,450 segment occurrences across the 56 public pages.
- **Excluded by design:** `build-report.html` (internal build diagnostics), everything under `reports/`, development files, and all `translate="no"` content (publication titles, authors, venues, DOIs, names, thesis and talk titles, the patent title, counts, dates, the e-mail address).

## 2. Per-language volume

| Language | Translated words | Characters | Segments identical to English |
|---|---|---|---|
| fr | 15,482 | 102,787 | 94 |
| ar | 12,524 | 82,386 | 69 |
| tr | 12,367 | 90,759 | 73 |
| ga | 14,564 | 102,776 | 66 |
| es | 15,246 | 101,152 | 72 |
| pt | 14,764 | 98,740 | 73 |
| zh | 4,519 (whitespace tokens; Chinese is unspaced) | 39,643 | 68 |

"Identical to English" segments were reviewed. They are proper names (Rinn Artificial Intelligence, Munster Technological University, Taighde Éireann – Research Ireland), official programme and call lists (Horizon Europe, MSCA, ERC, Enterprise Ireland schemes), course titles kept verbatim (*Machine Learning in Biology*, *Building AI Confidence in the Gaeltacht Workplace*), institution and date lines, acronyms, and words spelled the same in the target language (French *Contact*, *Publications*). No untranslated English prose was found.

## 3. Pages (all 56, in every live language)

about · analytics-map · assistant · collaborate · collections · conference-deadlines · contact · cv · event-adapt-leadership · event-adaptnmt-tooling · event-arabicnlp-palmx-2025 · event-cork-independent-2025 · event-eacl-2026-pteb · event-emnlp-2025 · event-gendai · event-hai-group-founding · event-itflows · event-iwslt-2026 · event-language-of-life-brazil · event-language-of-life-wuhan · event-patent-split-federated · event-politicalnlp-series · event-rinn-ai-colead · for-media · funding-calls · gallery · group · index · industry · innovation · journey · languages · news · newsletter · privacy · projects · prospective-phd · publications · research · research-calendar · research-intelligence · research-vision · rinn-ai · service · showcase · subscribe · supervision · talks · teaching · theme-bio · theme-evaluation · theme-hcai · theme-innovation · theme-multilingual · theme-trustworthy · timeline

Non-HTML outputs stay in English: the Atom feed, RSS and ICS feeds, JSON APIs and the CV PDF. They are linked from translated pages with translated labels.

## 4. How completeness is enforced and kept honest

1. **Hash-keyed catalogues.** Each segment is keyed by a hash of its English source. Editing English text makes the existing translation inapplicable, so the segment counts as missing.
2. **Completeness gate.** A language is generated only if all 56 pages are complete. Otherwise it is withdrawn entirely at the next build: no folder, no switcher entry, no `hreflang`, no sitemap URL. No translated page is ever served with English fallback text.
3. **Tests** (`tests/test_site.py` §16) fail the CI build if:
   - A live language has any missing, outdated or placeholder-mismatched segment.
   - A translated page is missing.
   - A non-live language is advertised.
4. **Monitoring.** `python3 scripts/i18n.py status` prints coverage. `scripts/admin_sync.py --translations` writes `reports/translation-coverage.md` (live languages, reviewed counts) and `reports/translation-review-queue.md` (missing or outdated segments per page).

## 5. Maintenance after an English edit

1. Rebuild (`python3 scripts/build.py`). Affected languages are withdrawn automatically if any segment is now missing.
2. Run `python3 scripts/i18n.py extract` (refreshes `locales/source.json`), then `python3 scripts/i18n.py status` for coverage per language. `python3 scripts/admin_sync.py --translations` lists the affected pages in `reports/translation-review-queue.md`; the missing segment IDs are those in `source.json` with no entry in the language catalogue.
3. Add the translations to `locales/<code>.json` (status `ai-assisted`, or `reviewed` after native review), re-run the linguistic checks, rebuild and run the tests.
