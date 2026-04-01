-- USDC Supply by Chain — Last 12 Months (Daily)
-- Tracks USDC (Circle) circulating supply across major chains
-- Use on Dune Analytics: https://dune.com
-- Table: dune.stablecoin.stablecoin_balances (Dune's new stablecoin dataset, March 2026)
-- Alternative: tokens.erc20_supply for Ethereum/EVM chains

-- Query 1: USDC total supply over time (Ethereum)
SELECT
    date_trunc('day', block_time) AS day,
    SUM(balance) / 1e6 AS usdc_supply_usd  -- USDC has 6 decimals
FROM tokens.erc20_daily_balances
WHERE token_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC on Ethereum
    AND block_time >= NOW() - INTERVAL '365' DAY
GROUP BY 1
ORDER BY 1;

-- Query 2: USDC supply breakdown by chain (latest snapshot)
-- Uses Dune's cross-chain stablecoin dataset
SELECT
    blockchain,
    symbol,
    SUM(balance_usd) AS total_supply_usd,
    COUNT(DISTINCT address) AS unique_holders
FROM stablecoin.balances
WHERE symbol = 'USDC'
    AND balance_usd > 0
GROUP BY 1, 2
ORDER BY total_supply_usd DESC;

-- Query 3: USDC daily mint/burn on Ethereum
-- Mints = transfers FROM the zero address
-- Burns = transfers TO the zero address
SELECT
    date_trunc('day', block_time) AS day,
    SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value / 1e6 ELSE 0 END) AS minted_usd,
    SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN value / 1e6 ELSE 0 END) AS burned_usd,
    SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value / 1e6 ELSE 0 END)
    - SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN value / 1e6 ELSE 0 END) AS net_change_usd
FROM erc20_ethereum.evt_Transfer
WHERE contract_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    AND block_time >= NOW() - INTERVAL '90' DAY
GROUP BY 1
ORDER BY 1;
