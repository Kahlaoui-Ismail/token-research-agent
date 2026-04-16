import json
import os
import asyncio
import anthropic

from agent.fetchers.dexscreener import get_dexscreener_data
from agent.fetchers.etherscan import get_etherscan_data
from agent.fetchers.solscan import get_solscan_data
from agent.fetchers.rugcheck import get_rugcheck_data
from agent.fetchers.honeypot import get_honeypot_data
from agent.models import TokenReport

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1000

SYSTEM_PROMPT = """\
You are a crypto token security analyst. You have access to on-chain and market data tools.
Use all relevant tools to research the given token, then return ONLY a JSON object with this
exact schema — no preamble, no markdown:

{"token_name": "", "chain": "", "risk_score": 0-100, "risk_label": "SAFE|CAUTION|RISKY|LIKELY SCAM", "red_flags": [], "positive_signals": [], "on_chain_summary": "", "verdict": ""}

Risk score rules: 0–24 = LIKELY SCAM, 25–49 = RISKY, 50–74 = CAUTION, 75–100 = SAFE.

Red flags to watch:
- Unverified contract
- Honeypot detected
- Buy/sell tax >10%
- Top 10 holders >80% of supply
- Pair age <7 days
- Low liquidity <$10k
- Rugcheck high risk
"""

TOOLS_ETH = [
    {
        "name": "get_dexscreener_data",
        "description": "Fetch DEX market data for the token: price, volume, liquidity, pair age, DEX name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token contract address"}
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_etherscan_data",
        "description": "Fetch Ethereum on-chain data: contract verification status, total supply, holder count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token contract address (ETH)"}
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_honeypot_data",
        "description": "Check whether an Ethereum token is a honeypot: buy/sell/transfer tax, honeypot flag.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token contract address (ETH)"}
            },
            "required": ["address"],
        },
    },
]

TOOLS_SOL = [
    {
        "name": "get_dexscreener_data",
        "description": "Fetch DEX market data for the token: price, volume, liquidity, pair age, DEX name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token contract address"}
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_solscan_data",
        "description": "Fetch Solana on-chain data: token name, symbol, decimals, holder count, top-10 holders % of supply.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token mint address (SOL)"}
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_rugcheck_data",
        "description": "Fetch RugCheck risk report for a Solana token: overall risk score, list of risks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Token mint address (SOL)"}
            },
            "required": ["address"],
        },
    },
]

FETCHER_MAP = {
    "get_dexscreener_data": get_dexscreener_data,
    "get_etherscan_data": get_etherscan_data,
    "get_solscan_data": get_solscan_data,
    "get_rugcheck_data": get_rugcheck_data,
    "get_honeypot_data": get_honeypot_data,
}


async def _execute_tool(tool_name: str, tool_input: dict) -> str:
    fetcher = FETCHER_MAP.get(tool_name)
    if fetcher is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    address = tool_input.get("address", "")
    result = await fetcher(address)
    return json.dumps(result)


async def analyze_token(address: str, chain: str) -> TokenReport:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    tools = TOOLS_ETH if chain == "ETH" else TOOLS_SOL

    user_content = (
        f"Analyze this {chain} token at address {address}. "
        f"Use all available tools to collect data, then return your JSON analysis."
    )
    messages = [{"role": "user", "content": user_content}]

    # Agentic loop: keep calling until Claude stops requesting tools
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        # Execute all requested tool calls concurrently
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        results = await asyncio.gather(
            *[_execute_tool(b.name, b.input) for b in tool_use_blocks]
        )

        tool_results = [
            {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            }
            for block, result in zip(tool_use_blocks, results)
        ]
        messages.append({"role": "user", "content": tool_results})

    # Extract the final text block and parse JSON
    final_text = next(
        (b.text for b in response.content if b.type == "text"), "{}"
    )

    # Strip any accidental markdown fences
    clean = final_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
        clean = clean.strip()

    data = json.loads(clean)
    return TokenReport(**data)
