# Social-Curated Ingestion Workflow

Manually curated professional social posts — **supporting evidence**, not standalone pages. You add real public posts here; the build associates them with the verified record (CV, publication, project, grant, conference, people, timeline, knowledge graph) and **merges** them into the relevant Event Page. Nothing is scraped; nothing is auto-published.

## Folders
- `linkedin/` · `x/` · `facebook/` · `slideshare/`

## How to add a post
Drop one small file per post (Markdown with front-matter, or JSON) named by date + slug, e.g. `2025-05-08-ai-crossroads.md`:

```yaml
---
platform: linkedin          # linkedin | x | facebook | slideshare
url: https://www.linkedin.com/posts/...      # the public permalink
date: 2025-05-08
title: Short title of the post
event: m-2025-corkindependent   # milestone/event id it enriches (optional)
related: { pub: "", project: "", grant: "", theme: "hcai" }
people: []                  # named collaborators (optional)
image: ""                   # local path to a saved image you have rights to (optional)
status: draft               # draft | approved  (only approved is ever displayed)
summary: One-line factual description.
---
Optional longer notes / verified quote.
```

## Rules
- **Public content only**, added by you — never scraped.
- A post **enriches an existing event**; it never creates a standalone social page.
- Only `status: approved` items are eligible for display, and only after the usual copyright/consent review.
- The same event across slides + photos + LinkedIn + X + Facebook + news merges into **one** Event Page (see `docs/research-communication-strategy.md` → Event Page template).

## Association (automatic, when wired)
On build, each approved post is matched — by its `event`/`related` ids — to a milestone, publication, project or theme, and linked from that Event Page and the knowledge graph. Unmatched posts are listed for manual review rather than shown.
