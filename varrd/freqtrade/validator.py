"""Validate existing Freqtrade strategies using VARRD's statistical engine."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validating a Freqtrade strategy through VARRD."""

    strategy_name: str = ""
    pair: str = ""
    timeframe: str = ""
    indicators_found: list[str] = field(default_factory=list)
    entry_conditions: list[str] = field(default_factory=list)
    natural_language: str = ""

    # Populated after VARRD validation
    has_edge: bool | None = None
    edge_verdict: str = ""
    win_rate: float | None = None
    sharpe: float | None = None
    hypothesis_id: str = ""
    session_id: str = ""


def _extract_class_name(tree: ast.Module) -> str:
    """Find the IStrategy subclass name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name == "IStrategy":
                    return node.name
    return ""


def _extract_timeframe(tree: ast.Module) -> str:
    """Extract timeframe = '...' from the strategy class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "timeframe":
                    if isinstance(node.value, ast.Constant):
                        return str(node.value.value)
    return "1d"


def _extract_method_source(source: str, method_name: str) -> str:
    """Extract the source code of a method from the raw file text."""
    pattern = rf"(def {method_name}\(.*?\n(?:(?:        .+|[ \t]*)\n)*)"
    match = re.search(pattern, source)
    if match:
        return match.group(1).strip()
    return ""


def _conditions_to_natural_language(
    strategy_name: str,
    timeframe: str,
    indicators_body: str,
    entry_body: str,
) -> str:
    """Convert extracted code into a natural-language research prompt for VARRD."""
    parts = [f"I have a Freqtrade strategy called '{strategy_name}'."]
    parts.append(f"It runs on the {timeframe} timeframe.")

    if indicators_body:
        parts.append(f"It calculates these indicators:\n```python\n{indicators_body}\n```")

    if entry_body:
        parts.append(f"The entry conditions are:\n```python\n{entry_body}\n```")

    parts.append(
        "Can you validate whether this strategy has a real statistical edge? "
        "Please test the entry logic and tell me if the results are significant."
    )
    return "\n\n".join(parts)


def parse_strategy(strategy_path: str) -> ValidationResult:
    """Parse a Freqtrade strategy file and extract entry logic.

    This does NOT call VARRD — it just extracts the relevant code
    so you can inspect it or pass it to validate_strategy().
    """
    path = Path(strategy_path)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    class_name = _extract_class_name(tree)
    timeframe = _extract_timeframe(tree)

    indicators_body = _extract_method_source(source, "populate_indicators")
    entry_body = (
        _extract_method_source(source, "populate_entry_trend")
        or _extract_method_source(source, "populate_buy_trend")  # v2 compat
    )

    # Rough indicator detection
    indicator_names: list[str] = []
    indicator_patterns = [
        "RSI", "EMA", "SMA", "MACD", "BBANDS", "ATR", "ADX",
        "STOCH", "CCI", "MFI", "OBV", "WILLR", "ROC", "MOM",
    ]
    for name in indicator_patterns:
        if name.lower() in indicators_body.lower():
            indicator_names.append(name)

    conditions: list[str] = []
    # Extract dataframe.loc conditions
    for match in re.finditer(r'dataframe\.loc\[(.+?),', entry_body):
        conditions.append(match.group(1).strip())

    nl = _conditions_to_natural_language(class_name, timeframe, indicators_body, entry_body)

    return ValidationResult(
        strategy_name=class_name,
        pair="",
        timeframe=timeframe,
        indicators_found=indicator_names,
        entry_conditions=conditions,
        natural_language=nl,
    )


def validate_strategy(
    strategy_path: str,
    varrd_client=None,
) -> ValidationResult:
    """Parse a Freqtrade strategy and validate it through VARRD.

    Args:
        strategy_path: Path to a Freqtrade strategy .py file.
        varrd_client: Optional VARRD client instance. If None, creates one.

    Returns:
        ValidationResult with edge verdict and stats.
    """
    result = parse_strategy(strategy_path)

    if varrd_client is None:
        from varrd import VARRD
        varrd_client = VARRD()

    # Run the natural-language description through VARRD research
    r = varrd_client.research(result.natural_language)

    # Follow up until we get an edge verdict or exhaust next_actions
    max_turns = 10
    for _ in range(max_turns):
        ctx = r.context
        if ctx.has_edge is not None:
            break
        # Follow the first suggested next action
        if ctx.next_actions:
            action = ctx.next_actions[0]
            r = varrd_client.research(action, session_id=r.session_id)
        else:
            break

    result.session_id = r.session_id
    result.has_edge = r.context.has_edge
    result.edge_verdict = r.context.edge_verdict or ""
    result.hypothesis_id = ""  # Not always returned from research flow

    return result
