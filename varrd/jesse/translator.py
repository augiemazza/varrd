"""Shared translation utilities between VARRD and Jesse formats."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Market / timeframe mappings
# ---------------------------------------------------------------------------

_TF_MAP: dict[str, str] = {
    "daily": "1D",
    "60min": "1h",
    "15min": "15m",
    "5min": "5m",
    "weekly": "1W",
    "4h": "4h",
    "1h": "1h",
    "30min": "30m",
    # Already in common format
    "1d": "1D",
    "1w": "1W",
    "15m": "15m",
    "5m": "5m",
    "30m": "30m",
}


def varrd_market_to_jesse_pair(market: str, quote: str = "USDT") -> str:
    """Convert VARRD market string to Jesse pair format.

    'BTC_daily'    -> 'BTC-USDT'
    'BTCUSDT_1d'   -> 'BTC-USDT'
    'ETH'          -> 'ETH-USDT'
    'SOLUSDT_4h'   -> 'SOL-USDT'
    """
    base = market.split("_")[0].upper()

    # Strip quote currency suffix (BTCUSDT -> BTC, ETHUSDT -> ETH)
    for suffix in ("USDT", "USD", "BUSD", "USDC"):
        if base.endswith(suffix) and len(base) > len(suffix):
            base = base[: -len(suffix)]
            break

    return f"{base}-{quote}"


def varrd_timeframe_to_jesse(market: str) -> str:
    """Extract timeframe from VARRD market string and convert to Jesse format.

    'BTC_daily' -> '1D'
    'ES_60min'  -> '1h'
    'ETH'       -> '1D'  (default)
    """
    parts = market.split("_")
    if len(parts) >= 2:
        tf = parts[-1].lower()
        return _TF_MAP.get(tf, "1D")
    return "1D"


# ---------------------------------------------------------------------------
# Code translation (VARRD -> Jesse)
# ---------------------------------------------------------------------------

def varrd_to_jesse_indicators(setup_code: str) -> str:
    """Convert VARRD setup_code to Jesse before() method body.

    Main transforms:
    - Remove load_data / query_data lines
    - df['close'] -> self.close (OHLCV properties)
    - df['indicator'] = expr -> self.vars['indicator'] = expr
    - ta.RSI(df['close'], timeperiod=14) -> ta.rsi(self.candles, period=14)
    """
    code = setup_code

    # Remove load_data / query_data lines
    code = re.sub(r'^.*(?:load_data|query_data).*$', '', code, flags=re.MULTILINE)

    # Map talib calls: ta.INDICATOR(df[...], timeperiod=N) -> ta.indicator(self.candles, period=N)
    code = re.sub(
        r'ta\.([A-Z_]+)\(.*?\bdf\b.*?\)',
        lambda m: _translate_ta_call(m.group(0), m.group(1)),
        code,
    )

    # Map df['ohlcv'] references to self properties (before generic df replacement)
    for col in ('close', 'open', 'high', 'low', 'volume'):
        code = re.sub(rf"df\['{col}'\]", f"self.{col}", code)
        code = re.sub(rf'df\["{col}"\]', f"self.{col}", code)

    # Map df['indicator'] = ... -> self.vars['indicator'] = ...
    code = re.sub(r"df\['(\w+)'\]", r"self.vars['\1']", code)
    code = re.sub(r'df\["(\w+)"\]', r"self.vars['\1']", code)

    # Clean up blank lines
    code = re.sub(r'\n{3,}', '\n\n', code)

    return code.strip()


def _translate_ta_call(full_match: str, indicator: str) -> str:
    """Translate a single talib call to Jesse's indicator format."""
    jesse_name = indicator.lower()

    # Extract period parameter
    period_match = re.search(r'timeperiod\s*=\s*(\d+)', full_match)
    period = period_match.group(1) if period_match else "14"

    return f"ta.{jesse_name}(self.candles, period={period})"


def varrd_to_jesse_entry(formula: str) -> str:
    """Convert VARRD formula to a scalar bool expression for should_long()/should_short().

    'df['rsi'] < 30' -> 'self.vars['rsi'] < 30'
    '&' -> 'and', '|' -> 'or'
    'df['close']' -> 'self.close'
    """
    code = formula

    # Map OHLCV columns first
    for col in ('close', 'open', 'high', 'low', 'volume'):
        code = re.sub(rf"df\['{col}'\]", f"self.{col}", code)
        code = re.sub(rf'df\["{col}"\]', f"self.{col}", code)

    # Map other df references to self.vars
    code = re.sub(r"df\['(\w+)'\]", r"self.vars['\1']", code)
    code = re.sub(r'df\["(\w+)"\]', r"self.vars['\1']", code)

    # Replace bitwise operators with logical (for scalar context)
    code = re.sub(r'\s*&\s*', ' and ', code)
    code = re.sub(r'\s*\|\s*', ' or ', code)

    # Remove wrapping parentheses from pandas-style conditions
    # e.g. (self.vars['rsi'] < 30) and (self.close > self.vars['sma'])
    # These are fine in Python, but clean up doubled parens
    code = re.sub(r'\(\((.+?)\)\)', r'(\1)', code)

    return code.strip()


def atr_to_jesse_sl(sl_atr: float) -> str:
    """Return ATR-based stop-loss price expression for go_long()/go_short()."""
    return f"ta.atr(self.candles, period=14) * {sl_atr}"


def atr_to_jesse_tp(tp_atr: float) -> str:
    """Return ATR-based take-profit price expression for go_long()/go_short()."""
    return f"ta.atr(self.candles, period=14) * {tp_atr}"
