# Accessibility Policy & Test Plan
Target: WCAG 2.2 AA where reasonably achievable.
Built-in: semantic HTML5 landmarks (header/nav/main/footer), one h1 per page, logical heading order, skip-to-content link, aria-current on active nav, visible focus outlines (:focus-visible), responsive layout to 320px, colour contrast >= 4.5:1 for body text (ink #1a1a1a on #fff; accent #0b5c8a on #fff), no colour-only meaning, forms/controls labelled, site fully usable without JavaScript (filters are progressive enhancement).
Automated (in tests/test_site.py): lang attribute, title, single h1, skip link, single main landmark, structural tag balance.
Manual before launch and after major design changes: keyboard-only navigation of every page; screen-reader pass (VoiceOver/NVDA) on Home, Publications, Supervision; zoom to 200%; automated audit (axe DevTools / Lighthouse) with issues triaged; check alt text once a photo is added.
