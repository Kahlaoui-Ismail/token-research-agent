import httpx


async def get_honeypot_data(address: str) -> dict:
    url = f"https://api.honeypot.is/v2/IsHoneypot?address={address}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        honeypot_result = data.get("honeypotResult") or {}
        simulation = data.get("simulationResult") or {}
        flags = data.get("flags") or []

        return {
            "is_honeypot": honeypot_result.get("isHoneypot"),
            "buy_tax": simulation.get("buyTax"),
            "sell_tax": simulation.get("sellTax"),
            "transfer_tax": simulation.get("transferTax"),
            "flags": flags,
        }
    except Exception:
        return {}
