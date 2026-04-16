import asyncio
import httpx


async def get_solscan_data(address: str) -> dict:
    meta_url = f"https://public-api.solscan.io/token/meta?tokenAddress={address}"
    holders_url = f"https://public-api.solscan.io/token/holders?tokenAddress={address}&limit=10"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            meta_resp, holders_resp = await asyncio.gather(
                client.get(meta_url),
                client.get(holders_url),
            )
            meta_resp.raise_for_status()
            holders_resp.raise_for_status()

        meta = meta_resp.json()
        holders_data = holders_resp.json()

        holders = holders_data.get("data", [])
        total_supply_raw = meta.get("supply") or 1
        decimals = int(meta.get("decimals") or 0)
        total_supply = int(total_supply_raw) / (10 ** decimals) if decimals else int(total_supply_raw)

        top10_pct = None
        if holders and total_supply:
            top10_amount = sum(
                int(h.get("amount") or 0) / (10 ** decimals)
                for h in holders[:10]
            )
            top10_pct = round((top10_amount / total_supply) * 100, 2) if total_supply else None

        return {
            "name": meta.get("name"),
            "symbol": meta.get("symbol"),
            "decimals": decimals,
            "holder_count": holders_data.get("total"),
            "top10_holders_pct": top10_pct,
        }
    except Exception:
        return {}
