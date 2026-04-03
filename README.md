# 🔍 Stablecoin Market & Ecosystem Intelligence

> A market intelligence platform that transforms fragmented stablecoin market signals into decision-grade insights — covering market share dynamics, chain migration, peg stability, competitive positioning, regulatory tracking, and early warning systems.

**Live Dashboard:** [Stablecoin Market Intelligence on Dune Analytics](https://dune.com/enceladus68/stablecoin-market-intel)

---

## What This Does

The platform monitors the stablecoin ecosystem across six intelligence dimensions:

1. **Market share analysis** — USDC vs USDT dominance shifts, 90-day growth comparisons, and market structure signals
2. **Chain migration detection** — Where is stablecoin supply flowing? Which chains are gaining (Solana, Base, TON) and which are losing share (BSC, Polygon)?
3. **Peg stability scoring** — Real-time peg health with a 0-100 scoring system, deviation tracking in basis points, and depeg event history
4. **Competitor scorecards** — USDT, USDC, DAI, USDe, PYUSD, FDUSD, BUIDL scored on reserve transparency, regulatory standing, chain coverage, and threat level
5. **Early warning triggers** — Automated alerts for market share shifts, peg instability, chain concentration risk, regulatory changes, and competitor traction
6. **Regulatory tracker** — 12 jurisdictions mapped: US (GENIUS Act), EU (MiCA), Singapore (MAS), UK, Hong Kong, UAE, Japan, Brazil, India, Canada, Australia, South Korea

---

## Quick Start

```bash
# Run the full intelligence analysis
python -m engine.market_intelligence

# Generate an executive-ready markdown report
python -m engine.report_generator

# Fetch live data from DefiLlama (requires internet)
python engine/data_fetcher.py
```

The analysis engine works out of the box with curated sample data (sourced from real DefiLlama snapshots). When connected to the internet, the data fetcher pulls live supply, chain distribution, and pricing data.

---

## Sample Output

Running `python -m engine.market_intelligence` produces:

```
SECTION 1: MARKET SHARE ANALYSIS
  Total stablecoin supply:     $235,400,000,000
  USDT supply:                 $144,200,000,000 (61.3%)
  USDC supply:                 $60,800,000,000 (25.8%)
  
  90-day growth:
    USDC:                      +16.9%
    USDT:                      +12.7%
  
  Signal: USDC_GAINING
  Insight: USDC is growing faster than USDT (16.9% vs 12.7%)...

SECTION 5: EARLY WARNING TRIGGERS
  🔴 [CRITICAL] PEG_INSTABILITY
    TUSD peg stability score: 0/100. 1 depeg events in 90 days.
    Worst deviation: 1.5%. Current price: $0.9985
    Action: Monitor TUSD reserve disclosures...
```

---

## Dune SQL Queries

The `/dune_queries` directory contains production-ready SQL for Dune Analytics:

| Query | What it tracks |
|---|---|
| `usdc_supply.sql` | USDC supply by chain, daily mint/burn, cross-chain distribution |
| `peg_deviation.sql` | Peg prices from DEX trades and balance data, depeg event detection |
| `whale_concentration.sql` | Top holders, Gini-style concentration tiers, large transfer alerts |
| `market_share.sql` | Stablecoin dominance, USDC vs USDT per chain, market structure |
| `adoption_signals.sql` | Transfer volume by chain, size bucket analysis, whale alerts |

All queries use Dune's `stablecoins_multichain.balances` and `stablecoins_multichain.transfers` tables, providing full cross-chain coverage including Ethereum, Solana, Tron, Base, Arbitrum, and 30+ chains.

---

## Live Dune Dashboard

The [Stablecoin Market Intelligence dashboard](https://dune.com/enceladus68/stablecoin-market-intel) on Dune Analytics includes interactive visualizations covering:

- **USDC Supply by Chain** — Distribution across Ethereum, Solana, Base, Arbitrum, Polygon, and more
- **Stablecoin Market Share** — USDC vs USDT vs DAI vs USDe dominance
- **USDC vs USDT by Chain** — Which stablecoin dominates on each chain
- **Top USDC Holders** — Whale concentration on Ethereum
- **Holder Distribution** — Breakdown by size bucket (micro to whale)
- **Supply & Holder Overview** — Total supply, chains, and holder comparison

All data is live and refreshed from on-chain sources.

---

## Intelligence Reports

Run `python -m engine.report_generator` to produce a structured markdown report with:

- Executive summary with key metrics and critical alerts
- Market share dynamics table
- Chain distribution with migration signals
- Peg stability scorecards (0-100 scoring)
- Competitor scorecards with threat assessment
- Early warning triggers with recommended actions
- 12-jurisdiction regulatory tracker

Reports are saved to `/reports` with timestamps.

---

## Repo Structure

```
stablecoin-intel/
├── README.md
├── engine/
│   ├── __init__.py
│   ├── data_fetcher.py           ← Live data from DefiLlama API
│   ├── market_intelligence.py    ← Core analysis engine (6 sections)
│   └── report_generator.py       ← Executive-ready markdown reports
├── dune_queries/
│   ├── usdc_supply.sql           ← USDC supply by chain + mint/burn
│   ├── peg_deviation.sql         ← Peg tracking from DEX data
│   ├── whale_concentration.sql   ← Top holders + concentration metrics
│   ├── market_share.sql          ← Stablecoin dominance over time
│   └── adoption_signals.sql      ← Transfer flows + adoption metrics
├── reports/                      ← Auto-generated intelligence reports
├── data/                         ← Cached API responses
└── docs/
    └── methodology.md            ← Scoring models + data source documentation
```

---

## Methodology

### Peg Stability Score (0-100)
- Base: 100 (perfect peg)
- Deductions: current deviation (5 pts per basis point), event count (10 pts each), worst event severity (20 pts per %)
- Risk bands: LOW (90-100), MEDIUM (70-89), HIGH (50-69), CRITICAL (0-49)

### Competitor Threat Assessment
- HIGH: >50% dominance OR (>5% dominance + strong/moderate regulatory standing)
- MEDIUM: >2% dominance
- LOW: <2% dominance

### Early Warning Triggers
- Market share shift: Growth differential >3pp over 90 days
- Peg instability: Any stablecoin with stability score <70
- Chain concentration: Single chain holding >40% of total supply
- Regulatory change: Frameworks with 2026 implementation dates
- Competitor traction: New entrants exceeding $400M supply

---

## Data Sources

| Source | What | Access |
|---|---|---|
| DefiLlama Stablecoins API | Supply, chain distribution, prices | Free, no API key |
| Dune Analytics | On-chain transfers, DEX volume, holder data | Free tier (limited), API key for automation |
| Manual monitoring | Regulatory developments, partnership announcements | Curated in regulatory tracker |

---

*Product case study demonstrating market intelligence, on-chain analytics, and competitive analysis capability for the stablecoin ecosystem.*
