# Publication Enrichment Report — 2026-07-18

Consolidation pass over the 27-publication corpus. Metadata was verified and enriched using **official sources only** (Crossref DOI registry, arXiv, ACL Anthology, and — for one venue confirmation — the CEUR-WS proceedings and the RecSys-in-HR'25 programme). **No metadata was invented.** Where a field could not be verified, it was left empty and is listed under "Remaining gaps".

## Outcome

- **27 / 27** publications now resolve to an authoritative URL (was 15 / 27).
- **11** publications carry a verified DOI (all previously CV-sourced entries now have one; the 12th non-anthology item is a CEUR-WS workshop paper with no DOI — see below).
- **15** ACL Anthology papers use their canonical `aclanthology.org` URLs (authoritative; ACL serves their BibTeX and, where minted, DOIs).
- **12** publications gained a verified `publisher`; **3** gained a verbatim `abstract` (only where the publisher deposited one in Crossref).
- **0** duplicate titles or ids; **0** publications without a research theme.

## Verified DOIs added (Crossref, retrieved 2026-07-18)

| Publication | DOI | Publisher | Venue |
|---|---|---|---|
| adaptNMT: Open-Source, Language-Agnostic NMT | 10.1007/s10579-023-09671-2 | Springer | Language Resources and Evaluation |
| adaptMLLM: Fine-Tuning Multilingual LMs | 10.3390/info14120638 | MDPI | Information 14(12):638 |
| Performance and Information Leakage in Splitfed / MHSL | 10.3390/mps5040060 | MDPI | Methods and Protocols 5(4):60 |
| Advancing Earth Observation (survey) | 10.1080/22797254.2025.2567921 | Taylor & Francis | European Journal of Remote Sensing 58(1) |
| Building & Using Multimodal Comparable Corpora | 10.1017/s1351324916000152 | Cambridge UP | Natural Language Engineering 22(4):603–625 |
| The Influence of Iconicity (Sign Language) | 10.1007/978-3-031-70239-6_16 | Springer Nature | NLDB 2024 (LNCS), 226–240 |
| Stool & Ruminal Microbiome (Nelore cattle) | 10.3389/fgene.2022.812828 | Frontiers | Frontiers in Genetics 13 |
| Putative Mobilized Colistin Resistance (gut) | 10.1186/s12866-021-02281-4 | Springer Nature (BMC) | BMC Microbiology 21 |
| From Reads to Reports (GFM genomic platform) | 10.1109/bibm66473.2025.11356528 | IEEE | IEEE BIBM 2025, 7207–7213 |
| Enabling All In-Edge Deep Learning (review) | 10.1109/ACCESS.2023.3234110 | IEEE | IEEE Access 11 |
| Predicting Country Instability (preprint) | 10.48550/arXiv.2411.06639 | arXiv | arXiv 2411.06639 (2024-11-11) |

## Verification notes / disambiguation

- **Towards Explainable Job Title Matching.** A Crossref title search surfaced an ACL 2026 System-Demonstrations DOI (`10.18653/v1/2026.acl-demo.52`). This was **rejected as a false match**: the paper is confirmed as **RecSys-in-HR'25** (CEUR-WS Vol-4046; authors Zadykian, Andrade, Afli), with an arXiv preprint (2509.09522). The record's venue was therefore left unchanged; the arXiv link was added. No DOI assigned (CEUR-WS workshops typically mint none).
- **Country Instability** is an arXiv-only preprint; the DataCite arXiv DOI and abstract page were used. Status remains `preprint`.
- **Colistin resistance:** Crossref's top hit was the bioRxiv preprint (`10.1101/2020.12.31.424960`); the **published BMC Microbiology** DOI was used instead. The preprint abstract was **not** copied to the published record to avoid version drift.
- **Abstracts** were added only for the three papers where the publisher deposited a machine-readable abstract in Crossref (adaptMLLM, Splitfed/MHSL, Multimodal Comparable Corpora). All are stored verbatim.

## Enrichment now surfaced on the site

Each publication entry now renders, where available: an authoritative title link, a links row (DOI · PDF · arXiv · BibTeX), clickable research-theme tags (to `research.html#<theme>`), a collapsible verbatim **Abstract**, a generated **BibTeX** block (deterministic from verified fields, for non-Anthology items), and a "More in this theme" cross-link. Structured data (`ScholarlyArticle`) was extended with `abstract`, `publisher`, and DOI `sameAs`/`identifier`.

## Remaining gaps (reported, not invented)

- **DOI:** 1 non-anthology item (Job Title Matching — CEUR-WS, no DOI exists) and 15 ACL Anthology papers (authoritative anthology URLs present; DOIs not added to avoid synthesising identifiers for older venues).
- **Abstracts:** 24 publications have no verbatim abstract in Crossref. These can be added later only from an authoritative full text — not paraphrased.
- **Explicit keywords:** not populated. Research-theme tags serve as controlled keywords; free-text keywords would need an authoritative source (author-supplied or publisher-deposited) and are left empty.
- **Related datasets / software / media / NotebookLM briefings:** not yet linked per-publication; these require human-verified mappings (e.g. adaptNMT/adaptMLLM → their open-source repos) and are deferred to avoid unverified links.

## Method (reproducible)

Queries were issued to `https://api.crossref.org/works?query.bibliographic=...` (polite pool, `mailto` configured) and cross-checked against arXiv/CEUR-WS where relevant. Enrichment was applied by id to `data/publications.json`; the site, knowledge index, public API and CV regenerate from it on build. No field was written without a matching authoritative record.
