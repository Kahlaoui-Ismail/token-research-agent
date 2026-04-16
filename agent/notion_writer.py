import os
from datetime import date

import httpx

from agent.models import TokenReport

NOTION_API_VERSION = "2022-06-28"
NOTION_PAGES_URL = "https://api.notion.com/v1/pages"


async def save_to_notion(report: TokenReport) -> str:
    """Create a Notion page for the token report. Returns the created page URL."""
    api_key = os.environ["NOTION_API_KEY"]
    database_id = os.environ["NOTION_DATABASE_ID"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }

    red_flag_items = [
        {"object": "block", "type": "bulleted_list_item",
         "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": flag}}]}}
        for flag in report.red_flags
    ] or [
        {"object": "block", "type": "bulleted_list_item",
         "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "None"}}]}}
    ]

    positive_items = [
        {"object": "block", "type": "bulleted_list_item",
         "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": sig}}]}}
        for sig in report.positive_signals
    ] or [
        {"object": "block", "type": "bulleted_list_item",
         "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "None"}}]}}
    ]

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Token Name": {
                "title": [{"text": {"content": report.token_name}}]
            },
            "Chain": {
                "rich_text": [{"text": {"content": report.chain}}]
            },
            "Risk Score": {
                "number": report.risk_score
            },
            "Risk Label": {
                "select": {"name": report.risk_label}
            },
            "Date": {
                "date": {"start": date.today().isoformat()}
            },
        },
        "children": [
            # On-chain summary
            {
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "On-Chain Summary"}}]},
            },
            {
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": report.on_chain_summary}}]},
            },
            # Red flags
            {
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🚩 Red Flags"}}]},
            },
            *red_flag_items,
            # Positive signals
            {
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ Positive Signals"}}]},
            },
            *positive_items,
            # Verdict
            {
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Verdict"}}]},
            },
            {
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": report.verdict}}]},
            },
        ],
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(NOTION_PAGES_URL, headers=headers, json=payload)
        response.raise_for_status()
        page_data = response.json()

    return page_data.get("url", "")
