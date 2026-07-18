# Architecture (summary)
Plain static site generated from data/*.json by scripts/build.py (Python stdlib only), deployed on GitHub Pages. Full rationale and alternatives (Jekyll/al-folio, Hugo, Astro/Next) considered and rejected: see ../../ARCHITECTURE_DECISION.md.
Generator guarantees: content (data/) separated from templates (build.py render_* functions); all dynamic text HTML-escaped; URLs validated (http/https/mailto); data schema smoke-checked; malformed records skipped with a logged warning (fail-safe, never emit broken HTML); reproducible; output in site/ never hand-edited.
