# Deployment Guide
Prerequisite: GitHub repository `haithem-afli-academic-website` under Dr Afli's account (see repo README for access status).
1. Push this repository to `main`.
2. Repo Settings -> Pages -> Source: "GitHub Actions".
3. `.github/workflows/deploy.yml` runs on push: validates data, builds site/, runs tests/test_site.py, deploys to Pages.
4. Enable branch protection on `main` (require PR + passing checks). Enable Dependabot + secret scanning.
5. First deploy: verify the LIVE public URL loads, spot-check pages on mobile + desktop, confirm sitemap.xml and feed.xml resolve, run an external link check and a Lighthouse/axe audit. Do not consider deployment successful until the live site is verified.
6. Optional custom domain: add CNAME + update BASE_URL in build.py and canonical/sameAs.
