# Publication Metadata Model

Defines how a publication is represented as a complete, interconnected knowledge object, and the workflow for verifying and updating it. Single source of truth: `data/publications.json`. The site, knowledge index, public API, CV PDF, analytics and NotebookLM packs all derive from it.

## Field schema

| Field | Required | Meaning | Source of truth |
|---|---|---|---|
| `id` | yes | Stable slug (`pub:<anthology-id>` or `pub:<year>-<slug>`). | Assigned once; never reused. |
| `title` | yes | Exact published title. | Publisher / ACL Anthology. |
| `authors` | yes | Ordered author list as published. | Publisher / Anthology. |
| `year` | yes | Publication year. | Publisher. |
| `venue` | yes | Full venue / container title. | Publisher / Anthology. |
| `type` | yes | `journal` \| `conference` \| `workshop` \| `shared-task` \| `proceedings` \| `preprint`. | Editorial. |
| `themes` | yes (≥1) | Research-theme ids (`hcai, multilingual, trustworthy, evaluation, bio, innovation`). | Editorial, from taxonomy. |
| `status` | yes | `published` \| `preprint`. | Editorial. |
| `url` | strongly preferred | Authoritative landing page (DOI resolver, anthology, arXiv). | Registrar. |
| `doi` | when minted | Verified DOI (no `https://` prefix). | Crossref / DataCite / publisher. |
| `publisher` | when known | Publisher name. | Crossref. |
| `pages`, `volume`, `issue` | when applicable | Bibliographic locators. | Crossref / Anthology. |
| `anthology_id` | ACL venues | ACL Anthology id (implies canonical URL + BibTeX). | ACL Anthology. |
| `pdf_url` | when open | Direct PDF (open access only). | Publisher. |
| `arxiv`, `arxiv_url` | when a preprint exists | arXiv id / abstract page. | arXiv. |
| `abstract` | when deposited | **Verbatim** abstract (never paraphrased). | Publisher via Crossref, or authoritative full text. |
| `note` | optional | Short factual note (e.g. patent basis). | Editorial. |
| `role` | optional | Editorial role (e.g. "General Chair / Editor"). | Editorial. |
| `verified` | yes | Provenance trail with source + date (e.g. "ACL Anthology 2026-07-17; Crossref 2026-07-18"). | Maintained on every edit. |

## Derived / generated (never hand-authored)

- **BibTeX:** ACL papers use the Anthology `.bib`; others get a BibTeX block generated deterministically from the verified fields at build time.
- **Internal links:** theme tags → `research.html#<theme>`; "More in this theme" → `collections.html#<collection>`.
- **Structured data:** `ScholarlyArticle` JSON-LD (`author`, `datePublished`, `isPartOf`, `abstract`, `publisher`, DOI `sameAs`/`identifier`).
- **Public API:** `site/api/publications.json` (public fields only).
- **Knowledge index / assistant retrieval:** `site/data/assistant-index.json`.

## Provenance & truthfulness rules

1. **Never invent** a DOI, abstract, page range, keyword, or link. If unverifiable, leave the field empty and record it in the gap report.
2. **Abstracts are verbatim.** Copy only from an authoritative deposit; never paraphrase, and never copy a *preprint* abstract onto a *published* record.
3. **Prefer the published version's identifier** over a preprint's when both exist.
4. **Reject ambiguous matches.** A title-only search hit with a conflicting venue/author is not sufficient (see the Job-Title-Matching case in `reports/publication-enrichment.md`).
5. **Every edit updates `verified`** with the source and date.

## Review workflow

```
edit data/publications.json  →  verify each field against its official source
        →  python3 scripts/build.py   (regenerates site, API, index, CV; validates links/privacy)
        →  python3 scripts/research_os.py --gaps --analytics   (refresh gap + analytics reports)
        →  python3 tests/test_site.py  (must pass)
        →  commit + push               (deploys via Actions)
```

Automated monitoring (when enabled) proposes **new** bibliographic candidates as review PRs (`scripts/monitor.py`, `.github/workflows/monitor.yml`); a human verifies and merges. Automation never edits a verified record directly.

## Knowledge-gap reporting

`python3 scripts/research_os.py --gaps` writes `reports/knowledge-gaps.md`: publications missing url / doi / themes / abstract / anthology-id, plus profile-level gaps. This is the authoritative list of what to enrich next; it is regenerated on every intelligence run and never contains fabricated content.

## Update process (adding a new publication)

1. Add a new object with `id`, `title`, `authors`, `year`, `venue`, `type`, `themes`, `status`.
2. Look up the DOI on Crossref; add `doi`, `publisher`, `pages`, `url` (`https://doi.org/<doi>`). For ACL venues, set `anthology_id` and the anthology URL instead.
3. Add `abstract` only if an authoritative verbatim one is available; add `pdf_url`/`arxiv_url` if open.
4. Set `verified` with sources + today's date.
5. Rebuild, refresh gap/analytics reports, run tests, commit, push.
