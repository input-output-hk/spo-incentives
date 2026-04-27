# Reader feedback / analytics — build setup

The static site supports three optional, privacy-first integrations that
inject *only* when their config fields are populated. Default builds remain
tracker-free; the placeholders collapse to empty strings.

| Layer | Purpose | Backing system |
|---|---|---|
| Analytics | Pageviews, referrers, custom events | **Plausible** or **Umami** (auto-detected) |
| Giscus | Per-page reader comments | GitHub Discussions |
| Finding reactions | 👍 / 👎 per `.sro-finding`, signal-only | Analytics custom events |

The analytics layer abstracts both providers behind a unified
`window.spoTrack(name, propsFlat)` global, so the rest of the bundled JS
calls one function regardless of which provider is wired up. Switching
provider is a config-only change.

The reactions layer requires *some* analytics provider to be configured
(the buttons fire `Finding Reaction` custom events with
`{finding, sentiment, page}` props).

## 1. Free-only deployment paths

Both production-grade options below run on free infrastructure:

| Path | Cost | Custom events | Setup cost |
|---|---|---|---|
| **Umami self-hosted on Fly.io** | 0 € | yes | ~10 min, single Postgres-backed app |
| Plausible self-hosted | 0 € | yes | Docker on a VPS, needs Postgres + ClickHouse |
| Cloudflare Web Analytics | 0 € | no | beacon JS only, loses Finding Reaction signal |
| Plausible Cloud | 9 USD/mo | yes | account creation only |

Recommended free setup: **Umami self-hosted on Fly.io free tier**. The
build pipeline supports it natively — set `SPO_UMAMI_WEBSITE_ID` and
`SPO_UMAMI_SCRIPT_URL`, the rest is handled by `build_site.py`.

## 2. Configuration surface

Every setting can be overridden via environment variables at build time.
Constants in `build_site.py` (around line 207) act as fallbacks. The
GitHub Actions workflow `pages.yml` reads these from repo Variables
(`vars.*`), not Secrets — none of these values are sensitive.

| Env var | Purpose | Default |
|---|---|---|
| `SPO_ANALYTICS_PROVIDER` | `plausible`, `umami`, `none`, or empty (auto-detect) | _empty_ |
| `SPO_PLAUSIBLE_DOMAIN` | Domain registered with Plausible | _empty_ |
| `SPO_PLAUSIBLE_SCRIPT_URL` | Script URL (cloud or self-host) | `https://plausible.io/js/script.js` |
| `SPO_UMAMI_WEBSITE_ID` | Website id from Umami dashboard | _empty_ |
| `SPO_UMAMI_SCRIPT_URL` | `<your-umami-host>/script.js` | _empty_ |
| `SPO_GISCUS_REPO` | `owner/repo` — must have Discussions enabled | _empty_ |
| `SPO_GISCUS_REPO_ID` | From <https://giscus.app> | _empty_ |
| `SPO_GISCUS_CATEGORY` | Discussion category name | `General` |
| `SPO_GISCUS_CATEGORY_ID` | From <https://giscus.app> | _empty_ |
| `SPO_GISCUS_MAPPING` | One thread per HTML page | `pathname` |
| `SPO_GISCUS_THEME` | Follows OS theme | `preferred_color_scheme` |
| `SPO_GISCUS_LANG` | Giscus UI language | `en` |
| `SPO_REACTIONS_ENABLED` | `0`/`false`/`no` to disable | `1` |

Auto-detection rule (when `SPO_ANALYTICS_PROVIDER` is empty):

1. If `SPO_UMAMI_WEBSITE_ID` and `SPO_UMAMI_SCRIPT_URL` are set → Umami.
2. Else if `SPO_PLAUSIBLE_DOMAIN` is set → Plausible.
3. Else → no analytics.

## 3. Enabling Umami self-hosted on Fly.io (recommended free path)

1. Sign up at <https://fly.io>, install `flyctl` locally.
2. Deploy Umami:

   ```bash
   git clone https://github.com/umami-software/umami umami-iog
   cd umami-iog
   flyctl launch --no-deploy --copy-config --name spo-umami
   flyctl postgres create --name spo-umami-db
   flyctl postgres attach --app spo-umami spo-umami-db
   flyctl deploy
   ```

3. Open `https://spo-umami.fly.dev`, log in with the default
   `admin / umami` account, change the password.
4. Settings → Websites → Add website → fill in name + domain
   (`iohk.github.io/spo-incentives` or your custom GitHub Pages
   domain). Copy the website id.
5. Set the two repo Variables on `input-output-hk/spo-incentives`:

   - `SPO_UMAMI_WEBSITE_ID = <copied id>`
   - `SPO_UMAMI_SCRIPT_URL = https://spo-umami.fly.dev/script.js`

6. Re-trigger the `Deploy GitHub Pages` workflow. Done.

Custom events captured automatically by the bundled JS module:

| Event name | Props | When |
|---|---|---|
| `Overlay Open` | `kind: observation\|finding`, `target: <canon-id>`, `page` | User clicks an `obs-ref` or `finding-ref` overlay |
| `Finding Reaction` | `finding: <canon-id>`, `sentiment: up\|down`, `page` | User clicks 👍 / 👎 on a `.sro-finding` |

Both events are queued via `window.spoTrack(name, props)`, which is safe
whether the deferred analytics script has loaded yet or not.

## 4. Enabling Plausible (alternative)

Cloud (paid): sign up at <https://plausible.io>, copy the domain string,
set `SPO_PLAUSIBLE_DOMAIN`. Custom-event tracking works out of the box
via `window.plausible(...)`.

Self-host (free, heavier infra): follow the
[plausible/community-edition](https://github.com/plausible/community-edition)
deployment, then set `SPO_PLAUSIBLE_DOMAIN` and point
`SPO_PLAUSIBLE_SCRIPT_URL` to your instance's `script.js`.

## 5. Enabling Giscus

1. Repo prerequisites: enable **Discussions** under repo settings, then
   install the [giscus GitHub App](https://github.com/apps/giscus) on
   the same repo.
2. Open <https://giscus.app>, paste the repo, choose a Discussion
   category (e.g. *General* or a dedicated *Reader Feedback*), and copy
   the four ids it generates: `repo`, `repo-id`, `category`,
   `category-id`.
3. Set the matching Variables (`SPO_GISCUS_REPO`, …) and re-trigger
   the workflow.

Giscus loads as an iframe pinned below `<div class="content">` and above
the site footer. Threads are keyed by `pathname` — `operator.html` gets
its own discussion thread, distinct from `pools.html`.

## 6. Verifying a build

No-op (default):

```bash
python3 build_site.py
grep -c 'plausible\|umami\|giscus\|feedback-react' operator.html  # expect 0
```

With Plausible Cloud stub:

```bash
SPO_PLAUSIBLE_DOMAIN="example.com" \
SPO_GISCUS_REPO="owner/repo" \
SPO_GISCUS_REPO_ID="R_kgDO_stub" \
SPO_GISCUS_CATEGORY_ID="DIC_kwDO_stub" \
python3 build_site.py operator
grep -n 'data-analytics\|data-reactions\|page-feedback' operator.html
```

With Umami self-host stub:

```bash
SPO_UMAMI_WEBSITE_ID="abc-123" \
SPO_UMAMI_SCRIPT_URL="https://spo-umami.fly.dev/script.js" \
SPO_GISCUS_REPO="owner/repo" \
SPO_GISCUS_REPO_ID="R_kgDO_stub" \
SPO_GISCUS_CATEGORY_ID="DIC_kwDO_stub" \
python3 build_site.py operator
grep -n 'data-analytics="umami"\|data-website-id\|page-feedback' operator.html
```

In each case expect: one analytics `<script defer ...>` in `<head>`, the
inline `window.spoTrack` bridge, three `data-*` attributes on `<body>`,
one `<section class="page-feedback">` above the site footer.

## 7. Privacy posture

- Plausible and Umami: no cookies, no fingerprinting, only aggregated
  counts. Both GDPR-compliant by default; both privacy-policy-friendly.
- Giscus: relies on GitHub auth — readers identify *voluntarily* when
  they post; the page itself does not track anonymous visitors.
- Finding reactions: stored only as analytics custom events
  (aggregated in the dashboard). No per-user tracking.
- SessionStorage is used solely to suppress double-counting in the
  current tab; it never leaves the browser.

## 8. Future extensions (not implemented)

- **Live counters** for finding reactions: currently signal-only.
  A small Cloudflare Worker (~50 LoC) bound to KV could expose
  `POST /react` and `GET /counts/<page>` for an in-page tally.
- **Hypothesis** annotation overlay: drop-in script tag on the same
  pages, no build-time wiring needed beyond a `<script>` include.
- **Outbound link tracking**: swap `script.js` for
  `script.outbound-links.js` in `SPO_PLAUSIBLE_SCRIPT_URL` (Plausible
  only — Umami tracks outbound clicks natively when enabled in the
  website's settings).

## 9. History

- 2026/04/27 — initial Plausible + Giscus + finding-reactions wiring.
- 2026/04/27 — added Umami support; analytics layer abstracted behind
  `window.spoTrack(name, props)`. Free-only deployment path is now
  Umami self-hosted on Fly.io.
