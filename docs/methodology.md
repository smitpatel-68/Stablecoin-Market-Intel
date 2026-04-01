# Methodology & Data Sources

## Scoring Models

### Peg Stability Score (0–100)

The peg stability score quantifies how reliably a stablecoin maintains its $1.00 peg. It combines current state with recent history.

**Calculation:**
```
score = 100
score -= (current_deviation_bps × 5)      # Current price penalty
score -= (depeg_events_90d × 10)           # Event frequency penalty  
score -= (worst_deviation_pct × 20)        # Severity penalty
score = clamp(0, 100)
```

**Risk bands:**

| Score | Risk Level | Interpretation |
|---|---|---|
| 90–100 | LOW | Peg is stable. No recent events. |
| 70–89 | MEDIUM | Minor deviations or isolated events. Monitor. |
| 50–69 | HIGH | Significant peg stress. Escalate to risk team. |
| 0–49 | CRITICAL | Active depeg or severe instability. Immediate action required. |

**Design rationale:** The score weights recent events heavily because peg stability is path-dependent — a stablecoin that depegged last month is fundamentally riskier than one that didn't, even if both are at $1.00 today. The scoring intentionally penalizes event frequency more than magnitude because repeated small deviations signal structural weakness.

### Competitor Threat Assessment

Scores each non-USDC stablecoin's competitive threat to Circle.

| Threat Level | Criteria |
|---|---|
| HIGH | >50% market dominance (only USDT qualifies) OR >5% dominance + regulatory standing of STRONG or MODERATE |
| MEDIUM | >2% market dominance |
| LOW | <2% market dominance |

**Reserve transparency ratings** are based on auditor quality and frequency:
- HIGH: Big Four auditor + monthly attestation (e.g., Deloitte for USDC, PwC for BUIDL)
- MEDIUM: Reputable auditor + quarterly attestation, or fully on-chain verifiable
- LOW: Disputed audits, no regular attestation, or unverifiable claims

**Regulatory standing** is assessed based on licensing and compliance posture:
- STRONG: Licensed in multiple major jurisdictions (US, EU, Singapore)
- MODERATE: Licensed in at least one jurisdiction or in active compliance process
- WEAK: No licenses, regulatory scrutiny, or deliberate regulatory avoidance
- NONE: Decentralized governance, no regulatory relationship by design

### Early Warning Triggers

Each trigger has defined thresholds:

| Trigger | Threshold | Severity |
|---|---|---|
| USDC market share declining vs USDT | Growth differential >3pp over 90 days | HIGH |
| Peg instability | Stability score <50 | CRITICAL |
| Peg instability | Stability score 50–69 | HIGH |
| Chain concentration | Single chain >40% of total supply | MEDIUM |
| Regulatory change imminent | Framework with 2026 implementation date | MEDIUM |
| New competitor traction | Supply exceeding $400M | MEDIUM |

---

## Data Sources

### DefiLlama Stablecoins API (Primary)

**Endpoints used:**
- `GET /stablecoins` — All stablecoins with current circulating supply and prices
- `GET /stablecoin/{id}` — Detailed data per stablecoin including chain breakdown and history
- `GET /stablecoinchains` — Stablecoin supply per blockchain
- `GET /stablecoincharts/all` — Historical total supply
- `GET /stablecoinprices` — Historical prices for peg tracking

**Refresh frequency:** Hourly (DefiLlama updates supply data hourly)
**Rate limits:** No authentication required. Reasonable rate limiting applies.
**Reliability:** DefiLlama is the industry standard for DeFi data. Used by institutional investors, exchanges, and research firms.

### Dune Analytics (Supplementary)

**Tables used:**
- `erc20_ethereum.evt_Transfer` — ERC-20 transfer events for mint/burn and whale tracking
- `tokens.erc20_balances` — Current token balances per address
- `dex.trades` — DEX trading data for real-time peg pricing
- `stablecoin.balances` — Dune's curated stablecoin dataset (launched March 2026)
- `ethereum.logs` — Raw event logs for CCTP bridge monitoring

**Access:** Free tier for manual queries. API key required for programmatic access ($39/month for Plus plan).

### Manual Intelligence (Curated)

**Regulatory tracker** is maintained manually based on:
- Government gazette publications and legislative texts
- FATF mutual evaluation reports and guidance
- Central bank announcements (Fed, ECB, MAS, FCA, HKMA, VARA, etc.)
- Industry reporting (CoinDesk, The Block, Decrypt)

**Update frequency:** Weekly review, immediate update for material changes.

---

## Limitations

1. **Supply data is approximate.** DefiLlama aggregates from multiple on-chain sources. Discrepancies of 1-3% between DefiLlama and issuer-reported supply are normal due to timing differences and bridge accounting.

2. **Peg pricing from DEX trades is noisy.** Low-liquidity pools can show misleading deviations. The engine requires minimum trade counts per hour to filter noise.

3. **Chain migration signals are directional, not precise.** "GROWING" and "DECLINING" labels are based on known industry trends, not real-time inflow/outflow calculations (which would require Dune API access).

4. **Regulatory tracker requires manual maintenance.** Automated legislative monitoring is not implemented. The tracker reflects status as of the last manual update.

5. **Competitor dossiers are summary-level.** Deep competitor analysis (GTM strategy, partnership pipeline, product roadmap) requires additional research beyond what on-chain data provides.
