# Academic Digital-Twin Schema (v2, incremental)

## Principle
The website is a **renderer**, not the long-term owner of academic facts. Data files are evolving toward a graph-compatible entity model so that facts, evidence, provenance and relationships live independently of any page. This is introduced incrementally — no risky rewrite before deployment.

## Canonical entities (stable ID prefixes)
`person:` · `pub:` · `project:` · `grant:` · `role:` · `institution:` · `student:` · `talk:` · `event:` · `news:` · `media:` · `award:` · `software:` · `dataset:` · `theme:`

## Entity attributes (target shape)
```
id · type · attributes{} · relationships[{predicate, target_id}]
· evidence[{source, url, tier}] · provenance · confidence(established|supported|tentative|speculative)
· verification_status · valid_from · valid_until? · approval_history[] · change_history[]
```

## Relationships (examples)
`pub authored-by person` · `pub presented-at event` · `news announces pub` · `person leads project`
· `project funded-by grant` · `media depicts event` · `student supervised-by person` · `pub in-theme theme`

Worked chain (already wired in `data/news.json`):
`news:news-iwslt2026 → pub:2026.iwslt-1.6 → person:pournima-sonawane → theme:multilingual → event:iwslt-2026`

## What is implemented now (v2.0, non-breaking)
- Stable `id` on every publication (`pub:<anthology-id>` or `pub:<year>-<slug>`).
- Stable `id` + `related_entities[]` on every news item (graph edges to pubs/people/themes/events).
- `social-content.json` links each (future) post to entities via `related_entities`, never as isolated news.
- `themes` already carry stable ids used across pages.

## Migration plan (v2.1 → v2.2, post-deployment)
1. v2.1: extract `people`, `events`, `institutions` into their own registries with ids; back-reference from pubs/news/supervision (currently inline).
2. v2.1: add `evidence[]`+`confidence` to project/grant records (mirrors the ResearchOS confidence vocabulary) so funding entries carry machine-readable verification state, not just prose notes.
3. v2.2: single `entities.json` graph export generated from the per-type files by the build script; the site renders from the graph; a validator checks referential integrity (every `related_entities` target exists) — the same pattern as the ResearchOS `lint_registry.py`.
4. v2.2: optional read-only JSON-LD `@graph` emission for machine consumers.

## Integration with ResearchOS
The public site is downstream of, and must never expose more than, the ResearchOS registries. The digital-twin schema deliberately mirrors ResearchOS conventions (stable ids, typed relationships, confidence vocabulary, provenance) so approved public facts can eventually be projected from the internal registries rather than maintained twice.
