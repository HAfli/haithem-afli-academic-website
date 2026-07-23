# Research Communication Strategy (Release 1.3)

Turns the verified record into a credibility-first narrative. Everything below is evidence-based and traces to `data/*.json`, the DAM registry (`reports/dam-registry.json`) and the verified news item. Nothing is invented. Where evidence is absent it is listed under "Missing strategic assets", not fabricated.

**Guiding question applied throughout:** *what convinces a first-time visitor of international impact?* — international keynotes (Brazil, Wuhan), Horizon Europe projects, a European patent, national research-centre co-leadership (Rinn AI), ADAPT PI, 77 publications incl. flagship *ACL venues, and national media coverage.

---

## 1. Communication Impact Score (CIS) — replaces the quality score
A transparent 0–100 weighting applied to every event in the DAM registry and to milestones:
- **Category base** (workshop-organisation/keynote > presentation > public-engagement/HAI > seminar).
- **Visual quality** (derived from prior quality assessment).
- **Linkage** to a research theme/publication/grant (+).
- **Recording present** (+12) and **slides present** (+8).
- **International profile** keywords (Wuhan, Brazil, Kuwait, US Naval, DCU, Horizon EU, PoliticalNLP, keynote) (+).
- **Recency** (2024+ > 2021+).
CIS now drives homepage visibility and timeline prominence. Top-scoring events include Wuhan University (2025), Brazil Summer School keynote (2024), the PoliticalNLP workshops, DCU invited talks and ITFLOWS.

## 2. Top 25 career milestones
Encoded in `data/milestones.json` (21 headline milestones + chapter narratives; extendable to 25 as more are verified). Examples: PhD (2014); founding the HAI group (2018); ITFLOWS/Horizon 2020 (2020); IEEE Senior Member (2021); PoliticalNLP series (2022–2024); adaptNMT/adaptMLLM (2023); European patent WO/2024/227944 (2024); EC/REA expert (2024); GenDAI (2024); "The Language of Life" keynote, Brazil (2024); Cork Independent coverage (2025); EMNLP/EACL/IWSLT papers (2025–2026); **Rinn AI Institutional Co-Lead (2026)**; ADAPT PI & MTU Lead.

## 3. Top 20 homepage highlights
The homepage now leads with an **International highlights** band (top 8 milestones by CIS) before themes and featured content; the full ordered set lives in `milestones.json` and can be expanded to 20. Each highlight links into the Research Journey.

## 4. Research Journey (new central section)
`journey.html` — six evidence-linked chapters: **Foundation → Building Research Excellence → International & European Expansion → Human-Centred AI & Research Leadership → Research Impact & Recognition → Current & Future Vision.** Every milestone in a chapter links to its publication, project, theme or news. This is the narrative spine the brief asked for.

## 5. Homepage redesign
Implemented: hero (who/what) → **International highlights** → research themes → featured projects → latest publications → research intelligence → media → groups → talk → news → contact. Credibility now appears above the fold; implementation-oriented language removed in Release 1.0.

## 6. Research communication strategy (this document)
The connective tissue: publications ↔ conferences ↔ talks ↔ slides ↔ media ↔ news ↔ grants ↔ projects ↔ students ↔ themes, navigable via the knowledge graph and the Research Journey.

## 7. Event Page template (design)
For each *approved* major event, a single integrated page (generated from a future `data/events.json` keyed to a milestone id):
`Executive summary · Scientific contribution · Why it mattered · Audience/Host/Location/Date/Conference · Research theme · Publication · Project · Grant · Collaborators · Students · Slides · Poster · Video (with transcript) · Gallery · News · LinkedIn/X/Facebook (curated) · Downloads · Timeline position · Knowledge-graph neighbours · Related work · SEO/structured data/accessibility.`
Event Pages **merge** all evidence for one event (slides + photos + social + news) — never duplicate. They render only when the underlying assets are approved (copyright/consent). Not auto-generated in this release because publishing the `content/` assets requires your approval.

## 8. Updated knowledge graph
`site/data/knowledge-graph.json` now includes **milestones (20)** and **news/media (5)** as first-class nodes alongside publications, projects, talks, people, themes and students, with theme edges. This graph powers Ask Me's "related records" and the recommendation design below.

## 9. Media strategy (photography / video)
- **Photography:** publish only identity-strengthening images (keynotes, panels, conference, awards, HAI group) — consent required for identifiable people (2 photo folders flagged).
- **Video:** prioritise keynotes, conference talks and public lectures; self-host with **transcript, chapter markers, thumbnail, summary, keywords, speaker metadata** (media.json schema already supports transcript/captions/thumbnail; the richer fields extend it). 17 real recordings exist in `content/` and can be prepared on approval.

## 10. Updated DAM registry
`reports/dam-registry.json` (private) now carries `communication_impact_score` per asset (quality score removed) across the ~90 selected events, plus the rejected/manual-review classifications from Release 1.2.

## 11. Social-media ingestion workflow
`content/social-curated/{linkedin,x,facebook,slideshare}/` + `README.md` schema: you add real public posts as small front-matter files; each is associated (by `event`/`related` id) to a milestone/publication/project/theme and **merged into the relevant Event Page** — no standalone social pages, nothing scraped, only `approved` items displayed.

## 12. Timeline redesign
The timeline now interleaves **verified milestones** (keynotes, grants, awards, media, leadership, patent) with publications, each linking into the Research Journey chapter — making the timeline a navigation spine rather than a list.

## 13. Recommendation engine (design + foundation)
The knowledge graph (now including milestones/news/talks) is the substrate. Recommended implementation: for any publication/project/event, surface **related talks, slides, projects, grants, students, media, news and collaborators** by shared theme + shared author + graph adjacency. Ask Me already returns "related records" from this graph; a per-page "Related" strip is the next incremental step (client-side, reads `knowledge-graph.json`).

## 14. Missing strategic assets (verified gaps — not fabricated)
- **Professional portrait** and keynote/stage photography with consent (would strengthen the hero and Event Pages).
- **Conference talk slides/video** for several flagship papers (EMNLP/EACL/IWSLT) — not found in `content/`.
- **SlideShare export** — profile is bot-protected; provide PDFs to include.
- **Curated LinkedIn/X/Facebook posts** — none supplied yet (workflow ready).
- **A NotebookLM/overview video** introducing the research (brief suggests one).
- Official **MTU staff-profile URL** to link.

## 15. Final recommendations
1. Approve the top ~15 events (by CIS) to become Event Pages with real slides/recordings + transcripts.
2. Supply a professional portrait and 4–6 consented keynote photos.
3. Add curated LinkedIn/X posts for the biggest milestones (Rinn AI, patent, Brazil/Wuhan keynotes, Cork Independent).
4. Provide SlideShare PDFs for the strongest decks.
5. Then enable the per-page recommendation strip and generate Event Pages from `data/events.json`.

**Success-criteria status:** the site now opens with international evidence, offers a coherent Foundation→Future narrative, and interlinks research, projects, funding, talks, media and impact through a verified knowledge graph — the official digital presence of an internationally active researcher, built from evidence rather than an archive.
