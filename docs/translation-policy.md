# Translation & Multilingual Governance Policy

## Canonical source
English is the canonical source of all content. Where any difference arises, the English page and the linked official sources are the definitive references. This statement appears publicly on `languages.html` and in the notice at the top of every translated page.

## Supported languages
English (canonical) plus the Release 3.3 languages French (fr), Arabic (ar, right-to-left), Turkish (tr), Irish (ga), Spanish (es, Spain), Portuguese (pt, Portugal, AO 1990) and Chinese (zh, Simplified). Russian (ru), Persian/Farsi (fa), Hebrew (he), German (de) and Italian (it) are planned and untranslated. Registry: `data/languages.json`.

## How translations are produced and published (since Release 3.3)
- **Engine.** `scripts/i18n.py` segments the built English pages, looks each segment up in `locales/<lang>.json` (keyed by a hash of the English source) and writes `site/<lang>/…`. Run `python3 scripts/i18n.py status` for coverage and `python3 scripts/i18n.py extract` after changing English content.
- **Completeness gate.** A language is published only when every public page is completely translated. If any segment is missing — including because its English source changed, which changes its hash — the whole language is withdrawn at the next build (its folder, switcher entry, hreflang and sitemap entries disappear) until the gap is closed. Pages are never presented as translated while falling back to English.
- **Method.** Live translations are **AI-assisted** and checked with automated grammar, spelling and terminology tools (LanguageTool, Hunspell dictionaries, the Turkish morphological analyser zeyrek with TDK dictionary look-ups, OpenCC/jieba for Chinese, and the glossary check). Results are recorded in the release linguistic-quality report.
- **Labelling.** Every translated page carries a visible notice that it is an AI-assisted translation, checked with automated tools, **not yet reviewed by a native speaker**, and that the English version is authoritative, with a link to the English original.
- **Indexing.** Live languages are indexable: each page has a self-referencing canonical URL, reciprocal `hreflang` alternates (plus `x-default` → English), localised `og:locale`, and sitemap alternates. This replaces the earlier rule that machine drafts carry `noindex` and stay out of sitemaps. To revert to that rule, mark the languages `untranslated` in `data/languages.json` or remove their catalogues; the gate then withdraws them.
- **Native-speaker review.** No native-speaker review has taken place for the Release 3.3 languages. When a reviewer approves a segment, its catalogue entry changes from `"status": "ai-assisted"` to `"status": "reviewed"`; `reports/translation-coverage.md` counts reviewed segments per language.

## Scope
Only approved public content is translated. Private administrative information, internal reports (`reports/`, `build-report.html`), development files and confidential material are never translated.

## Terminology
Controlled glossary in `data/translation_glossary.json` (preferred term and accepted variants per language, with sources). Organisation names (Rinn Artificial Intelligence, ADAPT Centre, Research Ireland, Enterprise Ireland, Horizon Europe, MSCA, ERC) are **not** translated unless an official translated form exists (for example Irish *Taighde Éireann*, *Ollscoil Teicneolaíochta na Mumhan*).

## Publications, funding and deadlines
Official publication titles, author names, venues, DOIs, identifiers and BibTeX are preserved in the original language (marked `translate="no"` in the generated HTML); only short summaries and interface labels are translated. Publication statuses (including *forthcoming*) and the patent wording keep their English meaning exactly. Funding-call and conference identifiers (`HORIZON-…`, `ERC Consolidator Grant`, `ACL 2027`) are preserved; translated summaries carry: "Refer to the official call document for the definitive conditions." Legal/eligibility text is never translated as authoritative advice.

## Right-to-left
Arabic, Persian and Hebrew use true bidirectional layout (`dir="rtl"` on `<html>`), not mere right-alignment. Embedded Latin-script names, identifiers and code are isolated as left-to-right runs; logos, identifiers, code, mathematics and media controls are not mirrored. Each RTL language is tested separately.

## Newsletter
The English issue is canonical. Translated **summary** editions are the default for other languages; full translations only where review capacity exists. Multilingual emails are not sent to all subscribers by default; language is a per-subscriber preference, defaulting to English unless an approved translation exists.

## Newsletter public notice
"Translated pages are provided to improve accessibility. Where any difference arises, the English page and the linked official sources should be treated as the canonical references."

## Current status (2026-11-03, Release 3.3)
English canonical is published. French, Arabic, Turkish, Irish, Spanish, Portuguese and Chinese are published as complete AI-assisted, tool-checked translations awaiting native-speaker review. Russian, Persian, Hebrew, German and Italian remain untranslated and are not offered.
