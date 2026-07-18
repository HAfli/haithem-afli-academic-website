# Release 1.1 — QA, Accessibility, SEO & Performance Reports

2026-07-18 · Site: 25 pages, generated deterministically, deployed via GitHub Pages. All figures measured from the built `site/`.

## QA report
- Build: green — 25 pages, 132 image files, 1 PDF; **0 broken internal links, 0 missing assets, 0 missing image derivatives** (build validator + test suite).
- Duplicate content: none. Every page has a unique `<title>` and meta description (About given a distinct description in the launch audit).
- Orphan pages: none (analytics-map linked from hub + privacy).
- Reproducibility: two consecutive builds byte-identical except the build date.
- Mobile: responsive hero/grids/cards, viewport on every page, layouts wrap at 320px, intrinsic image dimensions (no layout shift).
- Homepage narrative reordered to: Hero → Research themes → Featured projects → Latest publications → Research Intelligence → Media → Groups/centres → Latest talk → Latest news → Contact. "Living" freshest items (newest publication, next verified deadline, latest talk) pull from existing data.
- Cross-linking: breadcrumbs on all sub-pages; homepage sections each link onward; Rinn/HAI/ADAPT distinction linked via `rinn-ai.html#ecosystem`.

## Accessibility report (target WCAG 2.2 AA)
- Structure: one `<h1>` per page; logical heading order; semantic `header/nav/main/footer`; breadcrumb `<nav aria-label="Breadcrumb">` with ordered list.
- Keyboard: skip-to-content link; native, keyboard-operable language selector (`<details>`); visible `:focus-visible` outlines; no keyboard traps; filters are progressive enhancement (site fully usable without JS).
- Screen readers: `aria-current` on active nav and breadcrumb; language selector labelled; every `<img>` has meaningful alt text (test-enforced); `lang` on the document and on non-English link labels.
- Contrast: body ink #1a1a1a on #fff (~14:1); accent #0b5c8a on #fff (~5.9:1); muted #5a5f66 (~6:1) — all ≥ AA. No colour-only meaning.
- Media: images carry captions/alt; no autoplaying media; no tracking pixels.
- Known limit: no video content yet, so transcript discoverability is N/A.

## SEO report
- Titles: unique per page, pattern "Page — Dr Haithem Afli".
- Descriptions: unique per page.
- Canonical: correct absolute URL under the repo prefix on every page.
- Open Graph: title/description/url/type/site_name on every page.
- Twitter Cards: `summary` with twitter:title/description on every page.
- Structured data: Person JSON-LD (structured `hasOccupation`/`affiliation`/`memberOf`) site-wide; **ScholarlyArticle @graph on Publications** (27 articles with authors, datePublished, isPartOf, url/DOI); ResearchProject on Rinn; **BreadcrumbList on every sub-page**. All JSON-LD validates.
- hreflang: en + x-default on every page.
- Sitemap: all 25 pages, correct URLs, `<lastmod>`. robots.txt allows all + correct Sitemap URL.
- Internal linking: hub-and-spoke; publications link to Anthology/DOI; projects link to official pages.
- No keyword stuffing; no deceptive SEO.

## Performance report (Lighthouse-style, static estimate)
- Total site 11.8 MB (dominated by 132 responsive image derivatives; individual pages are light).
- Average HTML page ~10 KB; single CSS file ~4 KB; 3 tiny JS files (filters, progressive enhancement); **no fonts loaded** (system font stack) → no font-blocking.
- Images: WebP + JPEG at thumb/medium/large with responsive `srcset` + `sizes`; **no image >400 KB**; `loading="lazy"` on all non-hero images; intrinsic width/height set.
- No render-blocking third-party scripts, no trackers, no cookies.
- Caching: static assets on GitHub Pages CDN with immutable content-hashed image names (stable filenames).
- Estimated Lighthouse: Performance high (static, no JS framework, lazy images), Accessibility high, Best Practices high (HTTPS, no console errors, rel=noopener), SEO high (metadata + structured data complete).
- Opportunity (optional, not blocking): AVIF derivatives could shave image bytes further; deferred to keep the dependency-free pipeline.

## Remaining recommendations (not launch-blocking; require data/credentials/review)
- Per-publication and per-theme standalone landing pages (rich abstracts, related work) — needs abstracts/permission; recommended as a content task, not fabricated.
- Live conference/funding records beyond EMNLP 2026 — populated by the CI sync from official sources.
- Connect a privacy analytics provider and a mailing provider to activate the visitor map and subscriptions.
- Reviewed translations for the 9 non-English languages.
