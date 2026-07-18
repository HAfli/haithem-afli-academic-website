# Research Assistant (Release 1.3)

A trustworthy, multilingual **Research Assistant** over the website's verified records. It is built to reinforce confidence rather than maximise fluency: every answer is a set of real records with citations, a confidence score, and an explanation of *why* it was returned. It never behaves like a generic chatbot, and it cannot fabricate, paraphrase incorrectly, or hallucinate — because it does not generate text at all.

## Design decision: grounded retrieval, not generation

The assistant is a **client-side grounded retrieval system**, not a generative language model.

- **No LLM, no server, no network calls at query time.** The page ships a small JavaScript retriever (`site/assistant.js`) and a static index (`site/data/assistant-index.json`). Retrieval happens entirely in the visitor's browser.
- **It surfaces only indexed, verified content.** The index is generated at build time from the same canonical JSON that produces the public pages (`publications.json`, `projects.json`, `talks.json`, `supervision.json`, `profile.json`). If a fact is not in the verified record, the assistant cannot say it.
- **GitHub-Pages-compatible.** No backend is required; it is a static site.
- **Private by construction.** No cookies, no tracking, no storage, no telemetry. The query stays in the browser for the session only. This is stated to the user on the page.

This directly satisfies the Human-Centred AI / no-fabrication constraints: a system that only ranks and cites real records is structurally incapable of inventing deadlines, papers, funding, citations, collaborators or claims.

## What is generated at build time

`scripts/build.py::build_knowledge_index()` writes two files into `site/data/`:

- **`assistant-index.json`** — the retrieval index: one `doc` per publication, project, talk, completed doctoral supervision, and site section, each with a title, canonical URL, type, themes, and a lowercase searchable `text` field. Also carries `theme_names` and the cross-language `glossary`, plus the build date.
- **`knowledge-graph.json`** — a typed node/edge graph (themes, publications, people, projects, talks, students) used to surface *related records* alongside an answer. Nodes carry a type and a link to the authoritative record.

Both are regenerated on every build, so they never drift from the published pages. Withheld/unverified items (`WITHHELD` notes) are excluded, exactly as on the public pages.

## How a query is answered (`site/assistant.js`)

1. **Tokenise** the query (stopwords in several languages removed).
2. **Cross-language expansion.** A curated glossary maps key terms in English, Arabic, French, Spanish, German, Italian, Turkish, Russian, Irish, Persian and Hebrew to language-neutral theme IDs (e.g. `تقييم`, `évaluation`, `meastóireacht` → *Evaluation Science*). Matched theme names are added to the query, so a question in Arabic or Irish reaches the same records as English. **The glossary is a fixed, human-curated term map — no machine translation is performed and no translated content is published.**
3. **Rank** every indexed doc by how many query terms (exact, plus a conservative prefix match) appear in its text.
4. **Cite.** The top records are shown, each linking to its authoritative source, with type, year, matched terms, and a relative confidence (high/moderate/low).
5. **Explain.** A "Why these answers?" panel states the ranking basis; each result shows the terms it matched and, in transparency mode, the raw score and percentage.
6. **Related records.** Records sharing the top hit's themes are shown as a small knowledge-graph view.

## Honesty: the "I don't know" fallback

If no record clears a minimum relevance threshold, the assistant does **not** guess. It says plainly that it has no confident answer from the verified records, and points the visitor to the most relevant sections (publications, research themes, projects) or to the contact page. This is the evidence-first behaviour required by the brief: *if uncertain, say so clearly.*

## Intent modes

Audience chips (prospective PhD, industry partner, journalist, prospective MSc, academic collaborator) pre-seed a relevant query and surface curated quick links to the right sections. They shape *navigation*, not facts — the underlying answers are still retrieved from the same verified index.

## Transparency / benchmark mode

The "Transparency mode" checkbox exposes the raw retrieval score and normalised percentage for each result, so the ranking is fully inspectable. There is no hidden model and no opaque scoring.

## Accessibility (WCAG 2.2 AA intent)

- Results region is an `aria-live="polite"` landmark; the input has an associated label.
- Fully keyboard operable (form + buttons); intent chips expose `aria-pressed`.
- RTL-aware styling for Arabic/Persian/Hebrew queries.
- Respects `prefers-reduced-motion`.
- Works without JavaScript degraded gracefully via a `<noscript>` pointer to the same records.

## Optional extension points (config-only, not enabled)

The architecture leaves room for optional enhancement **without changing the grounding guarantee**:

- **Embeddings / semantic retrieval.** The `text` field per doc could be replaced or augmented with precomputed embedding vectors written into the index at build time; the client ranker would use cosine similarity instead of term overlap. This remains retrieval over verified records — still no generation.
- **LLM adapter.** If a hosted model were ever introduced (e.g. to phrase a one-line summary), it must be constrained to *only* rephrase retrieved, cited records, must never add facts, and must be disabled by default. This would be a documented config flag, not a default behaviour, and is **not implemented** here.

Neither is enabled: the shipped assistant is deterministic, offline, and free of any model.

## Limitations

- Retrieval is lexical (term overlap) with cross-language glossary expansion; it is not semantic embedding search. Very indirect phrasings may under-retrieve. This is a deliberate trade for zero dependencies, full transparency, and no hallucination.
- The glossary covers key research terms, not general vocabulary; unusual terms fall back to English matching.
- Coverage is exactly the site's records — by design. For anything outside them, the assistant refers the visitor to contact Dr Afli.

## Files

- `scripts/build.py` → `build_knowledge_index()`; `ASSISTANT_JS`; `assistant` page in `render()`.
- `site/data/assistant-index.json`, `site/data/knowledge-graph.json` (generated).
- `site/assistant.js` (generated from `ASSISTANT_JS`).
- Public page: `assistant.html` (linked from the primary navigation).
