-- ⚠️ DUNE USAGE: Each query below must be run SEPARATELY on Dune Analytics.
-- Table: stablecoins_multichain.balances

-- Query 1: Top 20 USDC holders on Ethereum
-- Visualization: Horizontal bar chart | address vs balance_usd
SELECT
    address,
    ROUND(balance_usd, 0) AS balance_usd
FROM stablecoins_multichain.balances
WHERE blockchain = 'ethereum'
    AND token_symbol = 'USDC'
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
ORDER BY balance_usd DESC
LIMIT 20

-- Query 2: USDC holder distribution tiers on Ethereum (concentration risk)
-- Visualization: Pie chart | tier vs pct_of_total
WITH ranked AS (
    SELECT
        address,
        balance_usd,
        ROW_NUMBER() OVER (ORDER BY balance_usd DESC) AS rank
    FROM stablecoins_multichain.balances
    WHERE blockchain = 'ethereum'
        AND token_symbol = 'USDC'
        AND balance_usd > 0
        AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
)
SELECT
    CASE
        WHEN rank <= 10 THEN 'Top 10'
        WHEN rank <= 50 THEN 'Top 11-50'
        WHEN rank <= 100 THEN 'Top 51-100'
        WHEN rank <= 1000 THEN 'Top 101-1000'
        ELSE 'All Others'
    END AS tier,
    COUNT(*) AS holder_count,
    ROUND(SUM(balance_usd), 0) AS tier_supply_usd,
    ROUND(SUM(balance_usd) * 100.0 / (SELECT SUM(balance_usd) FROM ranked), 2) AS pct_of_total
FROM ranked
GROUP BY 1
ORDER BY MIN(rank)

-- Query 3: USDC holders by balance size bucket (retail vs whale)
-- Visualization: Bar chart | size_bucket vs holder_count or total_balance_usd
SELECT
    CASE
        WHEN balance_usd < 100 THEN '1. Micro (<$100)'
        WHEN balance_usd < 1000 THEN '2. Small ($100-$1K)'
        WHEN balance_usd < 10000 THEN '3. Medium ($1K-$10K)'
        WHEN balance_usd < 100000 THEN '4. Large ($10K-$100K)'
        WHEN balance_usd < 1000000 THEN '5. Very Large ($100K-$1M)'
        ELSE '6. Whale (>$1M)'
    END AS size_bucket,
    COUNT(*) AS holder_count,
    ROUND(SUM(balance_usd), 0) AS total_balance_usd
FROM stablecoins_multichain.balances
WHERE blockchain = 'ethereum'
    AND token_symbol = 'USDC'
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
ORDER BY 1
