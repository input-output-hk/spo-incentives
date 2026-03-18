# Pool Reward Distribution Summary (Mainnet)

- Pool-history epochs covered: **210..615**
- Pools with reward history: **6,056**
- Epoch rows in summary: **406**
- Total realized pool rewards since Shelley: **4516.74M ADA**

## Exact split from Koios pool history
- Operator fees: **818.95M ADA**
- Owner member-like rewards: **83.53M ADA**
- Public delegator/member rewards: **3614.26M ADA**

## Cross-check against epoch-wide reward totals
- `koios_pool_history_mainnet.csv` is summed by epoch and compared with `reward_epoch_pools_mainnet.csv`.
- Median absolute epoch difference: **3000.0000 ADA**
- Max absolute epoch difference: **23500.0000 ADA**

## Reward concentration
- Top 10 pools captured **3.1%** of all realized rewards since Shelley.
- Top 50 pools captured **12.9%**.
- Top 100 pools captured **23.2%**.
- Top 250 pools captured **46.9%**.
- Top 10 bucket mix: **5 Near-saturation pools, 3 Large healthy pools, 2 Healthy pools**.
- Top 50 bucket mix: **24 Large healthy pools, 15 Healthy pools, 11 Near-saturation pools**.
- Top 100 bucket mix: **42 Healthy pools, 42 Large healthy pools, 16 Near-saturation pools**.
- Top 250 bucket mix: **144 Healthy pools, 71 Large healthy pools, 35 Near-saturation pools**.
- All current healthy-and-above pools (`n=679`) bucket mix: **508 Healthy pools, 112 Large healthy pools, 59 Near-saturation pools**.

## Distribution by size category
- `Subscale pools`: active stake share **2.5%**, block share **2.3%**, reward share **2.3%**
- `Healthy pools`: active stake share **33.5%**, block share **33.7%**, reward share **32.1%**
- `Large healthy pools`: active stake share **24.8%**, block share **24.7%**, reward share **25.0%**
- `Near-saturation pools`: active stake share **23.0%**, block share **23.1%**, reward share **23.1%**
- `Saturated pools`: active stake share **15.0%**, block share **15.1%**, reward share **16.7%**
- `Oversaturated pools`: active stake share **1.2%**, block share **1.1%**, reward share **0.9%**

## Exact reward split by size category
- `Subscale pools` (`n=1423`): operator fees **30.0%**, owner member-like rewards **2.6%**, public delegator/member rewards **62.1%**, median pool reward **335.3 ADA/epoch**
- `Healthy pools` (`n=982`): operator fees **8.7%**, owner member-like rewards **0.3%**, public delegator/member rewards **89.9%**, median pool reward **5741.4 ADA/epoch**
- `Large healthy pools` (`n=257`): operator fees **5.1%**, owner member-like rewards **0.1%**, public delegator/member rewards **93.8%**, median pool reward **22572.2 ADA/epoch**
- `Near-saturation pools` (`n=66`): operator fees **6.2%**, owner member-like rewards **0.0%**, public delegator/member rewards **93.8%**, median pool reward **28002.6 ADA/epoch**
- `Saturated pools` (`n=17`): operator fees **100.0%**, owner member-like rewards **0.0%**, public delegator/member rewards **0.0%**, median pool reward **31223.6 ADA/epoch**
- `Oversaturated pools` (`n=0`): operator fees **0.0%**, owner member-like rewards **0.0%**, public delegator/member rewards **0.0%**, median pool reward **0.0 ADA/epoch**

## What this unlocks next
- We now have exact realized pool-level reward splits from Shelley to current tip.
- The next step is pledge compliance and parameter-change analysis using `pool_owner_history` and `pool_updates`.
