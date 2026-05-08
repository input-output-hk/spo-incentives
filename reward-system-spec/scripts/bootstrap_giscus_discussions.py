#!/usr/bin/env python3
"""Bootstrap GitHub Discussions for the 10 induced problems.

Idempotent. Run once with a personal access token that has `discussion:write`
scope on `input-output-hk/spo-incentives`:

    GITHUB_TOKEN=ghp_xxx python3 scripts/bootstrap_giscus_discussions.py

The script:

1. Resolves the `CPS` category id under the repo's Discussions.
2. For each of the 10 problems below, checks whether a Discussion with the
   canonical title `[μ##] <title>` already exists. If not, creates it.
3. Writes the resolved category id + the per-problem discussion id and
   number to `generated-website/data/giscus-problems.json`. That file is
   the single source of truth read at runtime by `site.js` to wire the
   "Discuss →" button on each card and by the sync workflow to fetch
   reaction counts.

Re-running the script is safe: existing Discussions are detected by
exact title match and re-used; only missing ones are created. The output
JSON is rewritten atomically each run.

The CPS category itself must exist before running this script — GitHub
does not yet expose category creation via the Discussions API. Create
it once at:

    https://github.com/input-output-hk/spo-incentives/discussions/categories

with these settings:
    - Name:        CPS
    - Description: Cardano Problem Statements — community priority votes
    - Format:      Open-ended discussion
    - Emoji:       any (pick something memorable, e.g. 🧭)

Convention used in the discussion body:

    Vote on this problem's priority by clicking a reaction on this post.
    The mapping the website reads:
        👎 = 1 — Low priority
        😕 = 2 — Below average
        👀 = 3 — Moderate
        🚀 = 4 — High priority
        ❤️ = 5 — Critical

Python 3.9 compatible.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

REPO_OWNER = "input-output-hk"
REPO_NAME = "spo-incentives"
CATEGORY_NAME = "CPS"

# 10 induced problems — mirrors `build_site.py` MICRO_SECTIONS / MACRO_SECTIONS.
# (problem_id_slug, token, title). The slug is the page anchor used by the
# carousel hash navigation — kept identical so a Discussion link can deep-link
# back to its card.
PROBLEMS = [
    # Microeconomics
    ("problem-1-2-3",   "μ01", "Closing the Consensus Incentive Gap: The pledge paradox & Non-Participant problem"),
    ("problem-1-3-3-1", "μ02", "Guarantee operator viability across the productive population"),
    ("problem-1-3-3-2", "μ03", "Restore a competitive delegator yield — soon to fall below 2% AYI"),
    ("problem-2-1-3-1", "μ04", "SPO (Supply-side) — fewer and fewer entities participate in consensus"),
    ("problem-2-1-3-2", "μ05", "Delegator (Arbiter-side) — titans move the disciplining capital, but not on yield"),
    # Macroeconomics
    ("problem-1-1-3",   "M01", "Funding the Protocol Without a Reserve"),
    # M02 (Non-participants) was absorbed into μ01 as the non-participant face of
    # the same lens-of-view incentive-gap problem. Numbers shift down accordingly.
    ("problem-2-2-3",   "M02", "Tx Submitter (Demand-side) — fees, the canonical answer to M01, are not growing fast enough at current throughput"),
    ("problem-3-1-1",   "M03", "A deflationist ₳ — what mechanisms can complement finite supply?"),
    ("problem-3-1-2",   "M04", "₳/Fiat volatility — what instruments can wire governance to price observations?"),
]

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
USER_AGENT = "spo-incentives-bootstrap/1.0"

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "generated-website" / "data" / "giscus-problems.json"


def _gql(token: str, query: str, variables: Optional[dict] = None) -> dict:
    """POST a GraphQL request and return the `data` block. Raises on error."""
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"GraphQL HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}\n")
        raise
    if body.get("errors"):
        raise RuntimeError(f"GraphQL errors: {body['errors']}")
    return body.get("data", {})


_REPO_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id
    discussionCategories(first: 50) {
      nodes { id name slug }
    }
    discussions(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        id
        number
        title
        category { name }
      }
    }
  }
}
"""


_CREATE_DISCUSSION = """
mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
  createDiscussion(input: {
    repositoryId: $repoId,
    categoryId: $catId,
    title: $title,
    body: $body
  }) {
    discussion { id number url title }
  }
}
"""


def _discussion_body(slug: str, token: str, title: str) -> str:
    """The body posted to each Discussion thread. Documents the voting
    convention so the page label and the GitHub thread agree."""
    return (
        f"# {token} — {title}\n\n"
        "**Community priority vote.** Click a reaction on this post to record "
        "how important you think this problem is for the V2 mechanism work. "
        "The reward-system-spec website reads these counts and shows a live "
        "weighted average alongside the problem card.\n\n"
        "**Reaction → priority mapping** (one vote per GitHub user; clicking "
        "a different reaction overrides your previous vote)\n\n"
        "| Reaction | Priority |\n"
        "|---|---|\n"
        "| 👎 | 1 — Low priority |\n"
        "| 😕 | 2 — Below average |\n"
        "| 👀 | 3 — Moderate |\n"
        "| 🚀 | 4 — High priority |\n"
        "| ❤️ | 5 — Critical |\n\n"
        f"**Card:** [`{slug}` on the problem-statements page]"
        f"(https://input-output-hk.github.io/spo-incentives/problem-statements.html#{slug})\n\n"
        "Comments are welcome below. Use them to argue *why* you voted what "
        "you voted, contest the framing, or supply evidence the diagnostic "
        "is missing."
    )


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.stderr.write(
            "Set GITHUB_TOKEN (PAT with `discussion:write` scope on "
            f"{REPO_OWNER}/{REPO_NAME}) before running.\n"
        )
        return 1

    sys.stderr.write(f"Resolving repo + categories for {REPO_OWNER}/{REPO_NAME}…\n")
    repo_data = _gql(
        token,
        _REPO_QUERY,
        {"owner": REPO_OWNER, "name": REPO_NAME},
    )["repository"]
    repo_id = repo_data["id"]

    cats = {n["name"]: n for n in repo_data["discussionCategories"]["nodes"]}
    if CATEGORY_NAME not in cats:
        sys.stderr.write(
            f"Category '{CATEGORY_NAME}' not found in {REPO_OWNER}/{REPO_NAME}.\n"
            f"Create it at https://github.com/{REPO_OWNER}/{REPO_NAME}/discussions/categories\n"
            f"(format: Open-ended discussion). Existing categories: "
            f"{', '.join(sorted(cats))}\n"
        )
        return 2
    category_id = cats[CATEGORY_NAME]["id"]
    sys.stderr.write(f"  category_id = {category_id}\n")

    # Index existing CPS discussions by exact title match.
    existing = {
        n["title"]: n
        for n in repo_data["discussions"]["nodes"]
        if n.get("category", {}).get("name") == CATEGORY_NAME
    }

    out_problems = {}
    for slug, token_label, title in PROBLEMS:
        full_title = f"[{token_label}] {title}"
        if full_title in existing:
            d = existing[full_title]
            sys.stderr.write(f"  ✓ {token_label} — already present (#{d['number']})\n")
        else:
            sys.stderr.write(f"  + {token_label} — creating Discussion…\n")
            body = _discussion_body(slug, token_label, title)
            res = _gql(
                token,
                _CREATE_DISCUSSION,
                {
                    "repoId": repo_id,
                    "catId": category_id,
                    "title": full_title,
                    "body": body,
                },
            )["createDiscussion"]["discussion"]
            d = res
            time.sleep(0.5)  # be polite to the secondary rate limit
        out_problems[slug] = {
            "discussion_id": d["id"],
            "discussion_number": d["number"],
            "token": token_label,
            "title": title,
        }

    out = {
        "synced_at": time.strftime("%Y/%m/%d %H:%M UTC", time.gmtime()),
        "repo": f"{REPO_OWNER}/{REPO_NAME}",
        "repo_id": repo_id,
        "category": CATEGORY_NAME,
        "category_id": category_id,
        "problems": out_problems,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    sys.stderr.write(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}\n")
    sys.stderr.write(
        "\nNext: paste the category_id printed above into "
        "SPO_GISCUS_CATEGORY_ID (or commit the JSON file and let "
        "build_site.py read it directly).\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
