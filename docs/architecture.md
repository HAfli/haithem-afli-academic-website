# Architecture (summary)
Plain static site generated from data/*.json by scripts/build.py (Python stdlib only), deployed on GitHub Pages. Full rationale and alternatives (Jekyll/al-folio, Hugo, Astro/Next) considered and rejected: see ../../ARCHITECTURE_DECISION.md.
Generator guarantees: content (data/) separated from templates (build.py render_* functions); all dynamic text HTML-escaped; URLs validated (http/https/mailto); data schema smoke-checked; malformed records skipped with a logged warning (fail-safe, never emit broken HTML); reproducible; output in site/ never hand-edited.

## Production build pipeline (v5)
`python3 scripts/build.py` is a self-contained, deterministic pipeline:
1. render pages from data/ into site/;
2. write CSS/JS/feed/sitemap/robots/.nojekyll;
3. **publish assets** — mirror assets/img (and assets/downloads if present) into site/assets/… (create dirs, overwrite, prune stale). Originals in assets/source are never published;
4. **validate** — scan every generated page for local references (src, href, srcset), confirm each exists in site/, confirm every image derivative (thumb/medium/large × webp/jpg) exists, and reject any root-relative ("/…") path that would break under the GitHub Pages repo prefix;
5. **report** — write site/build-report.html and site/build-report.json (pages, asset counts, image inventory, broken references, external links, total size, duration);
6. print a summary and **exit non-zero on any missing asset or broken link** — a broken site is never generated.
Flags: `--check` (validate data only), `--verbose` (log every copy/validation). No manual copying is ever required; GitHub Actions runs the same command before deploy.
