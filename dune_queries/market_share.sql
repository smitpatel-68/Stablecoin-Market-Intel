-- Stablecoin Market Share & Dominance Tracker
-- Tracks USDC vs USDT market share shifts over time
-- Core metric for Circle competitive intelligence

-- Query 1: Weekly market share — USDC vs USDT vs Others (last 12 months)
-- Uses Dune's stablecoin dataset (launched March 2026)
SELECT
    date_trunc('week', day) AS week,
    SUM(CASE WHEN symbol = 'USDT' THEN circulating_usd ELSE 0 END) AS usdt_supply,
    SUM(CASE WHEN symbol = 'USDC' THEN circulating_usd ELSE 0 END) AS usdc_supply,
    SUM(CASE WHEN symbol NOT IN ('USDT', 'USDC') THEN circulating_usd ELSE 0 END) AS other_supply,
    SUM(circulating_usd) AS total_supply,
    -- Dominance percentages
    SUM(CASE WHEN symbol = 'USDT' THEN circulating_usd ELSE 0 END) * 100.0
        / NULLIF(SUM(circulating_usd), 0) AS usdt_dominance_pct,
    SUM(CASE WHEN symbol = 'USDC' THEN circulating_usd ELSE 0 END) * 100.0
        / NULLIF(SUM(circulating_usd), 0) AS usdc_dominance_pct
FROM stablecoin.daily_supply
WHERE day >= NOW() - INTERVAL '365' DAY
GROUP BY 1
ORDER BY 1;

-- Query 2: USDC chain migration — where is USDC growing fastest?
-- Compares current vs 90-day-ago distribution
WITH current_dist AS (
    SELECT
        blockchain,
        SUM(balance_usd) AS current_supply
    FROM stablecoin.balances
    WHERE symbol = 'USDC'
        AND balance_usd > 0
    GROUP BY 1
),
old_dist AS (
    SELECT
        blockchain,
        SUM(circulating_usd) AS supply_90d_ago
    FROM stablecoin.daily_supply
    WHERE symbol = 'USDC'
        AND day = date_trunc('day', NOW() - INTERVAL '90' DAY)
    GROUP BY 1
)
SELECT
    c.blockchain,
    c.current_supply,
    o.supply_90d_ago,
    c.current_supply - COALESCE(o.supply_90d_ago, 0) AS absolute_change,
    CASE
        WHEN o.supply_90d_ago > 0 THEN (c.current_supply - o.supply_90d_ago) / o.supply_90d_ago * 100
        ELSE NULL
    END AS pct_change_90d
FROM current_dist c
LEFT JOIN old_dist o ON c.blockchain = o.blockchain
WHERE c.current_supply > 10000000  -- >$10M
ORDER BY absolute_change DESC;

-- Query 3: USDT vs USDC by use case (DEX volume vs transfers)
-- Approximation: DEX trading volume suggests speculative use,
-- transfer volume suggests payment/settlement use
SELECT
    date_trunc('week', block_time) AS week,
    -- DEX volume (speculative/trading)
    SUM(CASE WHEN token_bought_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 OR token_sold_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 THEN amount_usd ELSE 0 END) AS usdc_dex_volume,
    SUM(CASE WHEN token_bought_address = 0xdAC17F958D2ee523a2206206994597C13D831ec7 OR token_sold_address = 0xdAC17F958D2ee523a2206206994597C13D831ec7 THEN amount_usd ELSE 0 END) AS usdt_dex_volume
FROM dex.trades
WHERE blockchain = 'ethereum'
    AND block_time >= NOW() - INTERVAL '90' DAY
    AND amount_usd > 100
GROUP BY 1
ORDER BY 1;
