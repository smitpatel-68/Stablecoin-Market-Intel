-- ⚠️ DUNE USAGE: Each query below must be run SEPARATELY on Dune Analytics.
-- Table: stablecoins_multichain.balances | stablecoins_multichain.transfers

-- Query 1: Total USDC supply across ALL chains
SELECT
    ROUND(SUM(balance_usd), 0) AS total_usdc_supply_usd
FROM stablecoins_multichain.balances
WHERE token_symbol = 'USDC'
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')

-- Query 2: USDC supply by chain (top 15)
-- Visualization: Bar chart | X: blockchain, Y: usdc_supply_usd
SELECT
    blockchain,
    ROUND(SUM(balance_usd), 0) AS usdc_supply_usd,
    COUNT(DISTINCT address) AS holders
FROM stablecoins_multichain.balances
WHERE token_symbol = 'USDC'
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
ORDER BY 2 DESC
LIMIT 15

-- Query 3: USDC supply trend on Ethereum (daily, last 90 days)
-- Visualization: Line chart | X: day, Y: usdc_supply_usd
SELECT
    day,
    ROUND(SUM(balance_usd), 0) AS usdc_supply_usd
FROM stablecoins_multichain.balances
WHERE blockchain = 'ethereum'
    AND token_symbol = 'USDC'
    AND balance_usd > 0
    AND day >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY 1
ORDER BY 1

-- Query 4: USDC mint/burn on Ethereum (last 30 days)
-- Mints = from zero address | Burns = to zero address
-- Visualization: Bar chart | X: day, Y: net_flow_usd
SELECT
    date_trunc('day', block_time) AS day,
    ROUND(SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount_usd ELSE 0 END), 0) AS minted_usd,
    ROUND(SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN amount_usd ELSE 0 END), 0) AS burned_usd,
    ROUND(SUM(CASE
        WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount_usd
        WHEN "to" = 0x0000000000000000000000000000000000000000 THEN -amount_usd
        ELSE 0
    END), 0) AS net_flow_usd
FROM stablecoins_multichain.transfers
WHERE blockchain = 'ethereum'
    AND token_symbol = 'USDC'
    AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY 1
ORDER BY 1
