# Deployment Readiness & Pre-Publish Red-Team (v2)

2026-07-17 · Repository is complete, tested, and push-ready. Deployment is blocked only on GitHub write access.

## Pre-publish red-team (automated in tests/test_site.py — all passing)
| Check | Result |
|---|---|
| Private email addresses (only approved one permitted) | PASS |
| Telephone numbers | PASS |
| Home addresses | PASS (none present) |
| Access tokens / keys / secrets | PASS |
| Private repository links | PASS |
| Filesystem paths (/Users, /sessions) | PASS |
| EXIF geolocation | N/A (no images published) |
| Student grades / identifiers | PASS (academic-only fields) |
| Unauthorised photographs | PASS (zero images) |
| Images with unclear rights | PASS (none published; withheld by design) |
| Unverified funding claims (withheld terms) | PASS (€32M / €400k / GenAI Lab absent) |
| Unsupported employment claims | PASS (roles carry verification notes) |
| Broken internal links | PASS |
| Accessible alt text | PASS (all images, when present, require alt) |
| Duplicate news | PASS (stable ids) |
| Copied social text | PASS (no social content imported) |
| LinkedIn/X tracking scripts | PASS (tracker-string test) |
| Withheld verification-queue terms | PASS |

High-risk issue → build fails. Currently none.

## Deployment steps (execute when GitHub access exists)
1. Create/confirm empty repo `haithem-afli-academic-website`; confirm it holds no unrelated content.
2. Push this repository to `main`.
3. Settings → Pages → Source: **GitHub Actions**. `deploy.yml` builds, tests, deploys; HTTPS is automatic.
4. Settings → Branches: protect `main` (require PR + passing checks; no force push; no branch deletion). Enable secret scanning + Dependabot.
5. Inspect the workflow run logs; confirm build + tests green.
6. Open the live URL; verify Home, About, Research, Publications, Projects, Group, Supervision, Teaching, Innovation, Talks, Service, News, **Media**, CV, Contact, `sitemap.xml`, `feed.xml`, `robots.txt`.
7. Verify responsive layout (320px → desktop), external links, image loading (none yet), withheld claims absent, no secrets published.
8. Record: live URL, deployment commit hash, date. Provide rollback (docs/rollback.md).
Do not declare deployment complete until the live URL is opened and tested.

## Custom domain (optional, not configured)
GitHub Pages default URL is `https://<username>.github.io/haithem-afli-academic-website/`. Future custom-domain options: `haithemafli.com`, `haithemafli.ie`, or `afli.ie` (academic name-based). DNS: add a `CNAME` file with the domain, and at the registrar set an `ALIAS`/`ANAME` or four A-records to GitHub Pages IPs (185.199.108–111.153) for an apex domain, or a `CNAME` to `<username>.github.io` for a subdomain; then enable "Enforce HTTPS". Do not purchase/configure without approval; do not delay the Pages deployment for it.

## BASE_URL note
`scripts/build.py` `BASE_URL` is set to the project-Pages path; update it (and rebuild) if a `<username>` differs or a custom domain is adopted, so canonical/sitemap/feed/JSON-LD URLs stay correct.
