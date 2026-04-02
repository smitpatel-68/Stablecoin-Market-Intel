-- ⚠️ DUNE USAGE: Each query below must be run SEPARATELY on Dune Analytics.
-- Table: stablecoins_multichain.balances

-- Query 1: Top stablecoins by total supply (market share / dominance)
-- Visualization: Pie chart or Bar chart | token_symbol vs supply_usd
SELECT
    token_symbol,
    ROUND(SUM(balance_usd), 0) AS supply_usd,
    ROUND(SUM(balance_usd) * 100.0 / SUM(SUM(balance_usd)) OVER (), 2) AS dominance_pct
FROM stablecoins_multichain.balances
WHERE token_symbol IN ('USDC', 'USDT', 'DAI', 'USDe', 'USDS', 'PYUSD', 'FDUSD')
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
ORDER BY 2 DESC

-- Query 2: USDC vs USDT — total supply and holder comparison
-- Visualization: Table or grouped bar chart
SELECT
    token_symbol,
    ROUND(SUM(balance_usd), 0) AS total_supply_usd,
    COUNT(DISTINCT blockchain) AS num_chains,
    COUNT(DISTINCT address) AS holders
FROM stablecoins_multichain.balances
WHERE token_symbol IN ('USDC', 'USDT')
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
ORDER BY 2 DESC

-- Query 3: USDC vs USDT dominance per chain (who wins where?)
-- Visualization: Table with conditional formatting
SELECT
    blockchain,
    ROUND(SUM(CASE WHEN token_symbol = 'USDC' THEN balance_usd ELSE 0 END), 0) AS usdc_supply,
    ROUND(SUM(CASE WHEN token_symbol = 'USDT' THEN balance_usd ELSE 0 END), 0) AS usdt_supply,
    CASE
        WHEN SUM(CASE WHEN token_symbol = 'USDC' THEN balance_usd ELSE 0 END) >
             SUM(CASE WHEN token_symbol = 'USDT' THEN balance_usd ELSE 0 END)
        THEN 'USDC dominant'
        ELSE 'USDT dominant'
    END AS dominant
FROM stablecoins_multichain.balances
WHERE token_symbol IN ('USDC', 'USDT')
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
HAVING SUM(balance_usd) > 1000000
ORDER BY usdc_supply + usdt_supply DESC
LIMIT 15
