# Publications Page Correction Pass — 2026-07-22

Focused correction of the Publications page and its underlying metadata. No verified record was removed; nothing was fabricated.

## 1. Files modified
- `data/publications.json` — AICS 2019 record recovered; two `et al.` author lists completed; LoResMT event/deposit years separated; AICS theme corrected.
- `scripts/build.py` — professional type labels; output-category sections with counts; new BibTeX generator (unique keys, correct entry types, no malformed authors); source-link priority; compact cards; one-paragraph intro; removed the repeated "More in [theme]" line; `PUBS_JS` rewritten (search + year + type + result count + progressive disclosure); CSS for the new controls.
- `tests/test_site.py` — new checks: unique BibTeX keys, no `et al.`, no empty titles/authors, no raw type labels, filters present, category sections present, cross-artefact count consistency.
- `reports/publications-correction.md` — this report.

## 2. Corrected malformed record
**AICS 2019** — the placeholder title *"In The 27th Irish Conference on Artificial Intelligence and Cognitive Science"* was recovered from the official CEUR-WS proceedings (Vol-2563, paper `aics_37`, pp. 400–411):
- **Title:** *A Comparative Analysis of Classification Techniques for Cervical Cancer Utilising At Risk Factors and Screening Test Results*
- **Authors:** Sean Quinlan, Haithem Afli, Ruairi O'Reilly
- **Venue:** 27th AIAI Irish Conference on Artificial Intelligence and Cognitive Science (AICS 2019), Galway
- **Pages:** 400–411 · **URL:** paper-level `ceur-ws.org/Vol-2563/aics_37.pdf`
- **Theme:** corrected `hcai` → `bio` (cervical-cancer screening classification is AI for healthcare)
- Manual-review flag removed; provenance recorded as CEUR-WS official proceedings.

## 3. Duplicate BibTeX keys fixed
Keys are now deterministic and unique (`firstauthor + year + short-title token`). Across all 77 records exactly **one** base collision arose and was disambiguated:
- `hossain2025adapt` (ADAPT–MTU HAI at PalmX 2025) vs `hossain2025adapta` (ADAPT–MTU HAI at QIAS2025).

All 77 records carry a unique `data-bibkey`; a test now fails the build if any two collide.

## 4. Author lists completed (from the canonical CV)
- **Stool and Ruminal Microbiome… (Frontiers in Genetics, 2022):** `et al.` replaced with the full 12-author list.
- **Putative Mobilized Colistin Resistance… (BMC Microbiology, 2021):** `et al.` replaced with the full 6-author list.

No `et al.` remains anywhere; BibTeX is suppressed for any record whose author list is incomplete, so `and et al. and` can never be emitted.

## 5. BibTeX entry types (verified)
`@article` (journals, 14), `@inproceedings` (conference/workshop/shared-task, 22 generated), `@incollection` (book chapters, 4), `@proceedings` (edited volumes, 2 generated), `@techreport` (reports/deliverables, 4), `@misc` (arXiv-only preprints, 5). ACL Anthology papers link the canonical Anthology `.bib` rather than a generated entry. No book chapter or conference paper is emitted as `@misc`.

## 6. Usability improvements
- One-paragraph, accurate introduction (the "Selected and recent" wording is gone).
- Search box, **Year** filter, **Type** filter (professional labels), and a live **result count**.
- The list is grouped into four output categories with per-section counts and **Show more** progressive disclosure (12 shown per section by default); nothing is rendered fully expanded.
- Compact cards: title, authors (long lists abbreviated visually), venue, year, type badge and source links; abstracts and BibTeX remain collapsed.
- Repeated "More in [theme]" removed; theme badges remain clickable.
- Source links follow the priority DOI → publisher/landing → ACL Anthology.

## 7. Event vs publication year
- *Machine Translation in the Covid Domain… for LoResMT 2021*: venue/event year set to **2021**, with the **arXiv deposit (2024)** shown separately. (Flagged to confirm the ACL Anthology LoResMT proceedings link.)

## 8. Research-output separation and counts
The list now distinguishes: **Peer-reviewed publications**, **Preprints**, **Edited proceedings**, and **Technical reports & project deliverables**, and displays both headline counts.
- **Peer-reviewed publications: 63**
- **Total research outputs: 77** (63 peer-reviewed + 5 preprints + 5 edited proceedings + 4 reports/deliverables)

## 9. Records still requiring manual verification (20)
All are added and displayed but a field cannot be fully confirmed from an authoritative source without you. Categories:
- **Project deliverables / notebook papers** (grey literature, no peer-reviewed DOI): ITFLOWS D5.3, ITFLOWS D3.3, TRECVid 2016 and 2017 participation.
- **Non-authoritative host links** to confirm at the publisher/Anthology: the two CICLing/Arabic-UGC papers, the metagenomic-platform BIBM 2019 paper, the IJCLA sentiment paper, PBML sentiment-polarity paper.
- **Abstract/presentation-only** (CLIN 29/30): Dialect-Aware Tokenisation; Sentiment Preservation.
- **Duplicated source link/pages in the CV** (two CERC-2020 entries; the 2013/2014 multimodal-corpora pair).
- **No identifier in source:** Decision-Level Multimodal Sentiment (CICLing 2018/LNCS); OCR Error Correction (CICLing 2015); TALN 2012.
- **Event-year confirmation:** LoResMT 2021 proceedings link.

## 10. Theme assignments to confirm (lower confidence — not changed)
Themes were assigned from verified content, not titles alone, and were **not** adjusted to balance counts. A few are lower-confidence and worth a human check (leave or retag as you prefer):
- TRECVid VTT participation (2016, 2017) — currently `multilingual`; video-to-text retrieval has only a weak multilingual link.
- *Affective Analytics… Stock Market Forecasting* (2021) and *Online News Analysis… Market Prediction* (2020) — currently include `trustworthy`; these are applied forecasting and could be `hcai`/`innovation` instead.
- *Detecting Sarcasm in News Headlines* (2020) — `trustworthy`+`hcai`; arguably `hcai` only.

## 11. Validation
Regenerated and re-verified: publications page, public API, timeline, analytics, knowledge graph, Ask Me index, structured data (`ScholarlyArticle`/`Book`), and BibTeX. Counts are consistent at **77** across `data`, API, analytics and Ask Me index. Build passes (29 pages, 0 broken links); the full test suite passes, including the new publication-integrity tests.

## Final numbers
- **Peer-reviewed publications: 63**
- **Total research outputs: 77**
- **Build:** green (29 pages, 0 broken links, 0 missing assets) · **Tests:** all pass.
