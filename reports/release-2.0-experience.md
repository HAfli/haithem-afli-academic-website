# Release 2.0 — Research Experience & Thematic Navigation (Implementation)

Presentation and experience upgrade — implemented, not planned. Build green (**56 pages**), full test suite passes, private assets remain unpublished, nothing fabricated.

## 1. Design system (Phase 1)
- **Accessible dark mode** via `prefers-color-scheme` — the whole palette is CSS variables (`--ink/--muted/--line/--accent/--bg/--tag/--surface/--accent-soft`), so every page adapts automatically; `color-scheme` set for native form controls.
- Consistent **card system** (role/media/summary cards) with subtle hover elevation, gated behind `prefers-reduced-motion`.
- Tightened typography (heading letter-spacing, reading width), spacing, and **mobile navigation** (denser nav + padding at ≤640 px).
- New reusable components: audience CTA buttons, summary cards, theme hero, filter chips.
- Restrained by design: no gradients, no decorative AI artwork, no gratuitous animation.

## 2. Event Pages (Phase 2)
Structure unchanged (per instruction); presentation improved. Where materials are still private, a concise "available on request / prepared with transcripts and permissions before publication" message replaces empty sections. Empty sections are hidden automatically.

## 3. Research Theme pages (Phase 3) — NEW ×6
`theme-{hcai,multilingual,trustworthy,evaluation,bio,innovation}.html`: overview, why it matters, featured events, related projects, publications (by theme), milestones, and news — all from verified data, sections hidden when empty. Linked from the Research page and homepage. (Arabic NLP / AI-for-Health / low-resource are represented within multilingual and bio rather than as unsupported standalone pages.)

## 4. Graphical research summaries (Phase 4)
Implemented as structured **summary-card** components (problem → approach → contribution) usable on theme pages — structured, not decorative; no invented metrics. (Extendable to the 5 flagship outputs on approval.)

## 5. Audience pages (Phase 5) — NEW ×4
`prospective-phd.html`, `collaborate.html`, `industry.html`, `for-media.html` — tailored entry points from verified evidence (no funding implied; no unapproved photos; media page offers only the approved CV download).

## 6. Research Vision (Phase 6) — NEW
`research-vision.html` — a restrained philosophy page (multilingual, cultural reasoning, trustworthy evaluation, human-centred AI, low-resource languages; how HAI/ADAPT/Rinn AI/GenDAI contribute; future directions), linking to theme pages and the journey.

## 7. Timeline (Phase 8)
Interactive **filter chips** (Publications · Talks · Projects & grants · Leadership · Recognition · Media) with a live count and empty-year hiding; the Research Journey remains the primary narrative.

## 8. Navigation & flow
New flow wired end-to-end: **Vision → Research Journey → Milestones → Theme pages → Event Pages → Publications → Projects → Media**. "Vision" added to the primary nav; a "Find your path" audience band added to the homepage.

## 9. Accessibility report (Phase 11 / deliverable 13)
- Automated checks pass on all 56 pages: single `h1`, skip link, one `main`, `lang`, alt text on every image, valid JSON-LD, keyboard-operable native controls (filters/chips/buttons), `aria-live` status regions, `aria-pressed` on toggle chips.
- Dark mode uses higher-contrast ink/accent values; focus-visible outlines retained; motion gated by `prefers-reduced-motion`.
- Email remains obfuscated; no third-party trackers or iframes.
- **Manual follow-up:** verify colour-contrast ratios of the dark palette with a contrast tool; add captions to any future video.

## 10. Responsive design report (deliverable 14)
- Fluid layout with responsive image `srcset`/`sizes`, `loading="lazy"`, explicit dimensions (no layout shift); hero uses `fetchpriority`.
- Nav, cards and grids reflow with flex/grid; summary grid collapses to one column and nav densifies at ≤640 px.
- No fixed-width containers; reading width capped for legibility. Static site, ~40 KB API, cache-friendly.

## 11. Media review package (Phase 10)
`reports/media-review-package.md` (private) — per-asset review sheet for the six highest-value asset groups (Brazil/Wuhan keynote decks, keynote photos, recordings, PoliticalNLP slides, ITFLOWS materials). No file published; approval flow documented.

## 12. Social workflow (Phase 9)
Existing user-assisted ingestion retained and documented (templates + README from Release 1.3); no scraping; only `approved` items eligible; posts merge into Event Pages.

## Deliverables map
1 design system ✓ · 2 homepage (audience band + highlights) ✓ · 3 Event Pages polish ✓ · 4 Research Vision ✓ · 5 Theme pages ✓ · 6 Audience pages ✓ · 7 graphical summaries (component) ✓ · 8 KG explorer (Ask Me + theme pages; further explorer view deferred) ◐ · 9 research map (deferred — needs verified geo-coordinates) ○ · 10 timeline filters ✓ · 11 social workflow ✓ · 12 media review package ✓ · 13 accessibility report ✓ · 14 responsive report ✓ · 15 modified files ✓.

## Modified / new files
- **scripts/build.py** — dark mode + design system CSS; 6 theme pages; 4 audience pages; Research Vision; timeline filters (+`timeline.js`); homepage audience band; nav "Vision"; theme-page links.
- **data/events.json, data/milestones.json** — (Release 1.3, on branch).
- **.gitignore** — raw content/ excluded.
- **reports/** — media-review-package.md, release-2.0-experience.md (this file); dam-registry.json states.
- Generated: `site/*.html` (56 pages incl. 11 new), `site/style.css`, `site/timeline.js`.

## Not done (honestly)
- **Interactive research map** — deferred: would need verified geo-coordinates for events; no fabrication.
- **Full Knowledge-Graph explorer UI** — Ask Me + theme pages cover grounded exploration; a dedicated graph-visualisation view is a later step.
- Any media file publication — awaits your approval via the review package.
