# Release 1.3 — Implementation Report
_Generated 2026-07-22. A real, reviewable implementation: 15 canonical Event Pages, Research Journey, homepage highlights, milestone dataset, DAM states, social ingestion workflow. Built only from verified evidence; private assets are NOT published (metadata-only / staged-for-review).__

## A. Implemented Event Pages (15)
All are `approved-public` **narrative** pages built from already-public verified records (publication, project, news, profile). Any slides/recordings remain private (`materials: on-request`) pending file-level review.

| Event id | Title | CIS | Evidence | State | Unresolved |
|---|---|---|---|---|---|
| rinn-ai-colead | Institutional Co-Lead, Rinn Artificial Intelligence  | 90 | project, official link | approved-public | — |
| language-of-life-brazil | Keynote — “The Language of Life”, Hologenomic Data A | 84 | profile/role record | approved-public | — |
| language-of-life-wuhan | Invited talk — “The Language of Life”, Wuhan Univers | — | profile/role record | approved-public | Venue/date taken from the repository pre |
| patent-split-federated | European patent — On-Air Split Federated Learning wi | 82 | publication, official link | approved-public | — |
| adapt-leadership | Principal Investigator & MTU Lead, ADAPT Centre | 80 | project, official link | approved-public | — |
| politicalnlp-series | Founder & Chair — PoliticalNLP workshop series | 74 | publication | approved-public | — |
| cork-independent-2025 | Media coverage — “Ireland at AI ‘crossroads’”, Cork  | 79 | news, official link | approved-public | — |
| emnlp-2025 | Findings of EMNLP 2025 — GASE and sign-language tran | 77 | publication | approved-public | — |
| eacl-2026-pteb | EACL 2026 — PTEB: robust text-embedding evaluation | 78 | publication | approved-public | — |
| iwslt-2026 | IWSLT 2026 — robust cascaded speech translation (ADA | 70 | publication | approved-public | — |
| gendai | GenDAI — Horizon Europe project (Beneficiary) | 75 | project, official link | approved-public | — |
| itflows | ITFLOWS — Horizon 2020 project (Beneficiary) | 72 | project, official link | approved-public | — |
| adaptnmt-tooling | adaptNMT & adaptMLLM — open-source multilingual MT t | 70 | publication | approved-public | — |
| hai-group-founding | Founding of the Human-Centred AI Research Group, MTU | 78 | official link | approved-public | — |
| arabicnlp-palmx-2025 | ArabicNLP 2025 — winning PalmX system for Arabic cul | 73 | publication | approved-public | — |

## B. Assets ready for publication (subject to final review)
No media file is `approved-public` yet. The strongest **candidates** (real decks/recordings in `content/`, to publish as PDF + transcript after review): the *Language of Life* keynote deck (Brazil 2024 / Wuhan 2025), the PoliticalNLP slides, and the ITFLOWS materials. Recommend approving these first.

## C. Assets requiring review
- **Copyright / third-party:** co-authored decks and any slides containing third-party figures (most Presentations/* decks).
- **Consent:** photographs of identifiable people — `content/HAI/2025/Pictures/`, `content/HAI/photos/` (staged-for-review).
- **Factual verification:** Wuhan University talk — confirm exact date and host department (folder-derived).
- **Image/media quality:** several older seminar decks are low-value (`rejected-low-value`).
- **Confidentiality:** 10 private folders (NDAs, recruits, internships, proposals, visitors, NCSC) — `rejected-private`, excluded from git and build.

## D. Social-media collection queue (~15 targets — verify before claiming they exist)
For each: **target event · platform · date clue · what to capture · event_id · why**. These are *collection targets*, not confirmed posts.
1. Rinn AI Co-Lead announcement · LinkedIn · 2026 · post + photo · `rinn-ai-colead` · national leadership signal.
2. Brazil keynote 'The Language of Life' · LinkedIn/X · 2024 · stage photo + caption · `language-of-life-brazil` · international keynote.
3. Wuhan University visit · LinkedIn/X · 2025 · photo + caption · `language-of-life-wuhan` · international reach.
4. European patent granted/filed · LinkedIn · 2024 · announcement · `patent-split-federated` · IP/innovation.
5. GenDAI kickoff · LinkedIn · 2024 · project post · `gendai` · Horizon Europe.
6. EMNLP 2025 Findings · X/LinkedIn · 2025 · paper post · `emnlp-2025` · flagship publication.
7. ArabicNLP/PalmX win · LinkedIn/X · 2025 · result post · `arabicnlp-palmx-2025` · competition win.
8. EACL 2026 PTEB · X · 2026 · paper post · `eacl-2026-pteb` · flagship publication.
9. IWSLT 2026 · X · 2026 · shared-task post · `iwslt-2026` · low-resource speech.
10. Cork Independent feature · LinkedIn · 2025-05 · share of article · `cork-independent-2025` · media impact.
11. PoliticalNLP @ LREC-COLING 2024 · LinkedIn · 2024 · workshop photo · `politicalnlp-series` · leadership.
12. HAI group milestone (new members/visitors) · LinkedIn · 2024–2026 · group photo (consent) · `hai-group-founding` · group growth.
13. ADAPT activity · LinkedIn · — · role post · `adapt-leadership` · institutional.
14. adaptNMT/adaptMLLM release · X · 2023 · tool post · `adaptnmt-tooling` · open-source impact.
15. ITFLOWS dissemination · LinkedIn · 2020–2023 · project post · `itflows` · EU project.

## E. Missing strategic assets (updated)
- Professional portrait; 4–6 consented keynote/conference photographs.
- Talk slides/video for EMNLP/EACL/IWSLT (not in content/).
- SlideShare PDFs (profile bot-blocked).
- Curated LinkedIn/X/Facebook posts (workflow + templates now ready; none supplied yet).
- Short NotebookLM/overview video introducing the research.
- Official MTU staff-profile URL.

## F. Changes made
- **data/milestones.json** — +3 verified milestones (23 total), naming/consistency audit.
- **data/events.json** — NEW: 15 canonical Event entities.
- **scripts/build.py** — Event Page renderer (15 pages, hidden-when-empty sections, provenance, JSON-LD, breadcrumbs), recommendation strip, journey→event links, homepage International Highlights, milestone timeline, KG milestone/news nodes.
- **reports/dam-registry.json** — per-asset `state` (approved-public/staged/metadata-only/rejected-private/rejected-low-value) + public_derivative/file_review.
- **content/social-curated/** — `_template/post.md`, `slideshare/_template/metadata.md`, README workflow.
- **.gitignore** — exclude the raw 21 GB content/ archive and exports; keep only the curated scaffold.
- **docs/research-communication-strategy.md** — strategy (prior step).
- **reports/release-1.3-implementation.md** — this report.

## Build & tests
45 pages (15 new Event Pages + Research Journey); 0 broken links; full test suite passes. No private asset is published; nothing fabricated.