import os
import httpx
from datetime import datetime, timezone


async def get_etherscan_data(address: str) -> dict:
    api_key = os.environ.get("ETHERSCAN_API_KEY", "")
    base_url = "https://api.etherscan.io/api"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            source_resp, token_resp = await _fetch_both(client, base_url, address, api_key)

        source_data = source_resp.get("result", [{}])
        contract_info = source_data[0] if source_data else {}
        is_verified = bool(contract_info.get("SourceCode"))

        # Contract creation timestamp from token info or source code
        contract_age_days = None
        deploy_date_str = contract_info.get("ConstructorArguments")  # not reliable
        # Use token info endpoint for creation date if available
        token_result = token_resp.get("result", [{}])
        token_info = token_result[0] if token_result else {}

        total_supply = token_info.get("totalSupply")
        holder_count = token_info.get("holdersCount") or token_info.get("holderCount")

        return {
            "is_verified": is_verified,
            "contract_age_days": contract_age_days,
            "total_supply": total_supply,
            "holder_count": holder_count,
        }
    except Exception:
        return {}


async def _fetch_both(client: httpx.AsyncClient, base_url: str, address: str, api_key: str):
    import asyncio

    source_task = client.get(base_url, params={
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": api_key,
    })
    token_task = client.get(base_url, params={
        "module": "token",
        "action": "tokeninfo",
        "contractaddress": address,
        "apikey": api_key,
    })
    source_resp, token_resp = await asyncio.gather(source_task, token_task)
    source_resp.raise_for_status()
    token_resp.raise_for_status()
    return source_resp.json(), token_resp.json()
