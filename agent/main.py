#!/usr/bin/env python3
"""Token Research Agent — entry point."""

import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from agent.claude_agent import analyze_token
from agent.notion_writer import save_to_notion

console = Console()


def _detect_chain(address: str) -> str:
    """Return 'ETH' or 'SOL' based on address format."""
    stripped = address.strip()
    if stripped.lower().startswith("0x") and len(stripped) == 42:
        return "ETH"
    # Solana base58 addresses are 32–44 chars, no 0x prefix
    return "SOL"


def _score_color(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "yellow"
    if score >= 25:
        return "orange3"
    return "red"


def _label_icon(label: str) -> str:
    icons = {
        "SAFE": "✅",
        "CAUTION": "⚠️",
        "RISKY": "🔶",
        "LIKELY SCAM": "🚨",
    }
    return icons.get(label, "")


def display_report(report, saved_to_notion: bool = False) -> None:
    score_color = _score_color(report.risk_score)
    label_icon = _label_icon(report.risk_label)

    console.print(
        Panel(
            "[bold cyan]🐋 TOKEN RESEARCH AGENT[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )
    console.print()
    console.print(f"[bold]Token:[/bold]   {report.token_name}")
    console.print(f"[bold]Chain:[/bold]   {report.chain}")
    console.print(
        f"[bold]Score:[/bold]   [{score_color}]{report.risk_score}/100  "
        f"{label_icon} {report.risk_label}[/{score_color}]"
    )
    console.print()

    if report.red_flags:
        console.print("[bold red]RED FLAGS:[/bold red]")
        for flag in report.red_flags:
            console.print(f"  [red]•[/red] {flag}")
        console.print()

    if report.positive_signals:
        console.print("[bold green]POSITIVE SIGNALS:[/bold green]")
        for sig in report.positive_signals:
            console.print(f"  [green]•[/green] {sig}")
        console.print()

    console.print("[bold]ON-CHAIN SUMMARY:[/bold]")
    console.print(f"  {report.on_chain_summary}")
    console.print()

    console.print("[bold]VERDICT:[/bold]")
    console.print(f"  {report.verdict}")
    console.print()

    if saved_to_notion:
        console.print("[bold green]📝 Saved to Notion[/bold green]")


async def run(address: str) -> None:
    chain = _detect_chain(address)
    console.print(
        Panel(
            "[bold cyan]🐋 TOKEN RESEARCH AGENT[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )
    console.print(f"\n[dim]Detected chain:[/dim] [bold]{chain}[/bold]")
    console.print(f"[dim]Analyzing address:[/dim] [bold]{address}[/bold]\n")

    with console.status("[bold cyan]Fetching on-chain data and running AI analysis…[/bold cyan]"):
        report = await analyze_token(address, chain)

    saved = False
    try:
        await save_to_notion(report)
        saved = True
    except Exception as exc:
        console.print(f"[yellow]⚠ Notion save skipped:[/yellow] {exc}")

    # Clear the header — reprint full report
    console.clear()
    display_report(report, saved_to_notion=saved)


def main() -> None:
    if len(sys.argv) != 2:
        console.print("[red]Usage:[/red] python -m agent.main <token_address>")
        sys.exit(1)

    address = sys.argv[1]
    asyncio.run(run(address))


if __name__ == "__main__":
    main()
