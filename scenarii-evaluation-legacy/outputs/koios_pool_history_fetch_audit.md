# Koios Pool History Fetch Audit

- Source: `https://api.koios.rest/api/v1`
- Shelley start epoch used in filter: **208**
- Tip epoch at fetch time: **617**
- Pools discovered from `pool_list`: **6119**
- Pools completed in history fetch: **6119**
- Pool-history rows written: **1,142,665**
- Epoch range actually written: **210..615**

## Notes
- `pool_history` is fetched one pool at a time because Koios does not expose a global pool-history table.
- The job is resumable through `koios_pool_history_fetched_ids.txt`.
- `pool_fees + deleg_rewards = total_pool_rewards` in this exported dataset.
- `owner_member_rewards = deleg_rewards - member_rewards` when `member_rewards` is available.
