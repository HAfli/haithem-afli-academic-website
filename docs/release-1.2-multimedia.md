# Release 1.2 — Multimedia & Research Communication

Branch: `release-1.2-multimedia` (v1.0 tag untouched). Framework-first: accessible, privacy-preserving multimedia that renders only real, human-approved assets — no placeholders, no fabrication, nothing auto-published.

## Delivered

**Multimedia registry (`data/media.json`).** Unified, draft-gated schema for videos, audio/podcasts, slides, posters and graphical abstracts, with governance flags (no auto-publish, transcript required for A/V, no third-party trackers, prefer self-hosted). Seeded with one documented example (ignored).

**Media page (accessible + privacy-preserving).**
- Photographs: the 22-image gallery is now an accessible, keyboard-operable grid with a category filter and a live count; alt text and captions retained.
- Talk recordings / audio: self-hosted `<video>`/`<audio>` with `preload="none"`, optional caption tracks, and a mandatory transcript link; external recordings render as a click-out link (opens in a new tab), never an auto-loading tracking iframe.
- Slides & posters: download links with optional thumbnails.
- Every section renders **only approved** items; with none yet, an honest note explains that recordings, audio, slides and graphical abstracts appear as they become available. No placeholders.

**Graphical abstracts (per publication).** Publications may carry a `graphical_abstract` image id; it renders on the card **only if the image asset exists**.

**Research-communication workflow (active).** `admin_sync.py --communication` regenerates audience-tailored **draft** assets (plain-language summaries, pitches, social drafts, teaching summaries, media kits) into private `reports/`, with a readiness dashboard. Public Spotlights render only for human-approved assets in `data/communication.json` (currently none). Nothing is published externally without approval.

**Accessibility & privacy (test-guarded).** Approved audio/video must have a transcript; approved media must have a file or link; example/draft entries never reach the public gallery; the gallery exposes its filter and grid; no third-party iframe on the gallery. Global checks (alt text, no trackers, keyboard-accessible native controls) continue to apply.

**Documentation.** `docs/multimedia.md` (registry schema, add-media workflow, graphical abstracts, privacy, accessibility) and this summary; `docs/research-communication.md` remains the communication reference.

## How to populate (no code needed)

1. Add a real file (self-hosted under `downloads/`/`assets/`, or an official link) and a transcript for any recording.
2. Add an `approved` entry to `data/media.json` (or a `graphical_abstract` id to a publication).
3. Rebuild — the item appears on the Media page (or publication card).

## Build & tests

Build green (29 pages, 0 broken links, 0 missing assets); full test suite passes, including the new multimedia governance checks.

## Not in scope / deferred

- No real recordings, audio, slides or graphical-abstract images exist yet — the framework awaits assets.
- The 20 unresolved publication records remain documented and untouched.
