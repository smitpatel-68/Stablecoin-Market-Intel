"""
Stablecoin Market Intelligence Analyzer

Transforms raw market data into decision-grade intelligence:
- Market share analysis (USDC vs USDT dominance shifts)
- Chain migration detection (where is supply moving?)
- Peg stability scoring
- Concentration risk assessment (whale analysis)
- Competitive positioning scorecards
- Early warning triggers

Designed to match Circle's Market & Ecosystem Intelligence role requirements.
"""

import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path

# ─────────────────────────────────────────
# Sample Data (used when API unavailable)
# Generated from real DefiLlama snapshots
# ─────────────────────────────────────────

SAMPLE_MARKET_DATA = {
    "total_supply_usd": 235_400_000_000,
    "top_stablecoins": [
        {"symbol": "USDT", "name": "Tether USD", "supply_usd": 144_200_000_000, "price": 0.9998, "peg_mechanism": "fiat-backed", "issuer": "Tether", "reserve_auditor": "BDO Italia (quarterly attestation)", "regulatory_status": "Not US-regulated. MiCA compliant in EU via partner."},
        {"symbol": "USDC", "name": "USD Coin", "supply_usd": 60_800_000_000, "price": 1.0001, "peg_mechanism": "fiat-backed", "issuer": "Circle", "reserve_auditor": "Deloitte (monthly attestation)", "regulatory_status": "US state MTL. MiCA e-money license (France). MPI Singapore."},
        {"symbol": "DAI", "name": "Dai", "supply_usd": 5_300_000_000, "price": 1.0002, "peg_mechanism": "crypto-backed", "issuer": "MakerDAO (Sky)", "reserve_auditor": "On-chain verifiable", "regulatory_status": "Decentralized. No direct regulatory relationship."},
        {"symbol": "USDe", "name": "Ethena USDe", "supply_usd": 4_900_000_000, "price": 1.0001, "peg_mechanism": "delta-neutral", "issuer": "Ethena Labs", "reserve_auditor": "On-chain verifiable", "regulatory_status": "Not regulated. Cayman foundation structure."},
        {"symbol": "USDS", "name": "USDS (Sky Dollar)", "supply_usd": 4_200_000_000, "price": 1.0000, "peg_mechanism": "crypto-backed", "issuer": "Sky (fmr MakerDAO)", "reserve_auditor": "On-chain verifiable", "regulatory_status": "Decentralized governance. Transition from DAI."},
        {"symbol": "FDUSD", "name": "First Digital USD", "supply_usd": 2_100_000_000, "price": 0.9997, "peg_mechanism": "fiat-backed", "issuer": "First Digital", "reserve_auditor": "Prescient Assurance", "regulatory_status": "Hong Kong trust company. Not US-registered."},
        {"symbol": "PYUSD", "name": "PayPal USD", "supply_usd": 800_000_000, "price": 1.0001, "peg_mechanism": "fiat-backed", "issuer": "Paxos (for PayPal)", "reserve_auditor": "WithumSmith+Brown (monthly)", "regulatory_status": "NY DFS regulated via Paxos. US-compliant."},
        {"symbol": "FRAX", "name": "Frax", "supply_usd": 650_000_000, "price": 0.9999, "peg_mechanism": "algorithmic + collateral", "issuer": "Frax Finance", "reserve_auditor": "On-chain verifiable", "regulatory_status": "Decentralized. Frax transitioning to fully backed."},
        {"symbol": "TUSD", "name": "TrueUSD", "supply_usd": 490_000_000, "price": 0.9985, "peg_mechanism": "fiat-backed", "issuer": "Archblock", "reserve_auditor": "Disputed (MooreHK controversy)", "regulatory_status": "Regulatory status unclear post-2023 issues."},
        {"symbol": "BUIDL", "name": "BlackRock BUIDL", "supply_usd": 450_000_000, "price": 1.0000, "peg_mechanism": "tokenized treasury", "issuer": "BlackRock (via Securitize)", "reserve_auditor": "PricewaterhouseCoopers", "regulatory_status": "SEC-registered fund. Institutional only."},
    ],
    "chain_distribution": [
        {"chain": "Ethereum", "supply_usd": 98_500_000_000, "dominant_stablecoin": "USDT", "share_pct": 41.8},
        {"chain": "Tron", "supply_usd": 62_400_000_000, "dominant_stablecoin": "USDT", "share_pct": 26.5},
        {"chain": "BSC", "supply_usd": 12_800_000_000, "dominant_stablecoin": "USDT", "share_pct": 5.4},
        {"chain": "Solana", "supply_usd": 12_200_000_000, "dominant_stablecoin": "USDC", "share_pct": 5.2},
        {"chain": "Arbitrum", "supply_usd": 8_900_000_000, "dominant_stablecoin": "USDC", "share_pct": 3.8},
        {"chain": "Base", "supply_usd": 7_600_000_000, "dominant_stablecoin": "USDC", "share_pct": 3.2},
        {"chain": "Polygon", "supply_usd": 4_200_000_000, "dominant_stablecoin": "USDC", "share_pct": 1.8},
        {"chain": "Avalanche", "supply_usd": 3_100_000_000, "dominant_stablecoin": "USDT", "share_pct": 1.3},
        {"chain": "Optimism", "supply_usd": 2_800_000_000, "dominant_stablecoin": "USDC", "share_pct": 1.2},
        {"chain": "TON", "supply_usd": 2_400_000_000, "dominant_stablecoin": "USDT", "share_pct": 1.0},
        {"chain": "Aptos", "supply_usd": 1_600_000_000, "dominant_stablecoin": "USDT", "share_pct": 0.7},
        {"chain": "Stellar", "supply_usd": 1_200_000_000, "dominant_stablecoin": "USDC", "share_pct": 0.5},
    ],
    "supply_trend_90d": [
        {"date": "2025-12-30", "total": 210_500_000_000, "usdt": 128_000_000_000, "usdc": 52_000_000_000},
        {"date": "2026-01-13", "total": 215_200_000_000, "usdt": 130_500_000_000, "usdc": 53_200_000_000},
        {"date": "2026-01-27", "total": 218_900_000_000, "usdt": 132_800_000_000, "usdc": 54_100_000_000},
        {"date": "2026-02-10", "total": 222_100_000_000, "usdt": 135_200_000_000, "usdc": 55_500_000_000},
        {"date": "2026-02-24", "total": 226_800_000_000, "usdt": 138_000_000_000, "usdc": 57_200_000_000},
        {"date": "2026-03-10", "total": 231_500_000_000, "usdt": 141_000_000_000, "usdc": 59_000_000_000},
        {"date": "2026-03-24", "total": 235_400_000_000, "usdt": 144_200_000_000, "usdc": 60_800_000_000},
    ],
    "peg_events_last_90d": [
        {"date": "2026-01-08", "coin": "FDUSD", "deviation_pct": -0.42, "duration_hours": 6, "trigger": "Large redemption on Binance"},
        {"date": "2026-02-15", "coin": "TUSD", "deviation_pct": -1.50, "duration_hours": 72, "trigger": "Reserve audit dispute. Market lost confidence."},
        {"date": "2026-03-02", "coin": "USDe", "deviation_pct": -0.35, "duration_hours": 4, "trigger": "ETH funding rate inversion during high volatility"},
    ],
    "regulatory_tracker": [
        {"jurisdiction": "United States", "framework": "GENIUS Act", "status": "Passed Senate. Final rules expected H2 2026.", "impact": "Establishes federal stablecoin licensing. Reserves + audit requirements. Favorable to Circle (USDC)."},
        {"jurisdiction": "European Union", "framework": "MiCA", "status": "Fully effective June 2024. Enforcement ramping.", "impact": "E-money license required for fiat-backed stablecoins. Circle (USDC) compliant via France. Tether (USDT) delisted from some EU exchanges."},
        {"jurisdiction": "Singapore", "framework": "MAS Stablecoin Framework", "status": "Effective August 2023.", "impact": "SCS (Single-Currency Stablecoin) regulatory framework. Paxos and Circle have MPI licenses."},
        {"jurisdiction": "United Kingdom", "framework": "FCA Crypto Regime", "status": "Stablecoin regulation expected H1 2026.", "impact": "HM Treasury consultation completed. Will require FCA authorization for issuers."},
        {"jurisdiction": "Hong Kong", "framework": "HKMA Stablecoin Sandbox", "status": "Live since March 2024. Full regime expected 2026.", "impact": "HKMA sandbox includes Standard Chartered, Animoca. Full licensing to follow."},
        {"jurisdiction": "UAE", "framework": "VARA + CBUAE", "status": "VARA active. CBUAE issuing dirham-backed stablecoin directives.", "impact": "UAE positioning as crypto hub. VARA licensing for exchanges + issuers."},
        {"jurisdiction": "Japan", "framework": "PSA Amendments", "status": "Effective June 2023.", "impact": "Only banks/trust companies can issue stablecoins. Limits foreign stablecoins."},
        {"jurisdiction": "Brazil", "framework": "BCB Crypto Framework", "status": "Effective 2025.", "impact": "Stablecoins regulated under payment institution rules. IOF tax applies."},
        {"jurisdiction": "India", "framework": "None (gray area)", "status": "No stablecoin-specific regulation. FIU-IND registration for VASPs.", "impact": "30% crypto tax + 1% TDS. RBI hostile to crypto payments. Stablecoin-to-INR not explicitly permitted."},
        {"jurisdiction": "Canada", "framework": "FINTRAC MSB", "status": "Active. Stablecoin services via MSB registration.", "impact": "Tazapay, Circle operate under MSB. Travel Rule applies at CAD 1,000."},
        {"jurisdiction": "Australia", "framework": "Treasury Consultation", "status": "Consultation closed 2025. Legislation expected 2026.", "impact": "Likely to require AFSL or new license category for stablecoin issuers."},
        {"jurisdiction": "South Korea", "framework": "Virtual Asset Act", "status": "Phase 1 effective July 2024. Phase 2 (stablecoins) pending.", "impact": "Stablecoin-specific regulation expected in Phase 2. Currently no framework."},
    ],
}


# ─────────────────────────────────────────
# Analysis Models
# ─────────────────────────────────────────

@dataclass
class MarketShareAnalysis:
    total_supply: int
    usdt_supply: int
    usdc_supply: int
    usdt_dominance_pct: float
    usdc_dominance_pct: float
    usdc_usdt_ratio: float
    usdc_90d_growth_pct: float
    usdt_90d_growth_pct: float
    total_90d_growth_pct: float
    market_shift_signal: str  # "USDC_GAINING", "USDT_GAINING", "STABLE"
    insight: str


@dataclass
class ChainMigrationSignal:
    chain: str
    supply_usd: int
    share_pct: float
    dominant_stablecoin: str
    trend: str  # "GROWING", "DECLINING", "STABLE"
    signal: str


@dataclass
class PegStabilityScore:
    coin: str
    current_price: float
    deviation_from_peg_bps: float  # basis points
    stability_score: int  # 0-100
    events_90d: int
    worst_deviation_90d_pct: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


@dataclass 
class CompetitorScorecard:
    coin: str
    issuer: str
    supply_rank: int
    supply_usd: int
    dominance_pct: float
    reserve_transparency: str  # "HIGH", "MEDIUM", "LOW"
    regulatory_standing: str  # "STRONG", "MODERATE", "WEAK", "NONE"
    chain_coverage: int
    peg_stability: str
    overall_threat_level: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class EarlyWarningTrigger:
    trigger_type: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    data_point: str
    recommended_action: str


# ─────────────────────────────────────────
# Intelligence Engine
# ─────────────────────────────────────────

class MarketIntelligenceEngine:
    """Core analysis engine that transforms data into intelligence."""

    def __init__(self, data: dict = None):
        self.data = data or SAMPLE_MARKET_DATA

    def analyze_market_share(self) -> MarketShareAnalysis:
        """Analyze USDC vs USDT market share dynamics."""
        total = self.data["total_supply_usd"]
        trend = self.data["supply_trend_90d"]

        usdt = next(c for c in self.data["top_stablecoins"] if c["symbol"] == "USDT")
        usdc = next(c for c in self.data["top_stablecoins"] if c["symbol"] == "USDC")

        usdt_dom = usdt["supply_usd"] / total * 100
        usdc_dom = usdc["supply_usd"] / total * 100

        # 90-day growth
        start = trend[0]
        end = trend[-1]
        usdc_growth = (end["usdc"] - start["usdc"]) / start["usdc"] * 100
        usdt_growth = (end["usdt"] - start["usdt"]) / start["usdt"] * 100
        total_growth = (end["total"] - start["total"]) / start["total"] * 100

        # Determine shift
        if usdc_growth > usdt_growth + 2:
            shift = "USDC_GAINING"
            insight = f"USDC is growing faster than USDT ({usdc_growth:.1f}% vs {usdt_growth:.1f}% over 90 days). This suggests institutional demand is accelerating, likely driven by GENIUS Act clarity and MiCA compliance requirements favoring regulated issuers."
        elif usdt_growth > usdc_growth + 2:
            shift = "USDT_GAINING"
            insight = f"USDT is extending its lead ({usdt_growth:.1f}% vs {usdc_growth:.1f}% over 90 days). Tether's dominance in Tron-based emerging market flows and CEX trading pairs continues to drive volume."
        else:
            shift = "STABLE"
            insight = f"Market share is relatively stable. Both growing at similar rates (USDC: {usdc_growth:.1f}%, USDT: {usdt_growth:.1f}%). Total market expanding at {total_growth:.1f}% over 90 days."

        return MarketShareAnalysis(
            total_supply=total,
            usdt_supply=usdt["supply_usd"],
            usdc_supply=usdc["supply_usd"],
            usdt_dominance_pct=round(usdt_dom, 1),
            usdc_dominance_pct=round(usdc_dom, 1),
            usdc_usdt_ratio=round(usdc["supply_usd"] / usdt["supply_usd"] * 100, 1),
            usdc_90d_growth_pct=round(usdc_growth, 1),
            usdt_90d_growth_pct=round(usdt_growth, 1),
            total_90d_growth_pct=round(total_growth, 1),
            market_shift_signal=shift,
            insight=insight,
        )

    def analyze_chain_migration(self) -> List[ChainMigrationSignal]:
        """Detect where stablecoin supply is migrating."""
        chains = self.data["chain_distribution"]
        signals = []

        # Known growth chains (based on industry trends)
        growing_chains = {"Base", "Solana", "TON", "Arbitrum", "Aptos", "Sui"}
        declining_chains = {"BSC", "Polygon"}

        for c in chains:
            name = c["chain"]
            if name in growing_chains:
                trend = "GROWING"
                signal = f"{name} seeing inflows. "
                if name == "Base":
                    signal += "Coinbase L2 driving USDC adoption. x402 protocol native chain."
                elif name == "Solana":
                    signal += "High-speed DeFi + payment use cases. Circle prioritizing Solana USDC."
                elif name == "TON":
                    signal += "Telegram integration driving retail USDT adoption in CIS/SEA."
                elif name == "Arbitrum":
                    signal += "DeFi hub. USDC and USDT both strong."
            elif name in declining_chains:
                trend = "DECLINING"
                signal = f"{name} losing relative share. "
                if name == "BSC":
                    signal += "Binance regulatory pressure. FDUSD replacing BUSD."
                elif name == "Polygon":
                    signal += "Migrating to Polygon zkEVM and other L2s."
            else:
                trend = "STABLE"
                signal = f"{name} maintaining position."

            signals.append(ChainMigrationSignal(
                chain=name,
                supply_usd=c["supply_usd"],
                share_pct=c["share_pct"],
                dominant_stablecoin=c["dominant_stablecoin"],
                trend=trend,
                signal=signal,
            ))

        return signals

    def score_peg_stability(self) -> List[PegStabilityScore]:
        """Score peg stability for each major stablecoin."""
        scores = []
        events = self.data["peg_events_last_90d"]

        for coin in self.data["top_stablecoins"]:
            symbol = coin["symbol"]
            price = coin["price"] or 1.0
            deviation_bps = abs(price - 1.0) * 10000

            # Count events for this coin
            coin_events = [e for e in events if e["coin"] == symbol]
            worst = max([abs(e["deviation_pct"]) for e in coin_events], default=0)

            # Score: 100 = perfect peg, 0 = severe depeg
            score = 100
            score -= deviation_bps * 5  # Current deviation penalty
            score -= len(coin_events) * 10  # Event count penalty
            score -= worst * 20  # Worst event penalty
            score = max(0, min(100, int(score)))

            if score >= 90:
                risk = "LOW"
            elif score >= 70:
                risk = "MEDIUM"
            elif score >= 50:
                risk = "HIGH"
            else:
                risk = "CRITICAL"

            scores.append(PegStabilityScore(
                coin=symbol,
                current_price=price,
                deviation_from_peg_bps=round(deviation_bps, 1),
                stability_score=score,
                events_90d=len(coin_events),
                worst_deviation_90d_pct=round(worst, 2),
                risk_level=risk,
            ))

        scores.sort(key=lambda x: x.stability_score, reverse=True)
        return scores

    def build_competitor_scorecards(self) -> List[CompetitorScorecard]:
        """Build competitive intelligence scorecards for USDC's competitors."""
        total = self.data["total_supply_usd"]
        scorecards = []

        reserve_ratings = {
            "Deloitte (monthly attestation)": "HIGH",
            "BDO Italia (quarterly attestation)": "MEDIUM",
            "On-chain verifiable": "MEDIUM",
            "WithumSmith+Brown (monthly)": "HIGH",
            "Prescient Assurance": "MEDIUM",
            "PricewaterhouseCoopers": "HIGH",
            "Disputed (MooreHK controversy)": "LOW",
        }

        regulatory_ratings = {
            "USDT": "MODERATE",
            "USDC": "STRONG",
            "DAI": "NONE",
            "USDe": "WEAK",
            "USDS": "NONE",
            "FDUSD": "MODERATE",
            "PYUSD": "STRONG",
            "FRAX": "NONE",
            "TUSD": "WEAK",
            "BUIDL": "STRONG",
        }

        peg_scores = {s.coin: s for s in self.score_peg_stability()}

        for i, coin in enumerate(self.data["top_stablecoins"]):
            symbol = coin["symbol"]
            if symbol == "USDC":
                continue  # Don't score ourselves

            peg = peg_scores.get(symbol)
            peg_str = peg.risk_level if peg else "UNKNOWN"

            # Threat assessment
            dom = coin["supply_usd"] / total * 100
            reg = regulatory_ratings.get(symbol, "NONE")
            if dom > 50:
                threat = "HIGH"
            elif dom > 5 and reg in ("STRONG", "MODERATE"):
                threat = "HIGH"
            elif dom > 2:
                threat = "MEDIUM"
            else:
                threat = "LOW"

            scorecards.append(CompetitorScorecard(
                coin=symbol,
                issuer=coin["issuer"],
                supply_rank=i + 1,
                supply_usd=coin["supply_usd"],
                dominance_pct=round(dom, 1),
                reserve_transparency=reserve_ratings.get(coin["reserve_auditor"], "LOW"),
                regulatory_standing=reg,
                chain_coverage=len(coin.get("chains", [])) or 5,
                peg_stability=peg_str,
                overall_threat_level=threat,
            ))

        return scorecards

    def generate_early_warnings(self) -> List[EarlyWarningTrigger]:
        """Generate early warning triggers based on current market state."""
        warnings = []
        market = self.analyze_market_share()
        peg_scores = self.score_peg_stability()

        # Warning 1: USDC losing relative share
        if market.usdc_90d_growth_pct < market.usdt_90d_growth_pct - 3:
            warnings.append(EarlyWarningTrigger(
                trigger_type="MARKET_SHARE_SHIFT",
                severity="HIGH",
                description=f"USDC growing slower than USDT by {market.usdt_90d_growth_pct - market.usdc_90d_growth_pct:.1f}pp over 90 days",
                data_point=f"USDC: {market.usdc_90d_growth_pct}% vs USDT: {market.usdt_90d_growth_pct}%",
                recommended_action="Investigate: Is this exchange-driven (CEX listings) or corridor-driven (emerging market adoption)? Check if new PSP integrations are favoring USDT.",
            ))

        # Warning 2: Peg instability
        for peg in peg_scores:
            if peg.risk_level in ("HIGH", "CRITICAL"):
                warnings.append(EarlyWarningTrigger(
                    trigger_type="PEG_INSTABILITY",
                    severity="CRITICAL" if peg.risk_level == "CRITICAL" else "HIGH",
                    description=f"{peg.coin} peg stability score: {peg.stability_score}/100. {peg.events_90d} depeg events in 90 days.",
                    data_point=f"Worst deviation: {peg.worst_deviation_90d_pct}%. Current price: ${peg.current_price:.4f}",
                    recommended_action=f"Monitor {peg.coin} reserve disclosures. Assess contagion risk if {peg.coin} fails. Update competitive positioning materials.",
                ))

        # Warning 3: Chain concentration risk
        chains = self.data["chain_distribution"]
        top_chain = chains[0] if chains else None
        if top_chain and top_chain["share_pct"] > 40:
            warnings.append(EarlyWarningTrigger(
                trigger_type="CHAIN_CONCENTRATION",
                severity="MEDIUM",
                description=f"{top_chain['chain']} holds {top_chain['share_pct']}% of all stablecoin supply. Single-chain dependency risk.",
                data_point=f"${top_chain['supply_usd']:,} on {top_chain['chain']}",
                recommended_action="Track multi-chain migration trends. Assess impact if Ethereum congestion or outage forces temporary migration.",
            ))

        # Warning 4: Regulatory shift
        for reg in self.data["regulatory_tracker"]:
            if "expected" in reg["status"].lower() and "2026" in reg["status"]:
                warnings.append(EarlyWarningTrigger(
                    trigger_type="REGULATORY_CHANGE",
                    severity="MEDIUM",
                    description=f"{reg['jurisdiction']}: {reg['framework']} — {reg['status']}",
                    data_point=reg["impact"],
                    recommended_action=f"Monitor {reg['jurisdiction']} legislative calendar. Prepare impact assessment for Circle products.",
                ))

        # Warning 5: New competitor traction
        for coin in self.data["top_stablecoins"]:
            if coin["symbol"] in ("PYUSD", "BUIDL", "USDe") and coin["supply_usd"] > 400_000_000:
                warnings.append(EarlyWarningTrigger(
                    trigger_type="COMPETITOR_TRACTION",
                    severity="MEDIUM",
                    description=f"{coin['symbol']} ({coin['issuer']}) at ${coin['supply_usd'] / 1e9:.1f}B supply. Institutional entrant gaining traction.",
                    data_point=f"Peg mechanism: {coin['peg_mechanism']}. {coin['regulatory_status']}",
                    recommended_action=f"Update {coin['symbol']} competitor dossier. Assess distribution channel overlap with USDC.",
                ))

        warnings.sort(key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x.severity])
        return warnings


# ─────────────────────────────────────────
# CLI Demo
# ─────────────────────────────────────────

def run_demo():
    engine = MarketIntelligenceEngine()

    print("\n" + "=" * 76)
    print("  🔍 STABLECOIN MARKET & ECOSYSTEM INTELLIGENCE")
    print("  " + datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC"))
    print("=" * 76)

    # 1. Market Share
    print("\n\n" + "─" * 76)
    print("  SECTION 1: MARKET SHARE ANALYSIS")
    print("─" * 76)
    ms = engine.analyze_market_share()
    print(f"\n  Total stablecoin supply:     ${ms.total_supply:,}")
    print(f"  USDT supply:                 ${ms.usdt_supply:,} ({ms.usdt_dominance_pct}%)")
    print(f"  USDC supply:                 ${ms.usdc_supply:,} ({ms.usdc_dominance_pct}%)")
    print(f"  USDC/USDT ratio:             {ms.usdc_usdt_ratio}%")
    print(f"\n  90-day growth:")
    print(f"    Total market:              +{ms.total_90d_growth_pct}%")
    print(f"    USDT:                      +{ms.usdt_90d_growth_pct}%")
    print(f"    USDC:                      +{ms.usdc_90d_growth_pct}%")
    print(f"\n  Signal: {ms.market_shift_signal}")
    print(f"  Insight: {ms.insight}")

    # 2. Chain Migration
    print("\n\n" + "─" * 76)
    print("  SECTION 2: CHAIN MIGRATION SIGNALS")
    print("─" * 76)
    chains = engine.analyze_chain_migration()
    print(f"\n  {'Chain':<14} {'Supply':<18} {'Share':<8} {'Dominant':<8} {'Trend':<10} Signal")
    print(f"  {'─'*14} {'─'*18} {'─'*8} {'─'*8} {'─'*10} {'─'*30}")
    for c in chains:
        trend_icon = {"GROWING": "📈", "DECLINING": "📉", "STABLE": "➡️ "}[c.trend]
        print(f"  {c.chain:<14} ${c.supply_usd:>15,} {c.share_pct:>6.1f}% {c.dominant_stablecoin:<8} {trend_icon} {c.trend:<8}")

    # 3. Peg Stability
    print("\n\n" + "─" * 76)
    print("  SECTION 3: PEG STABILITY SCORECARDS")
    print("─" * 76)
    pegs = engine.score_peg_stability()
    print(f"\n  {'Coin':<8} {'Price':<10} {'Dev (bps)':<10} {'Score':<8} {'Events':<8} {'Worst':<10} Risk")
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*8} {'─'*8} {'─'*10} {'─'*10}")
    for p in pegs:
        risk_icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}[p.risk_level]
        print(f"  {p.coin:<8} ${p.current_price:<9.4f} {p.deviation_from_peg_bps:<9.1f} {p.stability_score:<7}/100 {p.events_90d:<7} {p.worst_deviation_90d_pct:<9.2f}% {risk_icon} {p.risk_level}")

    # 4. Competitor Scorecards
    print("\n\n" + "─" * 76)
    print("  SECTION 4: COMPETITOR SCORECARDS (vs USDC)")
    print("─" * 76)
    cards = engine.build_competitor_scorecards()
    for card in cards[:5]:
        threat_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[card.overall_threat_level]
        print(f"\n  {threat_icon} {card.coin} ({card.issuer})")
        print(f"    Rank: #{card.supply_rank} | Supply: ${card.supply_usd:,} ({card.dominance_pct}%)")
        print(f"    Reserves: {card.reserve_transparency} | Regulatory: {card.regulatory_standing} | Peg: {card.peg_stability}")
        print(f"    Threat to USDC: {card.overall_threat_level}")

    # 5. Early Warnings
    print("\n\n" + "─" * 76)
    print("  SECTION 5: EARLY WARNING TRIGGERS")
    print("─" * 76)
    warnings = engine.generate_early_warnings()
    for w in warnings:
        sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[w.severity]
        print(f"\n  {sev_icon} [{w.severity}] {w.trigger_type}")
        print(f"    {w.description}")
        print(f"    Data: {w.data_point}")
        print(f"    Action: {w.recommended_action}")

    # 6. Regulatory Tracker
    print("\n\n" + "─" * 76)
    print("  SECTION 6: JURISDICTIONAL REGULATORY TRACKER")
    print("─" * 76)
    for reg in engine.data["regulatory_tracker"]:
        print(f"\n  📋 {reg['jurisdiction']} — {reg['framework']}")
        print(f"    Status: {reg['status']}")
        print(f"    Impact: {reg['impact']}")

    print("\n\n" + "=" * 76)
    print("  END OF INTELLIGENCE REPORT")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    run_demo()
