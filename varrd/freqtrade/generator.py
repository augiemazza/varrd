"""Generate Freqtrade strategy files from VARRD-validated hypotheses."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from varrd.models import HypothesisDetail

from varrd.freqtrade.translator import (
    atr_sl_to_custom_stoploss,
    atr_tp_to_custom_exit,
    timeframe_to_seconds_code,
    varrd_market_to_pair,
    varrd_timeframe_to_freqtrade,
    varrd_to_freqtrade_code,
    varrd_to_freqtrade_entry,
)

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _sanitize_class_name(name: str, max_words: int = 4) -> str:
    """Convert hypothesis name to a valid Python class name.

    'RSI oversold reversal on BTC' -> 'VARRDRsiOversoldReversal'
    """
    # Remove non-alphanumeric (keep spaces for splitting)
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", name)
    parts = cleaned.split()[:max_words]
    class_name = "".join(word.capitalize() for word in parts)
    if not class_name:
        class_name = "Strategy"
    return f"VARRD{class_name}"


def _comment_wrap(text: str) -> str:
    """Wrap multi-line text so every line is a Python comment."""
    lines = text.strip().splitlines()
    return "\n".join(f"# {line.rstrip()}" for line in lines)


def generate_strategy(
    hypothesis: HypothesisDetail,
    strategy_name: str | None = None,
    exchange: str = "binance",
    stake_currency: str = "USDT",
    setup_code: str = "",
) -> tuple[str, dict[str, Any]]:
    """Generate a Freqtrade strategy file from a VARRD hypothesis.

    Args:
        hypothesis: HypothesisDetail from the varrd SDK.
        strategy_name: Override for the strategy class name.
        exchange: Freqtrade exchange name (default: binance).
        stake_currency: Quote currency (default: USDT).
        setup_code: VARRD setup_code if not on the hypothesis object.
            HypothesisDetail may not always carry setup_code; pass it
            explicitly when available.

    Returns:
        (strategy_py_content, config_dict) — the .py file content and a
        matching Freqtrade config.json dict.
    """
    # --- Resolve fields ---
    market = hypothesis.market or ""
    direction = (hypothesis.direction or "LONG").upper()
    formula = hypothesis.formula or "True"
    name = hypothesis.name or "Unnamed Strategy"
    pair = varrd_market_to_pair(market, stake_currency)
    timeframe = varrd_timeframe_to_freqtrade(market)

    sl_atr = hypothesis.stop_loss_atr
    tp_atr = hypothesis.take_profit_atr
    horizon = hypothesis.selected_horizon or 10

    strategy_class = strategy_name or _sanitize_class_name(name)

    # --- Translate code ---
    indicators_code = ""
    if setup_code:
        indicators_code = varrd_to_freqtrade_code(setup_code)
    # Indent each line for the class body
    if indicators_code:
        lines = indicators_code.split("\n")
        indicators_code = "\n        ".join(lines)

    entry_code = varrd_to_freqtrade_entry(formula, direction)

    # Custom stoploss / exit
    custom_stoploss_code = ""
    if sl_atr is not None:
        custom_stoploss_code = atr_sl_to_custom_stoploss(sl_atr)
        default_stoploss = -0.99  # disabled; custom_stoploss handles it
    else:
        default_stoploss = -0.10  # 10% fallback

    custom_exit_code = ""
    if tp_atr is not None or horizon:
        custom_exit_code = atr_tp_to_custom_exit(
            tp_atr if tp_atr is not None else 3.0,
            horizon,
        )

    # --- Clean text fields for the template ---
    # Explanation: wrap every line in # comments
    explanation = hypothesis.explanation or ""
    if explanation:
        explanation = _comment_wrap(explanation)

    # Hypothesis name: first line only, ASCII-safe for the header
    header_name = name.split("\n")[0].strip()
    header_name = header_name.encode("ascii", "replace").decode("ascii")

    # --- Render template ---
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        keep_trailing_newline=True,
    )
    template = env.get_template("strategy_template.py")

    strategy_content = template.render(
        version="0.1.0",
        hypothesis_name=header_name,
        market=market,
        pair=pair,
        direction=direction,
        timeframe=timeframe,
        has_edge=hypothesis.has_edge,
        win_rate=hypothesis.win_rate,
        sharpe=hypothesis.sharpe,
        ev_per_trade=hypothesis.ev_per_trade,
        profit_factor=hypothesis.profit_factor,
        total_trades=hypothesis.total_trades,
        risk_reward=hypothesis.risk_reward,
        stop_loss_atr=sl_atr,
        take_profit_atr=tp_atr,
        selected_horizon=hypothesis.selected_horizon,
        explanation=explanation,
        strategy_class=strategy_class,
        default_stoploss=default_stoploss,
        startup_candles=50,
        can_short="True" if direction == "SHORT" else "False",
        use_custom_stoploss="True" if sl_atr is not None else "False",
        indicators_code=indicators_code or "pass  # No setup_code provided",
        entry_code=entry_code,
        custom_stoploss_code=custom_stoploss_code,
        custom_exit_code=custom_exit_code,
        timeframe_to_seconds_func=timeframe_to_seconds_code(),
    )

    # --- Config dict ---
    config = {
        "trading_mode": "spot",
        "stake_currency": stake_currency,
        "stake_amount": "unlimited",
        "dry_run": True,
        "dry_run_wallet": 1000,
        "exchange": {
            "name": exchange,
            "pair_whitelist": [pair],
        },
        "entry_pricing": {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1,
        },
        "exit_pricing": {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1,
        },
        "pairlists": [{"method": "StaticPairList"}],
    }

    return strategy_content, config
