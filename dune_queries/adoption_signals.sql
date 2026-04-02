-- ⚠️ DUNE USAGE: Each query below must be run SEPARATELY on Dune Analytics.
-- Table: stablecoins_multichain.transfers

-- Query 1: USDC daily transfer volume across ALL chains (last 30 days)
-- Visualization: Line chart | X: day, Y: volume_usd
SELECT
    date_trunc('day', block_time) AS day,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount_usd), 0) AS volume_usd
FROM stablecoins_multichain.transfers
WHERE token_symbol = 'USDC'
    AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
    AND amount_usd > 0
GROUP BY 1
ORDER BY 1

-- Query 2: USDC transfer volume by chain (last 30 days)
-- Shows where USDC is most actively used
-- Visualization: Bar chart | X: blockchain, Y: volume_usd
SELECT
    blockchain,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount_usd), 0) AS volume_usd
FROM stablecoins_multichain.transfers
WHERE token_symbol = 'USDC'
    AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
    AND amount_usd > 0
GROUP BY 1
ORDER BY 3 DESC
LIMIT 10

-- Query 3: USDC transfers by size bucket (retail vs institutional)
-- Visualization: Stacked bar or pie chart
SELECT
    CASE
        WHEN amount_usd < 100 THEN '1. Micro (<$100)'
        WHEN amount_usd < 1000 THEN '2. Small ($100-$1K)'
        WHEN amount_usd < 10000 THEN '3. Medium ($1K-$10K)'
        WHEN amount_usd < 100000 THEN '4. Large ($10K-$100K)'
        WHEN amount_usd < 1000000 THEN '5. Very Large ($100K-$1M)'
        ELSE '6. Institutional (>$1M)'
    END AS size_bucket,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount_usd), 0) AS total_volume_usd
FROM stablecoins_multichain.transfers
WHERE blockchain = 'ethereum'
    AND token_symbol = 'USDC'
    AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
    AND amount_usd > 0
GROUP BY 1
ORDER BY 1

-- Query 4: Large USDC transfers (>$10M) in last 7 days — whale alerts
-- Visualization: Table
SELECT
    block_time,
    blockchain,
    "from" AS sender,
    "to" AS receiver,
    ROUND(amount_usd, 0) AS amount_usd,
    tx_hash
FROM stablecoins_multichain.transfers
WHERE token_symbol = 'USDC'
    AND amount_usd > 10000000
    AND block_time >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY amount_usd DESC
LIMIT 50

-- Query 5: USDC vs USDT daily volume comparison across all chains
-- Visualization: Dual line chart | X: day, Y: volume, series: token_symbol
SELECT
    date_trunc('day', block_time) AS day,
    token_symbol,
    ROUND(SUM(amount_usd), 0) AS volume_usd
FROM stablecoins_multichain.transfers
WHERE token_symbol IN ('USDC', 'USDT')
    AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
    AND amount_usd > 0
GROUP BY 1, 2
ORDER BY 1, 2
