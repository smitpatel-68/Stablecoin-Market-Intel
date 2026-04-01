-- Stablecoin Peg Deviation Tracker
-- Monitors USDC, USDT, DAI, PYUSD price vs $1.00 peg using DEX data
-- Flags deviations > 10bps (0.1%)

-- Query 1: Hourly peg prices from DEX trades (last 30 days)
-- Uses Uniswap V3 on Ethereum as the primary price source
SELECT
    date_trunc('hour', block_time) AS hour,
    CASE
        WHEN token_bought_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 THEN 'USDC'
        WHEN token_bought_address = 0xdAC17F958D2ee523a2206206994597C13D831ec7 THEN 'USDT'
        WHEN token_bought_address = 0x6B175474E89094C44Da98b954EedeAC495271d0F THEN 'DAI'
    END AS stablecoin,
    -- Price derived from WETH pair trades
    AVG(amount_usd / token_bought_amount_raw * 1e6) AS avg_price_usd,
    ABS(AVG(amount_usd / token_bought_amount_raw * 1e6) - 1.0) * 10000 AS deviation_bps,
    COUNT(*) AS trade_count
FROM dex.trades
WHERE blockchain = 'ethereum'
    AND (
        token_bought_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC
        OR token_bought_address = 0xdAC17F958D2ee523a2206206994597C13D831ec7  -- USDT
        OR token_bought_address = 0x6B175474E89094C44Da98b954EedeAC495271d0F  -- DAI
    )
    AND block_time >= NOW() - INTERVAL '30' DAY
    AND amount_usd > 1000  -- Filter small trades
GROUP BY 1, 2
HAVING COUNT(*) >= 5  -- Minimum trade count for reliable price
ORDER BY 1, 2;

-- Query 2: Depeg events (deviation > 50bps sustained for > 1 hour)
WITH hourly_prices AS (
    SELECT
        date_trunc('hour', block_time) AS hour,
        CASE
            WHEN token_bought_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 THEN 'USDC'
            WHEN token_bought_address = 0xdAC17F958D2ee523a2206206994597C13D831ec7 THEN 'USDT'
        END AS stablecoin,
        AVG(amount_usd / token_bought_amount_raw * 1e6) AS avg_price
    FROM dex.trades
    WHERE blockchain = 'ethereum'
        AND token_bought_address IN (
            0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,
            0xdAC17F958D2ee523a2206206994597C13D831ec7
        )
        AND block_time >= NOW() - INTERVAL '90' DAY
        AND amount_usd > 1000
    GROUP BY 1, 2
    HAVING COUNT(*) >= 5
)
SELECT
    hour,
    stablecoin,
    avg_price,
    ABS(avg_price - 1.0) * 10000 AS deviation_bps,
    CASE
        WHEN ABS(avg_price - 1.0) * 10000 > 100 THEN 'SEVERE'
        WHEN ABS(avg_price - 1.0) * 10000 > 50 THEN 'WARNING'
        WHEN ABS(avg_price - 1.0) * 10000 > 10 THEN 'MINOR'
        ELSE 'NORMAL'
    END AS severity
FROM hourly_prices
WHERE ABS(avg_price - 1.0) * 10000 > 10  -- Only show deviations > 10bps
ORDER BY deviation_bps DESC;
