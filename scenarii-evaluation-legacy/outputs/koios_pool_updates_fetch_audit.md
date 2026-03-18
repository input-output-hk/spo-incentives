# Koios Pool Updates Fetch Audit

- Source: `https://api.koios.rest/api/v1`
- Rows written: **39,982**
- Active epoch range: **210..620**

## Notes
- `pool_updates` is fetched page by page with `offset` and `limit`.
- JSON-valued columns such as `owners`, `relays`, and `meta_json` are serialized into CSV cells.
