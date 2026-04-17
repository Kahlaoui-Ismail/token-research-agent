# 🐋 Token Research Agent

An AI-powered crypto token security analyst. Give it any Ethereum or Solana token address and it will fetch on-chain data from multiple sources, run a structured risk analysis via Claude, and print a colour-coded report in the terminal.

![demo placeholder](docs/demo.gif)
---

## What it does

1. **Auto-detects chain** — `0x…` addresses → Ethereum, base58 → Solana
2. **Fetches parallel data** from:
   - [DexScreener](https://dexscreener.com/) — price, liquidity, volume, pair age (ETH + SOL)
   - [Etherscan](https://etherscan.io/) — contract verification, holder count (ETH only)
   - [Honeypot.is](https://honeypot.is/) — honeypot flag, buy/sell/transfer tax (ETH only)
   - [Solscan](https://solscan.io/) — token metadata, top-10 holder concentration (SOL only)
   - [RugCheck](https://rugcheck.xyz/) — risk score and risk items (SOL only)
3. **Runs an agentic Claude loop** — Claude uses tool-use to request and reason over the data
4. **Prints a rich terminal report** with colour-coded risk tier

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| HTTP client | `httpx` (async) |
| AI | Anthropic SDK (`anthropic`) |
| Data validation | Pydantic v2 |
| Terminal UI | `rich` |
| Container | Docker / Docker Compose |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/token-research-agent.git
cd token-research-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| `ETHERSCAN_API_KEY` | [etherscan.io/apis](https://etherscan.io/apis) |

### 3. Run

```bash
# Ethereum token
python -m agent.main 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48

# Solana token
python -m agent.main EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

---

## Example output

```
╔══════════════════════════════════╗
║     🐋 TOKEN RESEARCH AGENT      ║
╚══════════════════════════════════╝

Token:   USDC
Chain:   ETH
Score:   91/100  ✅ SAFE

POSITIVE SIGNALS:
  • Verified contract
  • High liquidity ($320M)
  • No honeypot detected
  • Active trading volume

ON-CHAIN SUMMARY:
  USDC is a fully-backed stablecoin issued by Circle...

VERDICT:
  Low-risk asset. Widely audited, regulated issuer...
```

> *(Replace with a real screenshot once you have one)*

---

## Docker

```bash
# Build
docker compose build

# Run
docker compose run token-researcher 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```

---

## Project structure

```
token-research-agent/
├── agent/
│   ├── main.py            # Entry point + rich terminal output
│   ├── claude_agent.py    # Agentic tool-use loop with Claude
│   ├── models.py          # Pydantic TokenReport model
│   └── fetchers/
│       ├── dexscreener.py # Market data (ETH + SOL)
│       ├── etherscan.py   # On-chain data (ETH)
│       ├── solscan.py     # On-chain data (SOL)
│       ├── rugcheck.py    # Risk report (SOL)
│       └── honeypot.py    # Honeypot check (ETH)
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Risk tiers

| Score | Label | Colour |
|---|---|---|
| 75 – 100 | SAFE | 🟢 Green |
| 50 – 74 | CAUTION | 🟡 Yellow |
| 25 – 49 | RISKY | 🟠 Orange |
| 0 – 24 | LIKELY SCAM | 🔴 Red |
