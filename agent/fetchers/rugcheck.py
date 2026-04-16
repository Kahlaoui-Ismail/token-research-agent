import httpx


async def get_rugcheck_data(address: str) -> dict:
    url = f"https://api.rugcheck.xyz/v1/tokens/{address}/report"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        score = data.get("score")
        risks_raw = data.get("risks") or []
        risks = [
            {
                "name": r.get("name"),
                "description": r.get("description"),
                "level": r.get("level"),
            }
            for r in risks_raw
        ]

        return {
            "overall_risk_score": score,
            "risks": risks,
        }
    except Exception:
        return {}
