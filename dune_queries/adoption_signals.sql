-- Stablecoin Adoption Signals — PSP, Card Network, and Settlement Platform Tracking
-- Monitors on-chain activity from known institutional wallets
-- Supplements manual tracking of partnerships and announcements

-- Query 1: USDC transfers involving known institutional addresses
-- This is a starting point — expand with verified addresses
WITH known_institutions AS (
    SELECT address, label FROM (VALUES
        (0xA7e8DDd6B1Cc2Be38E58F6D246Fd12bB8c250316, 'Circle Treasury'),
        (0x55FE002aefF02F77364de339a1292923A15844B8, 'Circle USDC Reserve'),
        (0x5B541d54e79052B34d7dEf2a6ffC5b47b199F862, 'Stripe'),
        (0x0D0707963952f2fBA59dD06f2b425ace40b492Fe, 'Gate.io'),
        (0xDFd5293D8e347dFe59E90eFd55b2956a1343963d, 'Coinbase Prime'),
        (0x28C6c06298d514Db089934071355E5743bf21d60, 'Binance'),
        (0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549, 'Bitfinex')
    ) AS t(address, label)
)
SELECT
    date_trunc('day', e.block_time) AS day,
    ki.label AS institution,
    CASE
        WHEN e."from" = ki.address THEN 'OUTFLOW'
        ELSE 'INFLOW'
    END AS direction,
    SUM(e.value / 1e6) AS volume_usd,
    COUNT(*) AS tx_count
FROM erc20_ethereum.evt_Transfer e
JOIN known_institutions ki ON (e."from" = ki.address OR e."to" = ki.address)
WHERE e.contract_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC
    AND e.block_time >= NOW() - INTERVAL '30' DAY
    AND e.value / 1e6 > 100000  -- >$100K transfers only
GROUP BY 1, 2, 3
ORDER BY 1 DESC, volume_usd DESC;

-- Query 2: Circle CCTP (Cross-Chain Transfer Protocol) volume
-- Tracks USDC moving between chains via Circle's native bridge
-- Signals which chains are seeing institutional inflows
SELECT
    date_trunc('day', block_time) AS day,
    -- Source chain is Ethereum (this query), destination parsed from event
    SUM(amount / 1e6) AS usdc_bridged_usd,
    COUNT(*) AS bridge_tx_count
FROM ethereum.logs
WHERE contract_address = 0xBd3fa81B58Ba92a82136038B25aDec7066af3155  -- CCTP TokenMessenger on Ethereum
    AND topic0 = 0x2fa9ca894982930190727e75500a97d8dc500233a5065e0f3126c48fbe0343c0  -- DepositForBurn event
    AND block_time >= NOW() - INTERVAL '90' DAY
GROUP BY 1
ORDER BY 1;

-- Query 3: New USDC holder growth by chain (proxy for adoption)
-- Counts unique addresses receiving USDC for the first time
SELECT
    date_trunc('week', first_received) AS week,
    COUNT(*) AS new_usdc_holders
FROM (
    SELECT
        "to" AS address,
        MIN(block_time) AS first_received
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
        AND block_time >= NOW() - INTERVAL '180' DAY
    GROUP BY 1
) first_transfers
WHERE first_received >= NOW() - INTERVAL '180' DAY
GROUP BY 1
ORDER BY 1;
