# Release 3.3 — Deployment report

**Status: DEPLOYED WITH DOCUMENTED LIMITATIONS**

| Item | Value |
|---|---|
| Pull request | #2 — "Release 3.3: multilingual academic website (fr, ar, tr, ga, es, pt, zh)", squash-merged |
| Merge commit on `main` | `9e21e32` (previous: `ed0f68b`, Release 3.2) |
| Deploy workflow | "Build and deploy" run 41560509265: build ✓, tests ✓, deploy ✓ (2026-11-03) |
| CI build output | `i18n: 448 pages written; languages live: fr, ar, tr, ga, es, pt, zh` (Python 3.12) |
| CI tests | `TESTS PASSED: 56 pages, links/a11y/privacy/JSON-LD/data all clean` |
| Live site | https://hafli.github.io/haithem-afli-academic-website/ |

## Quality gates before merge

| Gate | Result |
|---|---|
| Full build + `tests/test_site.py` (incl. Release 3.3 i18n checks) | Passed locally and in CI |
| Translation completeness | 1,182 / 1,182 segments, 56 / 56 pages in every language |
| Linguistic validation | Completed with the tools listed in the linguistic quality report; all flags triaged; 52 correction rules (123 segments) + French guillemet spacing applied |
| Browser QA | 576 page loads (8 languages × 18 pages × desktop/mobile × light/dark): no JS errors, no overflow, no broken images |
| Protected facts | Patent wording (PCT application), AACL 2026 *forthcoming*, course links and Údarás description verified in all languages |

## Live verification (after deployment)

- `/`, `/fr/`, `/ar/`, `/tr/`, `/ga/`, `/es/`, `/pt/`, `/zh/` and deep pages (`ar/publications`, `ga/teaching`, `zh/assistant`, `fr/languages`) return 200. Each has the correct `lang`/`dir` (Arabic `rtl`), a self-referencing canonical, 9 `hreflang` links (8 languages + `x-default`), a localised `<title>` and the translation notice (non-English).
- `sitemap.xml`: 448 URLs with alternates; `api/translation-status.json`: live = fr, ar, tr, ga, es, pt, zh.
- Live headless-Chrome check (mobile 390 px) of `ar/index`, `ga/teaching`, `zh/publications`, `fr/gallery`, `tr/assistant`, `es/conference-deadlines`, `pt/timeline`: correct `lang`/`dir`, no horizontal overflow, no console or network errors (assets and the assistant index resolve under the Pages sub-path).

## Credentials

The GitHub CLI was already authenticated on this machine (account `HAfli`). No token, password or credential appears in any commit or report.

## Documented limitations

1. **No native-speaker review** for any language. Every translated page states this, and the English page is authoritative.
2. **Turkish** has no grammar checker (LanguageTool does not support it). Spelling and morphology were checked with Hunspell, zeyrek and TDK.
3. **Arabic** has no dedicated dictionary or morphological analyser (CAMeL Tools not installed); LanguageTool and rule-based checks only.
4. **Portuguese Hunspell (Natura pt-PT)** run did not finish; LanguageTool's pt-PT dictionary was used.
5. **Irish terminology:** téarma.ie (bot challenge) and IATE (HTTP 500) were unavailable. Some NLP terms remain unconfirmed and are listed for review.
6. **Language withdrawal:** if English text changes, affected languages are withdrawn at the next build until the new segments are translated. This is intended (no English fallback) but means scheduled rebuilds can temporarily remove a language.
7. **Pre-existing, unchanged by this release:**
   - Five dead external links: CLIN29 abstract, two ITFLOWS PDFs, DCU PDF host.
   - The internal review note on the Wuhan event page, from `data/events.json`, which is now also visible in translation.
   - The failing `sync-deadlines.yml` and `generate-newsletter.yml` workflows (invalid YAML).
   - The Admin sync / Weekly source monitor PR-permission errors.
   - The Research Intelligence artefact path containing a colon.

## Rollback

Revert the merge commit (`git revert 9e21e32`) and push to `main`, or set the seven languages to `untranslated` in `data/languages.json`. The completeness gate then withdraws them at the next build. See `docs/rollback.md`.
