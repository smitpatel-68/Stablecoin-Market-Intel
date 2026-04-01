"""
Intelligence Report Generator

Produces executive-ready markdown reports from the analysis engine.
Designed to match Circle's requirement for:
- Impact summaries
- Escalation memos
- Scorecards tied to early-warning triggers
"""

from datetime import datetime, timezone
from engine.market_intelligence import MarketIntelligenceEngine
from dataclasses import asdict
from pathlib import Path


def generate_report(output_dir: str = "reports") -> str:
    """Generate a full intelligence report in markdown format."""
    engine = MarketIntelligenceEngine()
    now = datetime.now(timezone.utc)

    lines = []
    lines.append(f"# Stablecoin Market Intelligence Report")
    lines.append(f"**Generated:** {now.strftime('%B %d, %Y %H:%M UTC')}")
    lines.append(f"**Classification:** Internal — Decision Support")
    lines.append(f"**Prepared for:** Strategy & Market Intelligence Team")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    ms = engine.analyze_market_share()
    warnings = engine.generate_early_warnings()
    critical = [w for w in warnings if w.severity == "CRITICAL"]

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"Total stablecoin supply stands at **${ms.total_supply / 1e9:.1f}B**, up **{ms.total_90d_growth_pct}%** over 90 days. "
                 f"USDT holds **{ms.usdt_dominance_pct}%** dominance; USDC at **{ms.usdc_dominance_pct}%**. "
                 f"USDC/USDT ratio: **{ms.usdc_usdt_ratio}%**.")
    lines.append("")
    lines.append(f"**90-day signal:** {ms.market_shift_signal}")
    lines.append(f"> {ms.insight}")
    lines.append("")

    if critical:
        lines.append(f"**{len(critical)} critical alert(s) require immediate attention** — see Early Warnings section below.")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Market Share
    lines.append("## 1. Market Share Dynamics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total supply | ${ms.total_supply / 1e9:.1f}B |")
    lines.append(f"| USDT | ${ms.usdt_supply / 1e9:.1f}B ({ms.usdt_dominance_pct}%) |")
    lines.append(f"| USDC | ${ms.usdc_supply / 1e9:.1f}B ({ms.usdc_dominance_pct}%) |")
    lines.append(f"| 90-day total growth | +{ms.total_90d_growth_pct}% |")
    lines.append(f"| 90-day USDC growth | +{ms.usdc_90d_growth_pct}% |")
    lines.append(f"| 90-day USDT growth | +{ms.usdt_90d_growth_pct}% |")
    lines.append("")

    # Chain Distribution
    chains = engine.analyze_chain_migration()
    lines.append("## 2. Chain Distribution & Migration")
    lines.append("")
    lines.append("| Chain | Supply | Share | Dominant | Trend |")
    lines.append("|---|---|---|---|---|")
    for c in chains:
        lines.append(f"| {c.chain} | ${c.supply_usd / 1e9:.1f}B | {c.share_pct}% | {c.dominant_stablecoin} | {c.trend} |")
    lines.append("")

    growing = [c for c in chains if c.trend == "GROWING"]
    if growing:
        lines.append("**Growing chains:** " + ", ".join(f"{c.chain} ({c.signal.split('.')[0]})" for c in growing))
        lines.append("")

    # Peg Stability
    pegs = engine.score_peg_stability()
    lines.append("## 3. Peg Stability Scorecards")
    lines.append("")
    lines.append("| Coin | Price | Deviation (bps) | Score | Risk |")
    lines.append("|---|---|---|---|---|")
    for p in pegs:
        lines.append(f"| {p.coin} | ${p.current_price:.4f} | {p.deviation_from_peg_bps:.1f} | {p.stability_score}/100 | {p.risk_level} |")
    lines.append("")

    at_risk = [p for p in pegs if p.risk_level in ("HIGH", "CRITICAL")]
    if at_risk:
        lines.append("**Coins requiring monitoring:** " + ", ".join(f"{p.coin} ({p.risk_level})" for p in at_risk))
        lines.append("")

    # Competitor Scorecards
    cards = engine.build_competitor_scorecards()
    lines.append("## 4. Competitor Scorecards (vs USDC)")
    lines.append("")
    for card in cards[:5]:
        lines.append(f"### {card.coin} ({card.issuer})")
        lines.append(f"- **Rank:** #{card.supply_rank} | **Supply:** ${card.supply_usd / 1e9:.1f}B ({card.dominance_pct}%)")
        lines.append(f"- **Reserve transparency:** {card.reserve_transparency}")
        lines.append(f"- **Regulatory standing:** {card.regulatory_standing}")
        lines.append(f"- **Peg stability:** {card.peg_stability}")
        lines.append(f"- **Threat level:** {card.overall_threat_level}")
        lines.append("")

    # Early Warnings
    lines.append("## 5. Early Warning Triggers")
    lines.append("")
    for w in warnings:
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[w.severity]
        lines.append(f"### {icon} [{w.severity}] {w.trigger_type}")
        lines.append(f"**Signal:** {w.description}")
        lines.append(f"**Data:** {w.data_point}")
        lines.append(f"**Recommended action:** {w.recommended_action}")
        lines.append("")

    # Regulatory Tracker
    lines.append("## 6. Jurisdictional Regulatory Tracker")
    lines.append("")
    lines.append("| Jurisdiction | Framework | Status | Impact |")
    lines.append("|---|---|---|---|")
    for reg in engine.data["regulatory_tracker"]:
        lines.append(f"| {reg['jurisdiction']} | {reg['framework']} | {reg['status'][:60]} | {reg['impact'][:80]} |")
    lines.append("")

    lines.append("---")
    lines.append(f"*Report generated automatically by Stablecoin Intelligence Engine. "
                 f"Data sourced from DefiLlama, on-chain analytics, and regulatory monitoring.*")

    report = "\n".join(lines)

    # Save
    Path(output_dir).mkdir(exist_ok=True)
    filename = f"intel_report_{now.strftime('%Y%m%d_%H%M')}.md"
    filepath = Path(output_dir) / filename
    with open(filepath, "w") as f:
        f.write(report)

    print(f"\n📋 Intelligence report generated: {filepath}")
    print(f"   Sections: 6 | Warnings: {len(warnings)} ({len(critical)} critical)")
    return str(filepath)


if __name__ == "__main__":
    generate_report()
