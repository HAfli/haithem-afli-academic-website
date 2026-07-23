# Private Media Review Package (Release 2.0)

PRIVATE — not published. A review sheet for the highest-value assets only, so you can approve public derivatives one by one. **No file is published yet.** All items are `staged-for-review` or `metadata-only` in the DAM registry.

For each asset: source · event · ownership · co-authorship · copyright · consent · recommended derivative · thumbnail · publish recommendation.

## 1. Brazil keynote — "The Language of Life"
- **Source:** `content/Presentations/2024/Brazil_Summer_School/Opening Talk/The_Language_of_Life_Haithem_Afli.pptx` (+ PDF).
- **Event:** `event-language-of-life-brazil` (Hologenomic Data Analysis Symposium, São Carlos, 2024).
- **Ownership:** Haithem Afli. **Co-authorship:** likely sole/lead; confirm any collaborator figures.
- **Copyright:** check for third-party genomics figures. **Consent:** n/a (no identifiable people if slides only).
- **Recommended derivative:** clean **PDF**; do not publish PPTX. **Thumbnail:** title slide.
- **Recommendation:** strong publish candidate after third-party-figure check.

## 2. Wuhan University — "The Language of Life"
- **Source:** `content/Presentations/2025/Wuhan_University/The_Language_of_Life_Haithem_Afli.pdf` (+ pptx).
- **Event:** `event-language-of-life-wuhan` (2025). **Factual check:** confirm exact date and host department.
- **Ownership:** Haithem Afli. **Copyright/consent:** as above.
- **Recommended derivative:** PDF; same deck as Brazil (one canonical asset, two venues). **Recommendation:** publish with Brazil as a shared deck.

## 3. Keynote / conference photographs (up to 6)
- **Source:** `content/HAI/2025/Pictures/`, `content/HAI/photos/`, and event folders.
- **Consent:** REQUIRED for identifiable people before any publication. **Ownership/photographer:** record per photo.
- **Recommended derivative:** web-optimised JPEG/WebP via `process_images.py`, EXIF-stripped, alt text.
- **Recommendation:** you select 4–6 that show keynotes/panels/conferences; confirm consent; then approve.

## 4. Strategic recordings (up to 3)
- **Candidates:** `content/Presentations/AI_Seminars/IBM_Dec_2019/GMT20191206-134254_NLP_Guest__1280x720.mp4`; McCarthy Summer School 2022 video; other event recordings (17 total found).
- **Copyright/consent:** verify no confidential/personal material visible; confirm co-presenter consent.
- **Recommended derivative:** MP4 (H.264) + **transcript (mandatory)** + poster + chapter markers.
- **Recommendation:** begin with at most 3 of the strongest, self-hosted with transcripts.

## 5. PoliticalNLP slides
- **Source:** `content/Presentations/2022/PoliticalNLP/PoliticalNLP_slides_Haithem.pptx` (+ 2024 folder).
- **Event:** `event-politicalnlp-series`. **Co-authorship:** workshop/community content — check third-party slides.
- **Recommended derivative:** PDF. **Recommendation:** publish after third-party-content check.

## 6. ITFLOWS presentation materials
- **Source:** `content/Presentations/2020/ITFLOWS/`, `content/Presentations/2020/MT_meeting_ITFLOWS/`.
- **Event:** `event-itflows`. **Copyright:** EU consortium material — confirm dissemination level (public vs restricted).
- **Recommended derivative:** PDF of public dissemination decks only. **Recommendation:** publish only clearly-public deliverable decks.

## Process
Approve an item → I generate the public derivative (PDF/thumbnail/transcript), set its DAM `state` to `approved-public`, add an `approved` entry to `media.json` and wire it onto the relevant Event Page. Nothing is published before that approval.
