from pydantic import BaseModel
from typing import List


class TokenReport(BaseModel):
    token_name: str
    chain: str
    risk_score: int
    risk_label: str
    red_flags: List[str]
    positive_signals: List[str]
    on_chain_summary: str
    verdict: str
