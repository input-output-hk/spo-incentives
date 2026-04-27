# Q&A Worker — deploy

This Worker backs the inline "Ask the authors" feature on the static
site. It runs entirely on Cloudflare's free tier (Workers + KV) and
sends notification emails via MailChannels (also free for Workers).

## Prerequisites

- Cloudflare account (free).
- `npm install -g wrangler` (or use `npx wrangler`).
- A domain you can verify for MailChannels (any domain you own — you
  add a DNS TXT record per MailChannels' instructions).

## Deploy

```bash
cd cloudflare-worker

# Authenticate.
wrangler login

# Create the KV namespace and copy the id into wrangler.toml.
wrangler kv:namespace create QA
# → paste the returned id into wrangler.toml under kv_namespaces[0].id

# Edit wrangler.toml:
# - ALLOWED_ORIGIN: your GitHub Pages origin
# - FROM_EMAIL: an address on a domain you own (must pass MailChannels DNS check)
# - TO_EMAIL: where reader questions arrive

# Set the admin secret used by the answer endpoint.
wrangler secret put ADMIN_TOKEN
# → paste a strong random string when prompted

# Ship it.
wrangler deploy
```

You'll get a URL like `https://spo-qa.<your-subdomain>.workers.dev`.

## Wire it to the site

On `input-output-hk/spo-incentives` → Settings → Variables → add:

```
SPO_QA_ENDPOINT = https://spo-qa.<your-subdomain>.workers.dev
```

Re-trigger the `Deploy GitHub Pages` workflow. Each `.sro-finding` will
pick up an `Ask the authors` button.

## Posting answers

The static site only reads approved answers via `GET /qa/<finding>`.
Authors moderate questions out-of-band (in their inbox) and post
answers via:

```bash
curl -X POST https://spo-qa.../qa/answer \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "finding=OPE.O1.F4" \
  -F "author=Nicolas Henin" \
  -F "date=2026/04/27" \
  -F "html=<p>The flat fee follows a hyperbola because…</p>"
```

Once posted, the answer appears under the finding for every reader.

## Free tier limits

- Workers: 100 000 requests/day (paid plan starts at $5/mo for 10M).
- KV: 1 000 writes/day, 10M reads/month, 1 GB storage.
- MailChannels: free for Cloudflare Workers, no per-message cap
  documented as long as you stay under abuse thresholds.

For an internal-research site this is wildly oversized — you would need
hundreds of questions per day to leave the free tier.
