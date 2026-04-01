-- Whale Concentration Analysis — USDC & USDT
-- Tracks concentration risk: how much supply is held by top wallets
-- Key metric for Circle's reserve/distribution risk monitoring

-- Query 1: Top 50 USDC holders on Ethereum (current)
SELECT
    address,
    balance / 1e6 AS balance_usd,
    balance / 1e6 / (SELECT SUM(balance) / 1e6 FROM tokens.erc20_balances WHERE token_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 AND balance > 0) * 100 AS pct_of_supply,
    -- Label known addresses
    CASE
        WHEN address = 0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503 THEN 'Binance Hot Wallet'
        WHEN address = 0x28C6c06298d514Db089934071355E5743bf21d60 THEN 'Binance'
        WHEN address = 0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549 THEN 'Bitfinex'
        WHEN address = 0xDFd5293D8e347dFe59E90eFd55b2956a1343963d THEN 'Coinbase'
        WHEN address = 0xA7e8DDd6B1Cc2Be38E58F6D246Fd12bB8c250316 THEN 'Circle Treasury'
        ELSE 'Unknown'
    END AS label
FROM tokens.erc20_balances
WHERE token_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC
    AND balance > 0
ORDER BY balance DESC
LIMIT 50;

-- Query 2: Concentration metrics — Gini-style analysis
-- What % of supply is held by top 10, 50, 100 wallets?
WITH ranked AS (
    SELECT
        address,
        balance / 1e6 AS balance_usd,
        ROW_NUMBER() OVER (ORDER BY balance DESC) AS rank
    FROM tokens.erc20_balances
    WHERE token_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
        AND balance > 0
),
total AS (
    SELECT SUM(balance_usd) AS total_supply FROM ranked
)
SELECT
    'Top 10' AS tier,
    SUM(r.balance_usd) AS tier_supply,
    SUM(r.balance_usd) / t.total_supply * 100 AS pct_of_total
FROM ranked r, total t
WHERE r.rank <= 10
UNION ALL
SELECT
    'Top 50',
    SUM(r.balance_usd),
    SUM(r.balance_usd) / t.total_supply * 100
FROM ranked r, total t
WHERE r.rank <= 50
UNION ALL
SELECT
    'Top 100',
    SUM(r.balance_usd),
    SUM(r.balance_usd) / t.total_supply * 100
FROM ranked r, total t
WHERE r.rank <= 100
UNION ALL
SELECT
    'All others',
    SUM(r.balance_usd),
    SUM(r.balance_usd) / t.total_supply * 100
FROM ranked r, total t
WHERE r.rank > 100;

-- Query 3: Large transfer alerts (>$10M USDC movements in last 7 days)
SELECT
    block_time,
    "from" AS sender,
    "to" AS receiver,
    value / 1e6 AS amount_usd,
    tx_hash
FROM erc20_ethereum.evt_Transfer
WHERE contract_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC
    AND value / 1e6 > 10000000  -- > $10M
    AND block_time >= NOW() - INTERVAL '7' DAY
ORDER BY value DESC;
