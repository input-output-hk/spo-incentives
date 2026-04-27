# Reader feedback / analytics — build setup

The static site supports three optional, privacy-first integrations that
inject *only* when their config fields are populated. Default builds remain
tracker-free; the placeholders collapse to empty strings.

| Layer | Purpose | Backing system |
|---|---|---|
| Plausible Analytics | Pageviews, referrers, custom events | Plausible Cloud or self-hosted |
| Giscus | Per-page reader comments | GitHub Discussions |
| Finding reactions | 👍 / 👎 per `.sro-finding`, signal-only | Plausible custom events |

All three can be enabled independently. The reactions layer requires
Plausible to be configured (the buttons fire `Finding Reaction` custom
events with `{finding, sentiment, page}` props).

## 1. Configuration surface

Every setting can be overridden via environment variables at build time.
Constants in `build_site.py` (around line 207) act as fallbacks.

| Env var | Constant | Default | Notes |
|---|---|---|---|
| `SPO_PLAUSIBLE_DOMAIN` | `PLAUSIBLE_DOMAIN` | _empty_ | The domain you registered with Plausible |
| `SPO_PLAUSIBLE_SCRIPT_URL` | `PLAUSIBLE_SCRIPT_URL` | `https://plausible.io/js/script.js` | Swap for self-hosted instance |
| `SPO_GISCUS_REPO` | `GISCUS_REPO` | _empty_ | `owner/repo` — must have Discussions enabled |
| `SPO_GISCUS_REPO_ID` | `GISCUS_REPO_ID` | _empty_ | From <https://giscus.app> |
| `SPO_GISCUS_CATEGORY` | `GISCUS_CATEGORY` | `General` | Discussion category name |
| `SPO_GISCUS_CATEGORY_ID` | `GISCUS_CATEGORY_ID` | _empty_ | From <https://giscus.app> |
| `SPO_GISCUS_MAPPING` | `GISCUS_MAPPING` | `pathname` | One thread per HTML page |
| `SPO_GISCUS_THEME` | `GISCUS_THEME` | `preferred_color_scheme` | Follows OS theme |
| `SPO_GISCUS_LANG` | `GISCUS_LANG` | `en` | Giscus UI language |
| `SPO_REACTIONS_ENABLED` | `REACTIONS_ENABLED` | `1` | `0`/`false`/`no` to disable |

## 2. Enabling Plausible

Cloud path:

1. Sign up at <https://plausible.io>, add the site, copy the domain
   string Plausible expects (e.g. `iohk.github.io/spo-incentives`).
2. Set `SPO_PLAUSIBLE_DOMAIN` in the GitHub Actions env block — or edit
   the constant in `build_site.py` directly.
3. Rebuild. Each page now ships a deferred `<script>` tag plus a stub
   that queues `plausible(...)` calls fired before the script loads.

Self-hosted path: same as above, but set `SPO_PLAUSIBLE_SCRIPT_URL` to
your instance's `script.js` (or `script.outbound-links.js` to track
external link clicks too).

Custom events captured automatically by the bundled JS module:

| Event name | Props | When |
|---|---|---|
| `Overlay Open` | `kind: observation\|finding`, `target: <canon-id>`, `page` | User clicks an `obs-ref` or `finding-ref` overlay |
| `Finding Reaction` | `finding: <canon-id>`, `sentiment: up\|down`, `page` | User clicks 👍 / 👎 on a `.sro-finding` |

Both events are queued via `window.plausible(...)`, which is safe whether
the deferred script has loaded yet or not.

## 3. Enabling Giscus

1. Repo prerequisites: enable **Discussions** under repo settings, then
   install the [giscus GitHub App](https://github.com/apps/giscus) on
   the same repo.
2. Open <https://giscus.app>, paste the repo, choose a Discussion
   category (e.g. *General* or a dedicated *Reader Feedback*), and copy
   the four ids it generates: `repo`, `repo-id`, `category`,
   `category-id`.
3. Set the matching env vars (`SPO_GISCUS_REPO`, …) and rebuild.

Giscus loads as an iframe pinned below `<div class="content">` and above
the site footer. Threads are keyed by `pathname` — `operator.html` gets
its own discussion thread, distinct from `pools.html`.

## 4. Verifying a build

No-op (default):

```bash
python3 build_site.py
grep -c 'plausible\|giscus\|feedback-react' operator.html  # expect 0
```

With stub config:

```bash
SPO_PLAUSIBLE_DOMAIN="example.com" \
SPO_GISCUS_REPO="owner/repo" \
SPO_GISCUS_REPO_ID="R_kgDO_stub" \
SPO_GISCUS_CATEGORY_ID="DIC_kwDO_stub" \
python3 build_site.py operator
grep -n 'data-plausible\|data-reactions\|page-feedback' operator.html
```

Expect: one `<script defer data-domain=...>` in `<head>`, three
`data-*` attributes on `<body>`, one `<section class="page-feedback">`
above the site footer.

## 5. Privacy posture

- Plausible: no cookies, no fingerprinting, only aggregated counts.
  GDPR-compliant by default.
- Giscus: relies on GitHub auth — readers identify *voluntarily* when
  they post, the page itself does not track anonymous visitors.
- Finding reactions: stored only as Plausible custom events
  (aggregated in the dashboard). No per-user tracking.
- SessionStorage is used solely to suppress double-counting in the
  current tab; it never leaves the browser.

## 6. Costs

| Tool | Free tier | Paid |
|---|---|---|
| Plausible Cloud | 30-day trial | $9/mo for 10k pageviews/mo |
| Plausible self-hosted | Free (your infra) | — |
| Giscus | Free | — |
| GitHub Discussions | Free for public repos | — |

Self-hosted Plausible runs on Docker (Postgres + ClickHouse) and is the
budget-conscious option if a CI runner / VM is already available.

## 7. Future extensions (not implemented)

- **Live counters** for finding reactions: currently signal-only.
  A small Cloudflare Worker (~50 LoC) bound to KV could expose
  `POST /react` and `GET /counts/<page>` for an in-page tally.
- **Hypothesis** annotation overlay: drop-in script tag on the same
  pages, no build-time wiring needed beyond a `<script>` include.
- **Outbound link tracking**: swap `script.js` for
  `script.outbound-links.js` in `PLAUSIBLE_SCRIPT_URL`.

---

History:
- 2026/04/27 — initial Plausible + Giscus + finding-reactions wiring.
