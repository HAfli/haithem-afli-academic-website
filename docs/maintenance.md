# Maintenance Guide
Routine (mostly automated):
- Weekly: source monitor workflow opens a PR with proposed updates (publications, links); review against docs/source-policy.md before merge. Link check via rebuild+tests.
- Monthly: refresh citation metrics (with retrieval date) if displayed; Dependabot for any Actions updates.
- Per ARR/conference cycle: reconcile new publications from ACL Anthology/ORCID.
- Quarterly: full content audit against the CV and verification queue; resolve any withheld items that have become confirmable.
- Annually: architecture review; prune stale time-sensitive claims; re-run accessibility audit.
Manual triggers: new paper, award, talk, role change, funding confirmation, photograph provided, MTU profile URL confirmed.
Golden rules: output/ is generated (never hand-edit); no dependency added without justification; funding/role/bio/contact changes need explicit approval; every change is a reviewable commit.
