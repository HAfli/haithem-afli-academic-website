# Security Policy

## Reporting
Report suspected security issues privately by email (Haithem.Afli@mtu.ie) rather than public issues.

## Controls in this repository
- No secrets in the repository; the build needs none. GitHub Pages deploy uses OIDC (id-token), not stored tokens.
- Least-privilege Actions: deploy job has `pages: write` + `id-token: write` only; monitor job has `contents/pull-requests: write` to open PRs and never merges.
- Pin third-party Actions to commit SHAs before production use (currently tagged for readability).
- Enable branch protection on `main` (require PR + passing checks). Enable Dependabot/secret scanning in repo settings.
- HTTPS enforced by GitHub Pages. External links use rel="noopener".
- Reproducible, dependency-free build (Python stdlib) minimises supply-chain surface.
- Rollback = revert commit (see docs/rollback.md).
