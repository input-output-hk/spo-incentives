# Koios Pool Owner History Fetch Audit

- Source: `https://api.koios.rest/api/v1`
- Pools discovered: **6119**
- Pools completed: **6119**
- Rows written: **1,360,003**
- Epoch range written: **210..618**

## Notes
- `pool_owner_history` is fetched in POST batches of pool ids.
- Oversized batches are split recursively on HTTP 413.
- The job is resumable through `koios_pool_owner_history_fetched_ids.txt`.
