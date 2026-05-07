# `data/` — runtime JSON consumed by the website

`giscus-problems.json` maps each induced problem (μ01..M05) to its
GitHub Discussion thread in the `CPS` category of
`input-output-hk/spo-incentives`. `assets/site.js` reads it at runtime
to wire the *Discuss on GitHub* CTA in the top-right corner of each
problem card; clicking the button opens that problem's Discussion.

| File | Source | Refresh cadence |
|---|---|---|
| `giscus-problems.json` | `scripts/bootstrap_giscus_discussions.py` | Manual, on first setup or when a new induced problem is added |

## First-time setup (already done for the 10 current problems)

1. Create the `CPS` category in the repo's Discussions UI
   (https://github.com/input-output-hk/spo-incentives/discussions/categories).
2. Run the bootstrap script with a personal access token that has
   `public_repo` (or `repo`) scope:
   ```
   GITHUB_TOKEN=ghp_xxx python3 reward-system-spec/scripts/bootstrap_giscus_discussions.py
   ```
3. Commit `giscus-problems.json` to the repo.

The script is idempotent — re-running it adds Discussions for any new
problems listed in `bootstrap_giscus_discussions.py:PROBLEMS` and
leaves the existing ones alone.
