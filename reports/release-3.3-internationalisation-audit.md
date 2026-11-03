# Release 3.3 — Internationalisation audit

**Scope:** the public website as deployed from `main` at Release 3.2 (commit `ed0f68b`), audited before any Release 3.3 change.
**Purpose:** establish what had to change for a maintainable, honestly labelled multilingual site in English (canonical) plus French, Arabic, Turkish, Irish, Spanish, Portuguese and Chinese.
**Date:** 2026-11 (Release 3.3 branch `release-3.3-multilingual-academic-website`).

## 1. Starting point (Release 3.2)

| Area | Finding at Release 3.2 | Consequence |
|---|---|---|
| Content languages | English only: 56 public pages plus the internal `build-report.html`. | Nothing to switch to; every language other than English was "Planned — no translated pages yet". |
| Language registry | `data/languages.json` listed 13 languages. All except `en` had `status: untranslated`; `dir` was set correctly (ar/fa/he = rtl). | A sound registry to build on; no translated content attached to it. |
| Language switcher | Rendered on every page from the registry; non-English entries pointed to `languages.html`. | Honest, but offered no translated pages. |
| `hreflang` / SEO | Only `hreflang="en"` and `x-default`; no `og:locale`; sitemap with English URLs only. | Correct for an English-only site; no multilingual SEO. |
| Translation infrastructure | None in the build. `locales/en.json` existed (UI strings) but `scripts/build.py` never read it. No catalogue format, no extraction, no coverage tracking. | Any translation would have meant forking the generated HTML by hand, with no way to detect outdated text. |
| Hard-coded JavaScript strings | Interface strings built in JavaScript were English literals: "Show N more" (publications), "N photograph(s)" (gallery), result counts, assistant messages, timeline and e-mail obfuscation labels. | Translated pages would still show English UI text from scripts. |
| Dynamic values inside sentences | Counts ("64 peer-reviewed…"), build dates ("Compiled … on 2026-…"), deadline dates and UTC times were part of translatable prose. | Every rebuild would change the source text and invalidate translations. |
| Protected content | No mechanism to keep publication titles, authors, venues, DOIs, names, course codes or the patent title out of translation. | Risk of translating titles, names and identifiers that must stay verbatim. |
| Meta descriptions | Truncated by character count (`summary[:155]`), cutting words mid-way. | Poor snippets in every language; mid-word cuts also translate badly. |
| Right-to-left | No page-level RTL stylesheet (only three assistant-specific `[dir=rtl]` rules). The skip link was hidden with `left:-999px`. | In an RTL page the off-screen skip link created about 999 px of horizontal overflow. Arabic would have inherited LTR spacing and alignment. |
| Fonts | Latin font stack only; no Arabic or CJK fallbacks; letter-spacing applied to headings. | Letter-spacing breaks Arabic joining; CJK fell back to arbitrary system fonts. |
| Glossary | `data/translation_glossary.json`: 35 English entries flagged translate/do-not-translate, with no target-language forms. | No terminology control for any target language. |
| Policy | `docs/translation-policy.md`: unreviewed machine translations not published; drafts `noindex` and outside sitemaps; `require_review: true` in `config/admin_sync.json`. | Release 3.3 publishes AI-assisted, tool-checked translations, so the policy and the automation reports had to change (§3). |
| Automation | `scripts/admin_sync.py --translations` wrote a fixed text: "English canonical only; no unreviewed machine translations published". | It would have reported false information after Release 3.3. |
| Private material | `build-report.html` and `reports/` are internal. | Must be excluded from translation and from translated sitemaps. |

## 2. Requirements derived from the Release 3.3 brief

1. All public content translated into fr, ar, tr, ga, es, pt and zh, at `/<code>/`.
2. Titles, authors, venues, DOIs, statuses, the PCT patent wording, the AACL 2026 *forthcoming* status and the two course links preserved exactly; the Údarás na Gaeltachta course must not be presented as accredited or as an MTU module.
3. No page presented as translated while showing English fallback text; missing and outdated translations detectable.
4. Full Arabic right-to-left layout.
5. Multilingual SEO: localised title and meta description, self-referencing canonical, reciprocal `hreflang`, `og:locale`, sitemap alternates.
6. Linguistic validation with grammar checkers and dictionaries for every language, recorded honestly; no claim of native-speaker review.
7. A language is not shown as available until its content is translated and validated.

## 3. Design decisions taken

| Decision | Rationale |
|---|---|
| **Post-render segmentation** (`scripts/i18n.py`) of the built English pages, rather than templating every string in `build.py`. | The English generator stays the single source of truth. Translation catalogues are keyed by `sha1(source)[:12]`, so any English edit automatically makes the old translation "missing", which is how outdated text is detected. |
| **Inline markup as numbered placeholders** (`{1}…{/1}`, `{2/}`). | Translators can reorder phrases (needed for Arabic, Turkish, Irish and Chinese word order); the build verifies that placeholders match and are well nested. |
| **`translate="no"`** on protected fragments (publication titles, authors, venues, abstracts, DOIs and link labels, names, thesis titles, talk titles, the patent title, counts, dates, the e-mail address and the switcher). | Protected text is never extracted, so it cannot be mistranslated. It also tells browser translation tools not to touch it. |
| **Completeness gate**: a language is live only when *every* public page is fully translated; otherwise its folder, switcher entry, `hreflang` and sitemap entries are not generated. | Satisfies "never presented as translated while falling back to English" and "do not display languages as available until translated". |
| **Visible notice on every translated page** stating AI assistance, automated checking, no native-speaker review yet, and that English is authoritative, with a link to the English page. | Honest labelling; no claim of native review. |
| **JavaScript strings** moved to `locales/js-strings.json` and served per page as `window.I18N`, read through a small `T()` helper. | Scripted UI text is translated with the page. |
| **RTL**: `dir="rtl"` on `<html>`; a `[dir=rtl]` stylesheet block; Latin-only and protected inline runs isolated as LTR islands; clip-based skip link; Arabic/CJK font stacks; no letter-spacing for Arabic. | True bidirectional layout rather than right-alignment, with Latin names and identifiers rendered correctly inside Arabic text. |
| **Whole-word meta descriptions** (`short_desc()`), ending in an ellipsis. | Clean snippets in every language. |
| **Scope exclusion**: `build-report.html` and all of `reports/` are excluded. | Private and internal material is not translated. |

## 4. Risks identified and how they are handled

| Risk | Handling |
|---|---|
| Translations silently going stale after English edits | Hash-keyed catalogues: an edited sentence shows as missing, and the language is withdrawn until it is translated again (tested in `tests/test_site.py`). |
| Placeholder or tag corruption in translations | `check_placeholders()` runs on import, at build time and in the tests. |
| Mistranslating protected identifiers | `translate="no"` extraction exclusion, plus protected-name list in the glossary. |
| Over-claiming quality | Notice on every page; Languages page status "AI-assisted translation, checked with automated language tools; native-speaker review pending"; linguistic report lists tools actually used and tools unavailable. |
| Gendered language inferred from names | Neutral forms used for collaborators and reader address; no gender inferred from names. |
| Pre-existing internal note in public content | `event-language-of-life-wuhan` contains the English note "Venue/date taken from the repository presentation folder; confirm exact date and host department." This predates Release 3.3 and is translated faithfully. It is flagged for the site owner and was not edited without instruction. |
