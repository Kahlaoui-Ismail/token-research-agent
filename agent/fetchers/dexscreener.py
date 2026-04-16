import httpx
from datetime import datetime, timezone


async def get_dexscreener_data(address: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        pairs = data.get("pairs") or []
        if not pairs:
            return {}

        # Use the pair with the highest liquidity
        pair = max(pairs, key=lambda p: (p.get("liquidity") or {}).get("usd") or 0)

        created_at_ms = pair.get("pairCreatedAt")
        pair_age_days = None
        if created_at_ms:
            created_dt = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc)
            pair_age_days = (datetime.now(tz=timezone.utc) - created_dt).days

        base_token = pair.get("baseToken") or {}
        volume = pair.get("volume") or {}
        liquidity = pair.get("liquidity") or {}
        price_change = pair.get("priceChange") or {}

        return {
            "token_name": base_token.get("name"),
            "token_symbol": base_token.get("symbol"),
            "price_usd": pair.get("priceUsd"),
            "volume_24h": volume.get("h24"),
            "liquidity_usd": liquidity.get("usd"),
            "pair_age_days": pair_age_days,
            "dex_name": pair.get("dexId"),
            "price_change_24h": price_change.get("h24"),
        }
    except Exception:
        return {}
