# Release 3.2 — Deployment readiness

Audit date: 2026-11-02 · Repository: `HAfli/haithem-afli-academic-website` · Site: https://hafli.github.io/haithem-afli-academic-website/

No tokens, passwords or keys were printed, copied or committed during this audit. The GitHub CLI token was masked in all output.

## Environment found

| Item | Finding |
|---|---|
| Authenticated account | `HAfli` via GitHub CLI (macOS keyring), HTTPS git protocol |
| Token scopes | `repo`, `workflow`, `read:org`, `gist` |
| Repository permission | `ADMIN` (from `gh repo view --json viewerPermission`) |
| Default branch | `main` (also the Pages publishing branch) |
| Branch protection on `main` | None |
| Pages | Enabled, public, HTTPS enforced, `build_type: workflow` (GitHub Actions), no custom domain |
| `github-pages` environment | Deployment branch policy: `main` only |
| Actions secrets / variables | None configured — none required (see below) |
| Workflow token defaults | `default_workflow_permissions: read`, `can_approve_pull_request_reviews: false` |
| Local clone | `website/repo` is on the old branch `release-1.2-multimedia` with ~70 uncommitted modified files. **It was not touched.** All Release 3.2 work was done in a separate git worktree (`website/release-3.2`) created from `origin/main`. |

### How deployment works

`.github/workflows/deploy.yml` runs on every push to `main` (and on manual `workflow_dispatch`):

1. `python3 scripts/build.py --check` (data validation)
2. `python3 scripts/build.py --verbose` (generates `site/`)
3. `python3 tests/test_site.py` (links, accessibility, privacy, JSON-LD, data integrity)
4. `actions/upload-pages-artifact` → `actions/deploy-pages` into the `github-pages` environment

Authentication to Pages uses the workflow's short-lived OIDC token (`id-token: write`, `pages: write`). **No repository secret is needed**, so the absence of secrets is correct, not a problem.

Last successful deployment: run 35256325095, 2026-09-17 (commit `e6348a4`, the current `main`).

## Capability assessment

| Capability | Status | Evidence | Required action |
|---|---|---|---|
| Repository read access | AVAILABLE | `gh repo view` succeeded; `git fetch origin` succeeded | None |
| Repository write access | AVAILABLE | `viewerPermission: ADMIN`; token scope `repo` | None |
| Branch creation | AVAILABLE | Created `release-3.2-academic-teaching-integration` from `origin/main` and pushed it | None |
| Commit and push | AVAILABLE | Release commits pushed to the release branch | None |
| Pull request creation | AVAILABLE | PR #1 opened against `main`: https://github.com/HAfli/haithem-afli-academic-website/pull/1 | None |
| GitHub Actions access | AVAILABLE | Listed workflows, runs and failure logs; token scope `workflow` | None |
| GitHub Pages configuration access | AVAILABLE | `GET /repos/.../pages` and environment policies readable (admin) | None |
| Deployment permission | AVAILABLE (by policy, not exercised) | Admin rights; merging to `main` triggers `deploy.yml`; `workflow_dispatch` also permitted | Your explicit approval to merge |
| Production deployment test | NOT TESTED | Deliberately not run: the only path to production is a push to `main`, which you asked me not to do without approval | Merge the PR when satisfied |

A separate "harmless documentation-only test PR" was not needed. The release branch and PR exercise exactly the same permissions (branch, commit, push, PR) without touching production.

## Pre-existing workflow problems (not caused by this release, not blocking deployment)

The deploy workflow is healthy, but three scheduled workflows have failed daily since at least 26 October 2026:

| Workflow | Error (from run logs) | Cause | Fix (needs your decision) |
|---|---|---|---|
| Admin sync (`admin-sync.yml`) | `GitHub Actions is not permitted to create or approve pull requests.` | Repository setting blocks Actions from opening PRs | Settings → Actions → General → Workflow permissions → tick **Allow GitHub Actions to create and approve pull requests** (or remove the PR step) |
| Weekly source monitor (`monitor.yml`) | Same as above | Same | Same setting |
| Research Intelligence (`research-intelligence.yml`) | `The path for one of the files in artifact is not valid: /reports/communication/pub:2024.politicalnlp-1.0.md. Contains the following character: Colon :` | A generated report filename contains `:` (from the publication id), which `upload-artifact` rejects | Sanitise `:` in generated filenames in `scripts/research_os.py` — recommended follow-up, left out of this release to keep scope controlled |

Two further workflow files are **invalid YAML**. GitHub reports "This run likely failed because of a workflow file issue" and creates zero jobs on every push, including the push of this release branch and the September push to `main`:

| Workflow file | Symptom | Likely cause | Effect |
|---|---|---|---|
| `.github/workflows/sync-deadlines.yml` | 0-job failure on each push | `run: { python3 scripts/build.py; python3 tests/test_site.py; }` is parsed as a YAML mapping, not a shell command | Daily deadline sync never runs |
| `.github/workflows/generate-newsletter.yml` | 0-job failure on each push | Workflow file does not parse (shown by path, not by name, in the Actions list) | Newsletter generation never runs |

These failures show as red crosses on the PR's branch but **do not affect `deploy.yml` or the release**. Nothing in them executed, and no commits or deployments were produced.

All three workflows also warn that their actions target the deprecated Node.js 20 runtime (`actions/checkout@v4`, `setup-python@v5`, `upload-artifact@v4`, `create-pull-request@v6`). They currently still run. Upgrading action versions is a recommended follow-up.

Changing repository settings is an account/security setting change, so I did not alter it.

## Gaps worth knowing

- **No CI on pull requests.** `deploy.yml` runs only on pushes to `main`, so the PR itself is not validated by GitHub. I ran the identical build and test commands locally (see QA report). A small `pull_request` workflow running `build.py --check`, `build.py` and `tests/test_site.py` is recommended.
- **No branch protection on `main`.** Anyone with write access (including automation) can deploy by pushing. Consider requiring a PR.

## Decision

**READY WITH LIMITATIONS.**

The credentials are sufficient to implement, push and open a PR, and technically to deploy: admin rights, a working Pages workflow, and no secrets required. Two limits remain:

1. Production publication requires **your explicit approval to merge** the PR into `main`. I have not merged.
2. Browser-based checks (visual, mobile and console) could not be run because the Chrome extension was not connected. Server-side and static checks were run instead (see the QA report).

No additional credentials or tokens are needed. If you ever need to re-authenticate, run `gh auth login` yourself in a terminal (or type `! gh auth login` in Claude Code). Never paste a personal access token into a chat.
