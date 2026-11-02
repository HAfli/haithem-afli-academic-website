# Release 3.2 — Teaching websites audit

Audit date: 2026-11-02. Both course websites are single-page applications that render with JavaScript, so their content was verified from their source repositories (READMEs and source files) as well as by HTTP status.

## Verified and integrated

| Title on academic site | Official title (source) | URL | HTTP | Association with Dr Afli | Status |
|---|---|---|---|---|---|
| Machine Learning in Biology — COMP9085 | *COMP9085 — Machine Learning and Foundation Models for Biology, Healthcare and Nutrition* | https://hafli.github.io/comp9085-ml-biology/ | 200 | Repository `HAfli/comp9085-ml-biology` (owner). README: "interactive course website for the MSc module COMP9085 at Munster Technological University, Department of Computer Science". Last pushed 2026-09-23. | **Integrated** |
| Building AI Confidence in the Gaeltacht Workplace | *Building AI Confidence in the Gaeltacht Workplace* | https://hafli.github.io/udaras-ai-course/ | 200 | Repository `HAfli/udaras-ai-course` (owner). README: training programme "delivered by Munster Technological University for Údarás na Gaeltachta, through the medium of Irish, at Campas Íosagáin"; facilitator Dr Haithem Afli. Last pushed 2026-10-20. | **Integrated** |

### Where they appear

- **Teaching page** (`teaching.html`): full resource cards in the new "Dedicated teaching websites" section, plus schema.org `Course` JSON-LD for both.
- **Homepage**: a compact Teaching section with both cards.
- **Theme pages**: COMP9085 under *AI for Healthcare, Biology & Genomics*; the Údarás course under *Multilingual & Culturally Aware AI* ("Related teaching").
- **Innovation & Industry page**: the Údarás course under "Knowledge transfer and AI literacy".

### Wording decisions you should check

- **Údarás course title.** Your brief suggested "Artificial Intelligence for Irish Language Communities – Údarás na Gaeltachta". The live site and its README use **"Building AI Confidence in the Gaeltacht Workplace"**, so the academic site uses that official title, with "Údarás na Gaeltachta" as the card's label. Change `data/teaching.json` if you prefer the other wording.
- **Status of the Údarás course.** It is described as "Professional training · delivered through Irish". The site does not call it accredited, a degree, or an MTU academic module; the source material does not say so. The README says it is delivered *by MTU for* Údarás na Gaeltachta, so the site says that and nothing stronger.
- **COMP9085 title.** The card heading is "Machine Learning in Biology", as requested. The full official module title appears in the description and in the JSON-LD `alternateName`. The site says "MSc module" without naming the programme, because the README does not say which MSc programmes take it.
- **Themes.** The Údarás themes listed (introduction to AI, generative AI and LLMs, everyday applications, AI safety and responsible use, AI literacy and the EU AI Act, AI and the Irish language) come from your brief and match the README's session structure and data files (`aiact.ts`, `research.ts`, Session 3 "An Ghaeilge i ré AI").
- **No outcome claims.** Neither course is described with impact or outcome claims.

## Other candidates examined (not published)

| Candidate | Finding | Decision |
|---|---|---|
| `HAfli/Lectures` (public repo) | Repository is empty; no Pages site (https://hafli.github.io/Lectures/ → 404) | Not added |
| `HAfli/Demo_Lectures` | Private repository | Not added (private) |
| `HAfli/haithem.afli` → https://hafli.github.io/haithem.afli/ | Live (200) but contains only the default GitHub Pages template README | Not added — consider archiving it so it doesn't surface in searches |
| `HAfli/CS231n` | Fork containing personal assignment solutions for a Stanford course | Not a teaching resource — not added |
| `HAfli/Coursera-ML` | Fork of personal course work | Not added |
| Repository data, docs and reports | No other `github.io` teaching URLs, module codes or course websites referenced | — |

**No additional teaching websites could be verified.** If you maintain others, such as Canvas-hosted modules or sites under another account, add them to `data/teaching.json` → `websites` with the same fields and rebuild.

## Not part of teaching (already on the site)

The research-programme sites https://hafli.github.io/cultural-adaptation-nlp/ and https://hafli.github.io/dynamic-nlp-evaluation/ are research websites, not teaching. Before this release they were injected by a hard-coded step in `deploy.yml`. They are now rendered from `data/profile.json` → `research_websites`.
