# Public API Layer

A read-only, static JSON API generated from verified data on **every build** into `site/api/`. It exposes only already-public, aggregate-safe data (no personal or private information) and provides a stable contract for future integrations (institutional dashboards, NotebookLM, third-party widgets).

Because it is static JSON on GitHub Pages, it is cache-friendly, needs no server, and cannot leak private data (test-guarded).

## Base URL

```
https://hafli.github.io/haithem-afli-academic-website/api/
```

## Endpoints

`index.json` is the manifest; consumers should read it first to discover available endpoints and the schema version.

| Endpoint | Contents |
|---|---|
| `index.json` | Version + list of endpoints + generation date. |
| `themes.json` | Research themes: `id`, `name`, `summary`. |
| `publications.json` | Publications (public fields): `title`, `year`, `venue`, `type`, `authors`, `themes`, `doi`, `url`. |
| `projects.json` | Projects (withheld excluded): `kind`, `name`, `funder`, `role`, `period`, `url`. |
| `funding.json` | Verified, future-dated open calls only: `name`, `programme`, `deadline`, `url`. |
| `analytics.json` | Aggregate publication analytics: `by_year`, `by_type`, `by_theme`, `distinct_coauthors`. No personal data. |
| `dashboard.json` | Public-safe portfolio snapshot: `publications`, `projects`, `funding_open_calls`, `website`. |

Every object includes a `generated` date (ISO-8601).

## Guarantees

- **No personal/private data.** Student and grant internals are never present (enforced by `tests/test_site.py`).
- **No fabricated fields.** Values are computed from verified data; absent data is omitted, not invented.
- **Aggregate analytics only.** Country/visitor analytics remain aggregate and privacy-preserving (see `docs/privacy-policy.md`); citation counts are excluded until a verified source is connected.
- **Stable-ish contract.** Additive changes only within a `version`. Breaking changes bump `index.json.version`.

## Example (JavaScript)

```js
const base = "/api/";
const manifest = await (await fetch(base + "index.json")).json();
if (manifest.endpoints.includes("analytics.json")) {
  const a = await (await fetch(base + "analytics.json")).json();
  console.log(`${a.total_publications} publications, ${a.distinct_coauthors} collaborators`);
}
```

## Regeneration

Produced by `scripts/research_os.py::gen_api()`, invoked automatically from `scripts/build.py`. To regenerate standalone: `python3 scripts/research_os.py --api`.
