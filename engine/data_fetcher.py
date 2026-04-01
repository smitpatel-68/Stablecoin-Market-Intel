"""
Stablecoin Data Fetcher — Live Market Data from DefiLlama

Pulls real-time and historical stablecoin data:
- Total supply per stablecoin (USDC, USDT, DAI, PYUSD, FDUSD, etc.)
- Chain-by-chain distribution
- Historical supply trends
- Price/peg data
- Market dominance

All data from DefiLlama's free, open API — no API key required.
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

BASE_URL = "https://stablecoins.llama.fi"

# Key stablecoin IDs on DefiLlama
TRACKED_STABLECOINS = {
    1: "USDT",
    2: "USDC",
    3: "DAI",
    # 4: "BUSD",  # deprecated
    5: "FRAX",
    6: "TUSD",
    12: "PYUSD",
    14: "FDUSD",
    48: "USDe",
    115: "USDS",
}

MAJOR_CHAINS = [
    "Ethereum", "Tron", "BSC", "Solana", "Polygon", "Arbitrum",
    "Avalanche", "Optimism", "Base", "Near", "Stellar", "TON",
    "Aptos", "Sui",
]


class StablecoinDataFetcher:
    """Fetches and caches stablecoin market data from DefiLlama."""

    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "StablecoinIntel/1.0"})

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make API request with basic error handling."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"  ⚠️ API error for {endpoint}: {e}")
            return {}

    def _cache(self, key: str, data: dict):
        """Cache data to disk."""
        path = self.cache_dir / f"{key}.json"
        with open(path, "w") as f:
            json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "data": data}, f, indent=2)

    def _load_cache(self, key: str, max_age_hours: int = 1) -> Optional[dict]:
        """Load cached data if fresh enough."""
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            return None
        with open(path) as f:
            cached = json.load(f)
        fetched = datetime.fromisoformat(cached["fetched_at"])
        age_hours = (datetime.now(timezone.utc) - fetched).total_seconds() / 3600
        if age_hours > max_age_hours:
            return None
        return cached["data"]

    # ─────────────────────────────────────────
    # Market Overview
    # ─────────────────────────────────────────

    def get_all_stablecoins(self) -> list:
        """Get current data for all stablecoins."""
        cached = self._load_cache("all_stablecoins")
        if cached:
            return cached
        data = self._get("stablecoins", {"includePrices": "true"})
        result = data.get("peggedAssets", [])
        self._cache("all_stablecoins", result)
        return result

    def get_market_overview(self) -> dict:
        """Build a market overview with top stablecoins, dominance, and totals."""
        assets = self.get_all_stablecoins()
        if not assets:
            return {}

        # Sort by circulating supply
        for a in assets:
            a["_supply"] = a.get("circulating", {}).get("peggedUSD", 0) or 0

        assets.sort(key=lambda x: x["_supply"], reverse=True)

        total_supply = sum(a["_supply"] for a in assets)
        top_10 = []

        for a in assets[:10]:
            supply = a["_supply"]
            top_10.append({
                "id": a.get("id"),
                "name": a.get("name", "Unknown"),
                "symbol": a.get("symbol", "?"),
                "supply_usd": round(supply),
                "dominance_pct": round((supply / total_supply * 100) if total_supply > 0 else 0, 2),
                "price": a.get("price"),
                "peg_mechanism": a.get("pegMechanism", "unknown"),
                "chains": list(a.get("chainCirculating", {}).keys())[:8],
            })

        return {
            "total_supply_usd": round(total_supply),
            "total_stablecoins_tracked": len(assets),
            "top_10": top_10,
            "usdc_usdt_ratio": round(
                top_10[1]["supply_usd"] / top_10[0]["supply_usd"] * 100, 1
            ) if len(top_10) >= 2 and top_10[0]["supply_usd"] > 0 else 0,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # ─────────────────────────────────────────
    # Chain Distribution
    # ─────────────────────────────────────────

    def get_chain_distribution(self) -> list:
        """Get stablecoin supply breakdown by chain."""
        cached = self._load_cache("chain_distribution")
        if cached:
            return cached

        data = self._get("stablecoinchains")
        if not data:
            return []

        chains = []
        for chain in data:
            total = chain.get("totalCirculatingUSD", {}).get("peggedUSD", 0) or 0
            if total > 100_000_000:  # Only chains with >$100M
                chains.append({
                    "chain": chain.get("name", "Unknown"),
                    "total_usd": round(total),
                })

        chains.sort(key=lambda x: x["total_usd"], reverse=True)
        self._cache("chain_distribution", chains)
        return chains

    # ─────────────────────────────────────────
    # Individual Stablecoin Deep Dive
    # ─────────────────────────────────────────

    def get_stablecoin_detail(self, stablecoin_id: int) -> dict:
        """Get detailed data for a specific stablecoin including chain breakdown."""
        cached = self._load_cache(f"stablecoin_{stablecoin_id}")
        if cached:
            return cached

        data = self._get(f"stablecoin/{stablecoin_id}")
        if not data:
            return {}

        # Extract chain breakdown
        chain_circulting = data.get("chainCirculating", {})
        chains = {}
        for chain_name, chain_data in chain_circulting.items():
            current = chain_data.get("current", {}).get("peggedUSD", 0) or 0
            if current > 1_000_000:  # >$1M
                chains[chain_name] = round(current)

        # Sort chains by value
        chains = dict(sorted(chains.items(), key=lambda x: x[1], reverse=True))

        # Extract recent supply history (last 90 days)
        tokens = data.get("tokens", [])
        history = []
        for entry in tokens[-90:]:
            date = entry.get("date", 0)
            supply = entry.get("circulating", {}).get("peggedUSD", 0) or 0
            if date and supply:
                history.append({
                    "date": datetime.fromtimestamp(date, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "supply_usd": round(supply),
                })

        result = {
            "id": data.get("id"),
            "name": data.get("name"),
            "symbol": data.get("symbol"),
            "total_supply": round(data.get("circulating", {}).get("peggedUSD", 0) or 0),
            "price": data.get("price"),
            "peg_mechanism": data.get("pegMechanism"),
            "peg_type": data.get("pegType"),
            "chain_breakdown": chains,
            "num_chains": len(chains),
            "history_90d": history,
        }

        self._cache(f"stablecoin_{stablecoin_id}", result)
        return result

    # ─────────────────────────────────────────
    # Peg Stability
    # ─────────────────────────────────────────

    def get_peg_prices(self) -> list:
        """Get historical peg prices for all stablecoins."""
        cached = self._load_cache("peg_prices")
        if cached:
            return cached

        data = self._get("stablecoinprices")
        if not data:
            return []

        # Get last 30 days
        recent = data[-30:] if len(data) > 30 else data
        result = []
        for entry in recent:
            date = entry.get("date", 0)
            prices = {}
            for coin_key, price in entry.items():
                if coin_key == "date":
                    continue
                # Extract symbol from key (format: "coingecko:tether" or similar)
                symbol = coin_key.split(":")[-1] if ":" in coin_key else coin_key
                if isinstance(price, (int, float)):
                    prices[symbol] = round(price, 6)

            if date and prices:
                result.append({
                    "date": datetime.fromtimestamp(date, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "prices": prices,
                })

        self._cache("peg_prices", result)
        return result

    # ─────────────────────────────────────────
    # Historical Market Data
    # ─────────────────────────────────────────

    def get_total_supply_history(self) -> list:
        """Get historical total stablecoin supply across all assets."""
        cached = self._load_cache("total_supply_history")
        if cached:
            return cached

        data = self._get("stablecoincharts/all", {"stablecoin": ""})
        if not data:
            return []

        # Last 365 days, weekly samples
        recent = data[-365:] if len(data) > 365 else data
        result = []
        for i, entry in enumerate(recent):
            if i % 7 != 0 and i != len(recent) - 1:  # Weekly + latest
                continue
            date = entry.get("date", 0)
            total = entry.get("totalCirculating", {}).get("peggedUSD", 0) or 0
            if date and total:
                result.append({
                    "date": datetime.fromtimestamp(date, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "total_supply_usd": round(total),
                })

        self._cache("total_supply_history", result)
        return result


# ─────────────────────────────────────────
# CLI
# ─────────────────────────────────────────

if __name__ == "__main__":
    fetcher = StablecoinDataFetcher()

    print("\n🔍 Fetching stablecoin market overview...")
    overview = fetcher.get_market_overview()
    if overview:
        print(f"\n  Total stablecoin supply: ${overview['total_supply_usd']:,}")
        print(f"  Stablecoins tracked: {overview['total_stablecoins_tracked']}")
        print(f"\n  Top 10:")
        for coin in overview["top_10"]:
            price_str = f"${coin['price']:.4f}" if coin['price'] else "N/A"
            print(f"    {coin['symbol']:<8} ${coin['supply_usd']:>15,}  ({coin['dominance_pct']:>5.1f}%)  Price: {price_str}")

    print("\n🔗 Fetching chain distribution...")
    chains = fetcher.get_chain_distribution()
    if chains:
        print(f"\n  Top chains by stablecoin supply:")
        for c in chains[:10]:
            print(f"    {c['chain']:<15} ${c['total_usd']:>15,}")

    print("\n📊 Fetching USDC detail...")
    usdc = fetcher.get_stablecoin_detail(2)
    if usdc:
        print(f"\n  USDC Supply: ${usdc['total_supply']:,}")
        print(f"  Chains: {usdc['num_chains']}")
        print(f"  Top chains:")
        for chain, val in list(usdc['chain_breakdown'].items())[:5]:
            print(f"    {chain:<15} ${val:>15,}")

    print("\n✅ Data fetch complete.\n")
