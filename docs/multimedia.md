# Multimedia & Research Communication (Release 1.2)

Adds accessible, privacy-preserving multimedia to the site — photographs, talk recordings, audio/podcasts, slides and posters, and per-publication graphical abstracts — plus the research-communication draft workflow. **Nothing is fabricated and nothing is auto-published.** Media appears only after a real file (or official link) exists and a human marks it approved.

## Principles

- **No placeholders.** A media item renders only when its asset exists and `status` is `approved`. Draft/example entries never appear on the public site (test-guarded).
- **Accessibility first.** Every video or audio item **must** have a transcript, or it will not render. Images require alt text. Captions are supported via `<track>`.
- **Privacy.** Prefer self-hosted files; external recordings are shown as a click-out link (opens in a new tab), never an auto-loading third-party tracking iframe. No trackers (test-guarded).
- **Single source of truth.** The registry is `data/media.json`; publications/talks reference media by id.

## The media registry — `data/media.json`

Each entry:

| Field | Meaning |
|---|---|
| `id` | Stable slug (avoid the `example-` prefix, which is ignored). |
| `kind` | `video` · `audio` · `slides` · `poster` · `graphical-abstract`. |
| `title`, `date`, `description` | Display metadata. |
| `status` | `draft` (default) or `approved`. Only `approved` renders. |
| `file` | Path to a self-hosted asset (e.g. `downloads/talk.mp4`, `assets/img/…`). Must exist at build time. |
| `link` | Official external URL (used when self-hosting isn't possible). |
| `thumbnail` | An image `id` from `gallery.json` used as poster/preview. |
| `transcript` | **Required for `video`/`audio`.** Path or URL to a transcript. |
| `captions` | Optional `.vtt` captions for `<video>`. |
| `related` | A publication/talk/theme id this media belongs to. |
| `license`, `alt` | Licence URL; alt text for images. |

## How to add media

1. Put the real file in the repo (self-hosted: `downloads/` or `assets/`), or obtain an official link.
2. Prepare a transcript for any recording (mandatory).
3. Add an entry to `data/media.json` with `status: "approved"` and the required fields.
4. Rebuild. The item appears in the relevant section of the **Media** page.

**Talk recording (self-hosted):** `kind: "video"`, `file: "downloads/keynote-2026.mp4"`, `transcript: "downloads/keynote-2026-transcript.txt"`, optional `captions` and `thumbnail`.

**Podcast/audio:** `kind: "audio"`, `file` or `link`, plus `transcript`.

**Slides/poster:** `kind: "slides"` or `"poster"`, `file` (PDF) or `link`, optional `thumbnail`.

**External recording (privacy-preserving):** omit `file`, set `link` to the official page; it renders as a click-out link, not an embed. A transcript is still required.

## Graphical abstracts (per publication)

Add a `graphical_abstract` field to a record in `data/publications.json`, set to an image `id` present in `gallery.json` (processed through the image pipeline). It renders as a small figure on that publication's card — **only if the image asset exists**. No abstract image is invented.

## Photographs gallery

The existing 22 images render in an accessible, keyboard-operable gallery with a category filter and a live count. Every image keeps its alt text and caption. Add photos via `assets/source/` + `scripts/process_images.py` (see `docs/image-policy.md`), tagged with a `category` in `gallery.json`.

## Research communication (draft workflow)

Audience-tailored communication assets (plain-language summaries, elevator pitches, social drafts, teaching summaries, media kits) are generated as **review drafts** by:

```
python3 scripts/admin_sync.py --communication
```

Drafts land in `reports/communication/` and `reports/media-kits/` (private, `DRAFT` labelled); a readiness matrix is written to `reports/communication-dashboard.md`. A public **Spotlight** page appears only after a human approves an asset in `data/communication.json` (`status: "approved"`) — see `docs/research-communication.md`. Nothing is published externally without approval.

## Accessibility & privacy checks (automated)

`tests/test_site.py` enforces: approved audio/video must carry a transcript; approved media must have a file or link; example/draft entries never reach the public gallery; the gallery exposes its category filter and grid; and no third-party iframe is embedded on the gallery.
