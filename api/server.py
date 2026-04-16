"""FastAPI server — wraps the token research agent behind an HTTP API."""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from agent.claude_agent import analyze_token  # noqa: E402

app = FastAPI(title="Token Research Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


def _detect_chain(address: str) -> str:
    stripped = address.strip()
    if stripped.lower().startswith("0x") and len(stripped) == 42:
        return "ETH"
    return "SOL"


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.get("/analyze/stream")
async def analyze_stream(address: str = Query(..., min_length=10)):
    """
    Server-Sent Events stream that:
      1. Emits `status` events with progress messages
      2. Emits a final `result` event with the full TokenReport JSON
      3. Emits an `error` event if anything goes wrong
    """

    async def event_generator():
        try:
            yield _sse({"type": "status", "message": "Detecting chain…"})
            chain = _detect_chain(address)
            yield _sse({"type": "status", "message": f"Chain detected: {chain}"})

            yield _sse({"type": "status", "message": "Fetching on-chain & market data…"})
            yield _sse({"type": "status", "message": "Running AI security analysis…"})

            report = await analyze_token(address, chain)

            yield _sse({"type": "result", "data": report.model_dump()})

        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Serve the frontend — mount last so API routes take precedence
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
