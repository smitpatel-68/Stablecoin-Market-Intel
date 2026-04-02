-- ⚠️ DUNE USAGE: Each query below must be run SEPARATELY on Dune Analytics.
-- Table: stablecoins_multichain.balances, prices.usd

-- Query 1: Current stablecoin peg check (implied price from balance vs balance_usd)
-- Visualization: Table with color coding by peg_status
SELECT
    token_symbol,
    ROUND(AVG(balance_usd / NULLIF(balance, 0)), 6) AS implied_price,
    ROUND(ABS(AVG(balance_usd / NULLIF(balance, 0)) - 1.0) * 10000, 1) AS deviation_bps,
    CASE
        WHEN ABS(AVG(balance_usd / NULLIF(balance, 0)) - 1.0) * 10000 > 100 THEN 'SEVERE'
        WHEN ABS(AVG(balance_usd / NULLIF(balance, 0)) - 1.0) * 10000 > 50 THEN 'WARNING'
        WHEN ABS(AVG(balance_usd / NULLIF(balance, 0)) - 1.0) * 10000 > 10 THEN 'MINOR'
        ELSE 'STABLE'
    END AS peg_status
FROM stablecoins_multichain.balances
WHERE blockchain = 'ethereum'
    AND token_symbol IN ('USDC', 'USDT', 'DAI', 'PYUSD', 'FRAX')
    AND balance > 1000
    AND balance_usd > 0
    AND day = (SELECT MAX(day) FROM stablecoins_multichain.balances WHERE token_symbol = 'USDC')
GROUP BY 1
ORDER BY deviation_bps DESC

-- Query 2: Stablecoin prices from prices.usd table (last 7 days)
-- More accurate — uses actual market prices
-- Visualization: Line chart | X: day, Y: avg_price, series: symbol
SELECT
    date_trunc('day', minute) AS day,
    symbol,
    ROUND(AVG(price), 6) AS avg_price,
    ROUND(MIN(price), 6) AS min_price,
    ROUND(MAX(price), 6) AS max_price
FROM prices.usd
WHERE symbol IN ('USDC', 'USDT', 'DAI', 'PYUSD')
    AND blockchain = 'ethereum'
    AND minute >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY 1, 2
ORDER BY 1, 2
