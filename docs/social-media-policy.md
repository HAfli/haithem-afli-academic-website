# Social-Media Integration Policy (LinkedIn & X only)

## Authorised sources
Only Dr Afli's professional **LinkedIn** account and **X** account (`@AfliHaithem`). No Facebook, Instagram, TikTok, Threads, personal blogs, private messaging, or other accounts. Institutional/publisher/conference/scholarly sources remain governed by `source-policy.md`.

## Permitted content
Papers (published/accepted), conference presentations, keynotes/invited talks, panels, workshops, research visits, public engagement, funded projects, group achievements, awards/recognition, student public research achievements, official events, collaboration announcements, leadership/service, media coverage of academic work.

## Excluded content
Family, personal travel unrelated to work, personal celebrations, political/religious commentary, private conversations, health, personal finance, unrelated reposts, informal photographs without professional relevance.

## Social is a discovery source, not a fact source
LinkedIn/X may establish that Dr Afli announced/attended/commented on an activity. The underlying academic claim (publication metadata, funding, titles, awards, appointment dates, student outcomes) must be corroborated from an authoritative source (ACL Anthology, ORCID, Crossref, OpenAlex, publisher, MTU, ADAPT, Research Ireland, CORDIS, official conference/project pages) before publication.

## Editorial
Curated news items, not feed copies. Rewrite into academic tone; never copy long passages; never reproduce comments, likes, reposts, or engagement counts; never present a post as peer-reviewed evidence. Each item links the original post AND an authoritative source where one exists, with a verification date.

## Images (see image-policy.md)
From Dr Afli's own professional posts or with explicit permission only; related to professional activity; no private/sensitive information; no students/children/audience/badges/screens/confidential slides without clearance; EXIF stripped; source and rights recorded. Where consent/rights are unclear → review item, do not publish.

## No tracking embeds
No live LinkedIn/X feed widgets or scripts that track visitors, set third-party cookies, harm accessibility/performance, or create platform dependence. Curated, locally stored, provenance-backed records with links to originals are used instead. The test suite (`tests/test_site.py`) fails the build if a known tracker/embed string appears in output.

## Current status
`data/social-content.json` is **empty** — no automated LinkedIn/X access is available in this environment and no posts were supplied, so nothing was imported. To populate: supply post URLs, an authorised export, or screenshots; each becomes a candidate record, corroborated and approved before it reaches the site.
