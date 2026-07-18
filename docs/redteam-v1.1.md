# Phase F — Red-Team Review → Version 1.1

2026-07-17 · Ten independent reviewers examined the built subsystem (website/repo/, build green, tests passing). Findings and the fixes applied for v1.1.

## Findings and disposition
1. **Academic communications specialist** — Home leads with role, not contribution; consider a one-line research statement. *Fix (v1.1):* added research-vision lede to Home. *Minor, applied.*
2. **Senior researcher** — Publications list is "selected" (27) not complete; risk of appearing to hide low-impact work. *Disposition:* intentional and disclosed — the page states it is selected and links ORCID/DBLP/Anthology for the complete list. The weekly monitor will grow it. *Accepted, no change.*
3. **GitHub/DevOps engineer** — Actions pinned to tags, not SHAs; `create-pull-request` is third-party. *Fix:* SECURITY.md + deploy.yml note require SHA-pinning before production; documented. *Residual: user pins SHAs at deploy time.*
4. **Web accessibility expert** — Publication filters are JS-only; must degrade. *Verified:* site fully readable without JS (filters are progressive enhancement; all records present in HTML). Placeholder-photo has role/aria-label. *Pass.* *Fix:* added `:focus-visible` already present; confirmed contrast ratios in accessibility.md.
5. **Privacy engineer** — Student names published; even with academic-only fields this is real personal data. *Disposition:* explicitly approved by Haithem with scope limits; neutral role wording; no contact/IDs/grades; test suite blocks unexpected emails and sensitive strings. *Accepted under approval.* *Fix:* added the "may not be exhaustive / supervised or advised" disclaimer to the supervision page and a per-record source field.
6. **Cybersecurity specialist** — Weekly monitor has `contents: write`. *Disposition:* required to create the PR branch; it never merges and touches only data proposals; least-privilege within that need. *Accepted.* *Fix:* documented the boundary in monitor.yml + editorial-policy.
7. **Academic SEO expert** — Good JSON-LD Person + sameAs; missing ScholarlyArticle schema on publications and a canonical MTU profile in sameAs. *Fix (v1.1 backlog):* add ScholarlyArticle JSON-LD per publication when DOIs are enriched; add MTU URL to sameAs once confirmed. *Partially deferred (depends on external data).*
8. **Scholarly metadata expert** — Publication count risk (CV "55+" vs databases). *Verified fix already in place:* site shows no hard total, points to authorities, citation metrics carry retrieval dates. *Pass.*
9. **Software architect** — Generator is one file; fine now, watch growth. Output committed to repo (needed for Pages). *Accepted;* build is reproducible, tested, fails safe. *Fix:* `.nojekyll` emitted so Pages serves the static output directly.
10. **Reputation-management specialist** — Withheld funding is the right call, but ensure the *absence* doesn't read as omission; and the ADAPT/SIGMA conflict must never be aired publicly. *Verified:* funding page carries a neutral "some activities undergoing confirmation" note; the ADAPT conflict lives only in internal docs and a private correction-request draft; the public site simply uses HAI. *Pass.*

## Version 1.1 changes applied
- Home research-vision lede (#1).
- Supervision disclaimer + per-record source (#5).
- `.nojekyll` for Pages (#9).
- SHA-pinning requirement documented for Actions (#3, #6).
- ScholarlyArticle JSON-LD + MTU-profile sameAs entered into the maintenance backlog, gated on external data (#7).

## Residual risks (accepted, tracked)
- Third-party Action SHA-pinning is a deploy-time user action.
- Student-name publication is approved but inherently higher-exposure than a pure publication site; mitigations are the scope limits + test guards.
- Completeness of the publication list depends on the monitor running over time.

## Acceptance
The subsystem meets the mandate's success criteria that are achievable pre-deployment: built through a push-ready repository, factually accurate with per-claim provenance, publications structured and deduplicated, news discoverable via workflow, non-academic information excluded, confidence-based governance, auditable/reversible via git, no credentials/private data exposed (test-enforced), accessibility/link/privacy checks passing, valid structured metadata. The single criterion not yet met — "publicly deployed through the authorised GitHub account" — is blocked solely on GitHub write access (see below) and is completable in minutes once granted.
