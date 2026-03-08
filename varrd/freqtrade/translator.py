"""Shared translation utilities between VARRD and Freqtrade formats."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Market / timeframe mappings
# ---------------------------------------------------------------------------

_TF_MAP: dict[str, str] = {
    "daily": "1d",
    "60min": "1h",
    "15min": "15m",
    "5min": "5m",
    "weekly": "1w",
    "4h": "4h",
    "1h": "1h",
    "30min": "30m",
    # Already in Freqtrade format (from VARRD crypto markets)
    "1d": "1d",
    "1w": "1w",
    "15m": "15m",
    "5m": "5m",
    "30m": "30m",
}


def varrd_market_to_pair(market: str, stake_currency: str = "USDT") -> str:
    """Convert VARRD market string to Freqtrade pair.

    'BTC_daily'    -> 'BTC/USDT'
    'BTCUSDT_1d'   -> 'BTC/USDT'
    'ETH'          -> 'ETH/USDT'
    'SOLUSDT_4h'   -> 'SOL/USDT'
    """
    base = market.split("_")[0].upper()

    # Strip quote currency suffix (BTCUSDT -> BTC, ETHUSDT -> ETH)
    for suffix in ("USDT", "USD", "BUSD", "USDC"):
        if base.endswith(suffix) and len(base) > len(suffix):
            base = base[: -len(suffix)]
            break

    return f"{base}/{stake_currency}"


def varrd_timeframe_to_freqtrade(market: str) -> str:
    """Extract timeframe from VARRD market string and convert.

    'BTC_daily' -> '1d'
    'ES_60min'  -> '1h'
    'ETH'       -> '1d'  (default)
    """
    parts = market.split("_")
    if len(parts) >= 2:
        tf = parts[-1].lower()
        return _TF_MAP.get(tf, "1d")
    return "1d"


# ---------------------------------------------------------------------------
# Code translation (VARRD -> Freqtrade)
# ---------------------------------------------------------------------------

def varrd_to_freqtrade_code(setup_code: str) -> str:
    """Convert VARRD setup_code to Freqtrade populate_indicators body.

    Main transforms:
    - df -> dataframe
    - Remove load_data / query_data calls (Freqtrade provides its own data)
    """
    code = setup_code

    # Replace df with dataframe (whole-word only, not inside other words)
    code = re.sub(r'\bdf\b', 'dataframe', code)

    # Remove any load_data or query_data lines (Freqtrade loads data itself)
    code = re.sub(r'^.*(?:load_data|query_data).*$', '', code, flags=re.MULTILINE)

    # Remove blank lines that were left behind
    code = re.sub(r'\n{3,}', '\n\n', code)

    return code.strip()


def varrd_to_freqtrade_entry(formula: str, direction: str) -> str:
    """Convert VARRD formula to Freqtrade entry column assignment.

    Returns code that sets the appropriate enter_long or enter_short column.
    """
    translated = re.sub(r'\bdf\b', 'dataframe', formula)
    col = "enter_long" if direction.upper() == "LONG" else "enter_short"
    return f'dataframe.loc[{translated}, "{col}"] = 1'


def atr_sl_to_custom_stoploss(sl_atr: float) -> str:
    """Generate custom_stoploss() method body using ATR-based stop.

    Returns the method body (indented for class context).
    """
    return f"""\
    def custom_stoploss(self, pair: str, trade: Trade, current_time,
                        current_rate: float, current_profit: float,
                        after_fill: bool, **kwargs) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return self.stoploss
        last = dataframe.iloc[-1]
        if "atr" not in last or pd.isna(last["atr"]):
            return self.stoploss
        atr_val = last["atr"]
        sl_distance = atr_val * {sl_atr}
        sl_ratio = -(sl_distance / current_rate)
        return sl_ratio"""


def atr_tp_to_custom_exit(tp_atr: float, horizon: int) -> str:
    """Generate custom_exit() method body with ATR take-profit and time limit."""
    return f"""\
    def custom_exit(self, pair: str, trade: Trade, current_time,
                    current_rate: float, current_profit: float,
                    **kwargs) -> str | bool:
        # Time-based exit: close after {horizon} bars
        bars_held = (current_time - trade.open_date_utc).total_seconds()
        timeframe_seconds = timeframe_to_seconds(self.timeframe)
        if bars_held >= {horizon} * timeframe_seconds:
            return "time_limit_{horizon}_bars"

        # ATR take-profit
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return False
        last = dataframe.iloc[-1]
        if "atr" not in last or pd.isna(last["atr"]):
            return False
        atr_val = last["atr"]
        tp_distance = atr_val * {tp_atr}
        tp_ratio = tp_distance / trade.open_rate
        if current_profit >= tp_ratio:
            return "atr_take_profit"
        return False"""


def timeframe_to_seconds_code() -> str:
    """Return a helper function that converts Freqtrade timeframe strings to seconds."""
    return '''\
def timeframe_to_seconds(tf: str) -> int:
    """Convert Freqtrade timeframe string to seconds."""
    multipliers = {"m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = tf[-1]
    value = int(tf[:-1])
    return value * multipliers.get(unit, 86400)
'''
