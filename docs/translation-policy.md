# Translation & Multilingual Governance Policy

## Canonical source
English is the canonical source of all content. Where any difference arises, the English page and the linked official sources are the definitive references. This statement appears publicly on `languages.html`.

## Supported languages
English (canonical) plus Irish (ga), Arabic (ar), Spanish (es), Russian (ru), Persian/Farsi (fa), Hebrew (he), German (de), Italian (it), French (fr). Registry: `data/languages.json`.

## Machine translation
Unreviewed machine translations are **not** published as authoritative content. Drafts (if ever enabled) carry a visible notice and `noindex`, and are excluded from sitemaps. Default config: `auto_generate_drafts: false`, `auto_publish: false`, `require_review: true` (`config/admin_sync.json`).

## Workflow
English canonical → machine-assisted draft → terminology + formatting checks → human/trusted review → approved → publish. Statuses: untranslated · machine-draft · under-review · approved · outdated · archived. Each translated page records `source_language`, `source_version` (hash/date), `translated_at`, `reviewed_at`. Source-hash changes mark translations outdated for re-review.

## Terminology
Controlled glossary in `data/translation_glossary.json`. Organisation names (Rinn Artificial Intelligence, ADAPT Centre, Research Ireland, Enterprise Ireland, Horizon Europe, MSCA, ERC) are **not** translated unless an official translated form exists.

## Publications, funding and deadlines
Official publication titles, author names, venues, DOIs, identifiers and BibTeX are preserved in the original language; only short summaries and interface labels are translated. Funding-call and conference identifiers (`HORIZON-…`, `ERC Consolidator Grant`, `ACL 2027`) are preserved; translated summaries carry: "Refer to the official call document for the definitive conditions." Legal/eligibility text is never translated as authoritative advice.

## Right-to-left
Arabic, Persian and Hebrew use true bidirectional layout (`dir="rtl"` at the container level), not mere right-alignment. Logos, identifiers, code, mathematics and media controls are not mirrored. Each RTL language is tested separately.

## Newsletter
The English issue is canonical. Translated **summary** editions are the default for other languages; full translations only where review capacity exists. Multilingual emails are not sent to all subscribers by default; language is a per-subscriber preference, defaulting to English unless an approved translation exists.

## Newsletter public notice
"Translated pages are provided to improve accessibility. Where any difference arises, the English page and the linked official sources should be treated as the canonical references."

## Current status (2026-07-18)
English canonical is published. All other languages are `untranslated` and not indexed; the language selector links to `languages.html` explaining status. No machine translations have been published.
