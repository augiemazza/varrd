"""Pydantic models for VARRD API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

class TradeSetup(BaseModel):
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    risk_reward: float | None = None
    horizon: int | None = None

class ScanItem(BaseModel):
    hypothesis_id: str
    name: str = ""
    market: str = ""
    status: str = ""
    firing_now: bool = False
    direction: str = ""
    has_edge: bool | None = None
    win_rate: float | None = None
    sharpe: float | None = None
    profit_factor: float | None = None
    entry_price: float | None = None
    stop_loss_price: float | None = None
    take_profit_price: float | None = None
    trade_setups: list[TradeSetup] = Field(default_factory=list)

class ScanResult(BaseModel):
    scanned_at: str = ""
    total_scanned: int = 0
    firing_count: int = 0
    results: list[ScanItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class SearchItem(BaseModel):
    hypothesis_id: str
    name: str = ""
    formula: str = ""
    market: str = ""
    direction: str = ""
    has_edge: bool | None = None
    win_rate: float | None = None
    sharpe: float | None = None
    similarity: float | None = None

class SearchResult(BaseModel):
    results: list[SearchItem] = Field(default_factory=list)
    query: str = ""
    method: str = ""


# ---------------------------------------------------------------------------
# Hypothesis detail
# ---------------------------------------------------------------------------

class HorizonResult(BaseModel):
    horizon: int
    mean_return: float | None = None
    win_rate: float | None = None
    significant: bool | None = None

class FormulaVersion(BaseModel):
    formula: str = ""
    market: str = ""
    created_at: str = ""

class HypothesisDetail(BaseModel):
    hypothesis_id: str
    name: str = ""
    formula: str = ""
    explanation: str = ""
    market: str = ""
    markets: list[str] = Field(default_factory=list)
    direction: str = ""
    selected_horizon: int | None = None
    entry_offset: int | None = None
    entry_price_type: str = ""
    has_edge: bool | None = None
    is_validated: bool | None = None
    test_type: str = ""
    win_rate: float | None = None
    sharpe: float | None = None
    ev_per_trade: float | None = None
    profit_factor: float | None = None
    max_drawdown: float | None = None
    total_trades: int | None = None
    risk_reward: float | None = None
    stop_loss_atr: float | None = None
    take_profit_atr: float | None = None
    horizon_results: list[HorizonResult] = Field(default_factory=list)
    versions: list[FormulaVersion] = Field(default_factory=list)
    created_at: str = ""


# ---------------------------------------------------------------------------
# Research
# ---------------------------------------------------------------------------

class ResearchContext(BaseModel):
    workflow_state: str | None = None
    direction: str | None = None
    signal_count: int | None = None
    k: int | None = Field(None, alias="K")
    test_type: str | None = None
    oos_used: bool | None = None
    has_edge: bool | None = None
    edge_verdict: str | None = None
    next_actions: list[str] = Field(default_factory=list)
    market: str | None = None
    most_recent_bar: str | None = None
    horizons_tested: Any = None
    best_horizon: Any = None
    markets_tested: Any = None
    backtest_phase: str | None = None
    expert_council_returned: bool | None = None
    expert_council_count: int | None = None
    expert_council_instruction: str | None = None

    model_config = {"populate_by_name": True}

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

class ResearchResult(BaseModel):
    session_id: str
    text: str = ""
    widgets: list[dict[str, Any]] = Field(default_factory=list)
    context: ResearchContext = Field(default_factory=ResearchContext)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)


# ---------------------------------------------------------------------------
# Discover (autonomous_research)
# ---------------------------------------------------------------------------

class DiscoverResult(BaseModel):
    hypothesis_id: str | None = None
    name: str = ""
    market: str = ""
    has_edge: bool | None = None
    edge_verdict: str = ""
    direction: str = ""
    win_rate: float | None = None
    sharpe: float | None = None
    trade_setup: TradeSetup | None = None
    text: str = ""
    widgets: list[dict[str, Any]] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)


# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------

class CreditPack(BaseModel):
    amount_cents: int
    label: str

class BalanceResult(BaseModel):
    balance_cents: int = 0
    lifetime_added_cents: int | None = None
    enforcement_enabled: bool = False
    credit_packs: list[CreditPack] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

class ResetResult(BaseModel):
    reset: bool = False
    message: str = ""
